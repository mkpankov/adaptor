#!/usr/bin/env python

"""
Test the script for running single experiment.

Currently severely outdated.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

import unittest
import run_single_program as testee  # This is like a 'callee' to a 'caller'
import collections
import textwrap


class TestCommandsPreparation(unittest.TestCase):
    def setUp(self):
        Settings = collections.namedtuple('Settings',
            'compiler base_opt program_name '
            'benchmark_root_dir benchmark_source_dir')
        settings = Settings(compiler='gcc', base_opt='-O3',
            program_name='atax',
            benchmark_root_dir='../data/sources/polybench-c-3.2',
            benchmark_source_dir='linear-algebra/kernels/atax')
        self.local_settings = testee.create_local_settings(settings)

    def test_prepare_command_build_reference(self):
        command = testee.prepare_command_build_reference(self.local_settings)
        command_valid = textwrap.dedent("""\
            gcc -O0 -I utilities -I linear-algebra/kernels/atax
            utilities/polybench.c linear-algebra/kernels/atax/atax.c
            -DPOLYBENCH_DUMP_ARRAYS -o ./bin/atax_ref""").translate(None, '\n')
        self.assertEquals(command, command_valid)

    def test_prepare_command_run_reference(self):
        command = testee.prepare_command_run_reference(self.local_settings)
        command_valid = textwrap.dedent("""\
            ./bin/atax_ref 1>./output/atax_ref.out
            2>./output/atax_ref.err""").translate(None, '\n')
        self.assertEquals(command, command_valid)

    def test_prepare_command_build_timed(self):
        command = testee.prepare_command_build_timed(self.local_settings)
        command_valid = textwrap.dedent("""\
            gcc -O3 -I utilities -I linear-algebra/kernels/atax
            utilities/polybench.c linear-algebra/kernels/atax/atax.c
            -DPOLYBENCH_TIME -o ./bin/atax_time""").translate(None, '\n')
        self.assertEquals(command, command_valid)

    def test_prepare_command_run_timed(self):
        command = testee.prepare_command_run_timed(self.local_settings)
        command_valid = textwrap.dedent("""\
            ./bin/atax_time 1>./output/atax_time.out
            2>./output/atax_time.err""").translate(None, '\n')
        self.assertEquals(command, command_valid)


if __name__ == '__main__':
    unittest.main()
