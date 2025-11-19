# SPDX-License-Identifier: Apache-2.0
# Copyright 2019 The Meson development team

from mesonbuild import mesonlib
from mesonbuild import mlog
from mesonbuild.mesonlib import MesonException, MachineChoice
from mesonbuild.modules import NewExtensionModule, ModuleInfo
from mesonbuild.interpreterbase.decorators import KwargInfo, FeatureNew, typed_kwargs
from mesonbuild.interpreter import Interpreter
from mesonbuild import build
from mesonbuild.programs import ExternalProgram

import typing as T

class JuliaModule(NewExtensionModule):

    INFO = ModuleInfo('julia', '1.1.0')

    def __init__(self, interpreter: Interpreter):
        super().__init__()
        self.interpreter = interpreter
        self.methods.update({
            'compile_library': self.compile_library,
        })

    @FeatureNew('julia.compile_library', '1.1.0')
    @typed_kwargs(
        'julia.compile_library',
        KwargInfo('name', str, required=True),
        KwargInfo('sources', (str, list), listify=True, required=True),
        KwargInfo('juliac', ExternalProgram, required=True),
    )
    def compile_library(self, state, args, kwargs):
        juliac = kwargs['juliac'].get_path()
        name = kwargs['name']
        sources = kwargs.pop('sources')

        kwargs['native'] = MachineChoice.HOST
        kwargs['name_prefix'] = ''
        kwargs['name_suffix'] = 'so' if not state.environment.machines[MachineChoice.HOST].is_windows() else 'dll'
        kwargs['sources'] = sources
        kwargs['objects'] = []
        kwargs['extra_files'] = []
        kwargs['c_args'] = []
        kwargs['cpp_args'] = []
        kwargs['c_link_args'] = []
        kwargs['cpp_link_args'] = []
        kwargs['cs_args'] = []
        kwargs['fortran_args'] = []
        kwargs['vala_args'] = []
        kwargs['rust_args'] = []
        kwargs['d_args'] = []
        kwargs['objc_args'] = []
        kwargs['objcpp_args'] = []
        kwargs['swift_args'] = []
        kwargs['java_args'] = []
        kwargs['cython_args'] = []
        kwargs['nasm_args'] = []
        kwargs['masm_args'] = []
        kwargs['link_args'] = []
        kwargs['cuda_args'] = []
        kwargs['linearasm_args'] = []
        kwargs['julia_args'] = []


        return self.interpreter.build_target(state.current_node, (name, sources), kwargs, build.SharedModule)


def initialize(interpreter: Interpreter) -> JuliaModule:
    return JuliaModule(interpreter)
