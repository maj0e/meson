# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The Meson development team

from __future__ import annotations

import typing as T

from ..mesonlib import MachineChoice
from .compilers import Compiler

if T.TYPE_CHECKING:
    from ..envconfig import MachineInfo
    from ..options import MutableKeyedOptionDictType


class JuliaCompiler(Compiler):
    language = 'julia'
    id = 'julia'

    def __init__(self, exelist: T.List[str], version: str, for_machine: MachineChoice,
                 is_cross: bool, info: 'MachineInfo', full_version: T.Optional[str] = None):
        super().__init__([], exelist, version, for_machine, info, full_version=full_version, is_cross=is_cross)

    def get_output_args(self, outputname: str) -> T.List[str]:
        return ['--output-o', outputname]

    def get_optimization_args(self, optimization_level: str) -> T.List[str]:
        return []

    def sanity_check(self, work_dir: str, environment: 'Environment') -> None:
        pass

    def get_options(self) -> 'MutableKeyedOptionDictType':
        return {}

    def __init__(self, exelist: T.List[str], version: str, for_machine: MachineChoice,
                 is_cross: bool, info: 'MachineInfo', full_version: T.Optional[str] = None):
        super().__init__([], exelist, version, for_machine, info, full_version=full_version, is_cross=is_cross)
        from ..options import COMPILER_BASE_OPTIONS
        self.base_options = {o for o in COMPILER_BASE_OPTIONS}
