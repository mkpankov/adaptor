"""
This module handles settings of system.

Platform-dependent, currently works on Unix only (uses '/proc' filesystem).

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

from data_types import *


def define_build_settings(s, sources_path, other_flags):
    s.build_settings = BuildSettings(
        benchmark_source_dir=os.path.join(
            s.benchmark_root_dir, '', sources_path),
        program_source="{0}.c".format(s.program_name),
        compiler=None,
        base_opt=None,
        optimization_flags=None,
        other_flags=other_flags,
        linker_options='-lm')


def define_run_settings(s):
    s.run_settings = RunSettings()
