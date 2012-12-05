#!/usr/bin/env python

"""Run experiment with specified program with given compilers."""

import os
import subprocess as sp
import textwrap as tw
import collections as cl


def build_reference(settings):
    """Build the reference version of the benchmark."""
    local_settings = create_local_settings(settings)
    command = tw.dedent("""
        {compiler} -O0 -I utilities -I {benchmark_source_dir} 
        utilities/polybench.c {benchmark_source_dir} 
        -DPOLYBENCH_DUMP_ARRAYS 
        -o ./bin/{program_name}_ref""").translate(None, '\n').format(
        **local_settings)
    os.chdir(local_settings['benchmark_root_dir'])
    print os.path.realpath(os.path.curdir)
    print command
    raw_input()
    reference_command_build = tw.dedent("""\
        gcc -O0 -I utilities -I linear-algebra/kernels/atax 
        utilities/polybench.c linear-algebra/kernels/atax/atax.c 
        -DPOLYBENCH_DUMP_ARRAYS -o ./bin/atax_ref""").translate(None, '\n')
    assert command == reference_command_build
    sp.call('mkdir bin'.split())
    sp.check_call(command.split())


def run_reference(settings):
    reference_command_run = './atax_ref 2>atax_ref.out'


def prepare_command(settings):
    command = tw.dedent("""
        {compiler} {base_opt} -I utilities 
        -I {benchmark_source_dir} utilities/polybench.c 
        {benchmark_source_dir}/{program_source} -DPOLYBENCH_TIME 
        -o ./bin/{program_name}_time""").translate(None, '\n').format(
        **local_settings)
    return command


def create_local_settings(settings):
    """Create local settings from global."""
    local_settings = dict()
    local_settings['program_source'] = '{program_name}.c'.format(
        **{'program_name': settings.program_name})
    local_settings.update(settings._asdict())
    return local_settings


def build_timed(settings):
    """Build the timed version of the benchmark."""
    local_settings = create_local_settings(settings)
    command = prepare_command(local_settings)
    os.chdir(local_settings['benchmark_root_dir'])
    print os.path.realpath(os.path.curdir)
    print command
    raw_input()
    reference_command_build == tw.dedent("""\
        gcc -O3 -I utilities -I linear-algebra/kernels/atax 
        utilities/polybench.c linear-algebra/kernels/atax/atax.c 
        -DPOLYBENCH_TIME -o ./bin/atax_time""").translate(None, '\n')
    assert command == reference_command_build
    sp.call('mkdir bin'.split())
    sp.check_call(command.split())


def main():
    """Invokes all necessary builds and experiments."""
    Settings = cl.namedtuple('Settings', 
        'compiler base_opt program_name '
        'benchmark_root_dir benchmark_source_dir')
    settings = Settings(compiler='gcc', base_opt='-O3', 
        program_name='atax', 
        benchmark_root_dir='../data/sources/polybench-c-3.2',
        benchmark_source_dir='linear-algebra/kernels/atax')

    build_reference(settings)
    build_timed(settings)


if __name__ == '__main__':
    main()
