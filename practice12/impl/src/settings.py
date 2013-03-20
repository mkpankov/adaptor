"""
This module handles settings of system.

Platform-dependent, currently works on Unix only (uses '/proc' filesystem).

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

import os
import recordtype as rt

from data_types import *


SettingsBase = rt.recordtype('SettingsBase',
    'program_name framework_root_dir benchmark_root_dir benchmark_bin_dir '
    'build_settings run_settings')


class Settings(PrintableStructure, SettingsBase):
    def __init__(self,
                 program_name,
                 benchmark_root_dir='data/sources/polybench-c-3.2/',
                 benchmark_bin_dir='data/bin/'):
        """ Initialize framework settings and return Settings object.

        program_name is name of directory to be found in benchmark_root_dir.
        benchmark_root_dir is directory, containing all sources of given
            benchmark.
        benchmark_bin_dir is directory, where binaries will be put.
        """
        self.program_name = program_name
        self.framework_root_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), '..')
        self.benchmark_root_dir = os.path.realpath(
            os.path.join(self.framework_root_dir, benchmark_root_dir))
        self.benchmark_bin_dir = os.path.realpath(
            os.path.join(self.framework_root_dir, benchmark_bin_dir))
        self.define_build_settings('src', '')
        self.define_run_settings()

    def define_build_settings(self, sources_path, other_flags):
        self.build_settings = BuildSettings(
            benchmark_source_dir=os.path.join(
                self.benchmark_root_dir, '', sources_path),
            program_source="{0}.c".format(self.program_name),
            compiler=None,
            base_opt=None,
            optimization_flags=None,
            other_flags=other_flags,
            linker_options='-lm')

    def define_run_settings(self):
        self.run_settings = RunSettings()
