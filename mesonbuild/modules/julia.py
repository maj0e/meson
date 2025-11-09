# Start of file
from __future__ import annotations

import typing as T
import os

from .. import mesonlib
from . import ExtensionModule, ModuleInfo
from ..interpreterbase import noPosargs, noKwargs, permittedKwargs, typed_pos_args, typed_kwargs
from ..build import CustomTarget, SharedModule, BuildTarget, CustomTargetIndex, GeneratedList, StructuredSources
from ..interpreter.type_checking import BuildTargetSource
from ..programs import ExternalProgram
from ..mesonlib import MachineChoice

if T.TYPE_CHECKING:
    from . import ModuleState

INFO = ModuleInfo('julia', '0.1.0')

class JuliaModule(ExtensionModule):
    INFO = INFO

    def __init__(self, interpreter):
        super().__init__(interpreter)
        self.methods.update({
            'find_juliac': self.find_juliac,
            'compile_library': self.compile_library,
        })

    @noPosargs
    @noKwargs
    def find_juliac(self, state, args, kwargs):
        """
        Return an ExternalProgram pointing to the juliac tool. Preference:
        - project-provided entry in environment (lookup_binary_entry)
        - juliac from PATH
        """
        cmd = state.environment.lookup_binary_entry(MachineChoice.HOST, 'juliac')
        if cmd is not None:
            prog = ExternalProgram.from_entry('juliac', cmd)
        else:
            prog = ExternalProgram('juliac', silent=True)
        return prog

    @permittedKwargs(set())
    @typed_pos_args('julia.compile_library', str, (str, mesonlib.File))
    @typed_kwargs('julia.compile_library',
                  'kind',       # 'static' or 'shared'
                  'juliac',     # an ExternalProgram or None
                  'juliac_args' # array of extra args for juliac
                  )
    def compile_library(self, state: 'ModuleState', args: T.Tuple[str, BuildTargetSource], kwargs: T.Dict[str, T.Any]):
        """
        compile_library(name, source, kind: 'static'|'shared', juliac: ExternalProgram, juliac_args: [])
        Produces a CustomTarget that builds the library via juliac.
        Returns the CustomTarget so it can be passed to link_with.
        """
        name, source = args
        kind = kwargs.get('kind', 'static')
        juliac_prog = kwargs.get('juliac', None)
        juliac_args = kwargs.get('juliac_args', [])

        # Resolve juliac program if not given
        if juliac_prog is None:
            juliac_prog = self.find_juliac(state, (), {})
            # If juliac not found, raise helpful error
            if not isinstance(juliac_prog, ExternalProgram) or not juliac_prog.found():
                raise mesonlib.MesonException('juliac (JuliaC) not found. Either install JuliaC or pass juliac: find_program("juliac") to compile_library().')

        # Determine output filename depending on kind and platform
        host_system = state.environment.machines.host.system
        if kind == 'static':
            if host_system == 'windows':
                filename = f'{name}.lib'
            else:
                filename = f'lib{name}.a'
        elif kind == 'shared':
            if host_system == 'windows':
                filename = f'{name}.dll'
            elif host_system == 'darwin':
                filename = f'lib{name}.dylib'
            else:
                filename = f'lib{name}.so'
        else:
            raise mesonlib.MesonException("Invalid kind for julia.compile_library: must be 'static' or 'shared'")

        # Build the CustomTarget args/kwargs for invoking juliac
        # Use '@OUTPUT@' and '@INPUT@' substitution tokens used by CustomTarget.
        juliac_exe = juliac_prog.get_path() if hasattr(juliac_prog, 'get_path') else juliac_prog.name
        cmd = [juliac_exe, '-o', '@OUTPUT@', '@INPUT@'] + list(juliac_args)

        ct_kwargs: T.Dict[str, T.Any] = {}
        ct_kwargs['output'] = [filename]
        ct_kwargs['input'] = [source]
        ct_kwargs['command'] = cmd
        ct_kwargs['capture'] = False
        # Forward install kwarg if user provided it
        if 'install' in kwargs:
            ct_kwargs['install'] = kwargs['install']
        # Forward a few other CustomTarget keys if present
        for k in ('depfile', 'build_always', 'build_by_default', 'install_dir'):
            if k in kwargs:
                ct_kwargs[k] = kwargs[k]

        # Build the CustomTarget
        ct_args = (name, [source])
        res = self.interpreter.build_target(state.current_node, ct_args, ct_kwargs, CustomTarget)
        return res

    def initialize(*args, **kwargs):
        return JuliaModule(*args, **kwargs)
# End of file
