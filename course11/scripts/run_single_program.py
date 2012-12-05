#!/usr/bin/env python

"""Run experiment with specified program with given compilers"""

import os
import subprocess as sp
import textwrap as tw

def main():
    compiler = 'gcc'
    base_opt = '-O3'
    program_name = 'atax'
    program_source = '{program_name}.c'.format(**{'program_name': program_name})
    benchmark_root_dir = '../data/sources/polybench-c-3.2'
    benchmark_source_dir = 'linear-algebra/kernels/atax'
    command = tw.dedent("""
        {compiler} {base_opt} -I utilities 
        -I {benchmark_source_dir} utilities/polybench.c 
        {benchmark_source_dir}/{program_source} -DPOLYBENCH_TIME 
        -o ./bin/{program_name}_time""").translate(None, '\n').format(**locals())
    os.chdir(benchmark_root_dir)
    print os.path.realpath('.')
    print command
    raw_input()
    assert command == tw.dedent("""\
        gcc -O3 -I utilities -I linear-algebra/kernels/atax 
        utilities/polybench.c linear-algebra/kernels/atax/atax.c 
        -DPOLYBENCH_TIME -o ./bin/atax_time""").translate(None, '\n')
    sp.call('mkdir bin'.split())
    sp.call(command.split())

if __name__ == '__main__':
    main()
