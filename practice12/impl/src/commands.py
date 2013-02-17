"""
This module handles mid-level commands of framework.

They are used internally mainly.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

import os
import subprocess as sp
import probe
import timeit
import sys
import copy
import textwrap as tw
import numpy as np

from data_types import *
from database import *

import ipdb

# This template is for use in timing.
definition = \
"""
from subprocess import Popen, PIPE
def run():
    p = Popen("{command}".split(), 
              stdout=PIPE, 
              stderr=PIPE)
    return p.communicate()
"""


def prepare_command_build(settings):
    """Prepare command for building of generic program."""

    full_path_source = os.path.join(
        "{build_settings.benchmark_source_dir}".format(**settings._asdict()),
        "{build_settings.program_source}".format(**settings._asdict()))
    full_path_binary = os.path.join(
        "{benchmark_bin_dir}".format(**settings._asdict()),
        "{program_name}".format(**settings._asdict()))

    ipdb.set_trace()

    command = tw.dedent("""
        {build_settings.compiler} {build_settings.base_opt} 
        {build_settings.other_flags} {0} 
        -o {1} {build_settings.linker_options}""").translate(None, '\n').format(
        full_path_source, full_path_binary, **settings._asdict())
    return command


def build(context):
    """Build the generic version of the program."""

    command = prepare_command_build(context.settings)
    context.paths_manager.nest_path_from_benchmark_root('')
    print os.path.realpath(os.path.curdir)
    print command
    context.paths_manager.nest_path_from_benchmark_root('')
    sp.call('mkdir bin'.split())
    context.paths_manager.unnest_path()
    sp.check_call(command.split())
    context.paths_manager.unnest_path()


def prepare_command_run(settings):
    """Prepare command for running the program."""

    command = tw.dedent("""
        ./{program_name}""").translate(None, '\n').format(
        **settings._asdict())
    return command


def run(context):
    """Run the generic version of program."""
    
    command = prepare_command_run(context.settings)
    context.paths_manager.nest_path_from_root(context, 'data/bin')
    print command
    r = calibrate(context, command)
    context.paths_manager.unnest_path(context)
    return r


def run_empty(context):
    """Run the generic version of program."""
    
    command = prepare_command_run(context.settings)
    context.paths_manager.nest_path_from_root(context, 'data/bin')
    print command
    r = calibrate_empty(context, command)
    context.paths_manager.unnest_path(context)
    return r


def gather_cpu_info():
    """Gather information about CPU and return structure."""
    p = probe.CPUProbe()
    cpu_info = CPUInfo(cpu_mhz=p.cpu_mhz(),
                       cache_size=p.cache_size(),
                       flags=p.flags())
    return cpu_info


def gather_hardware_info():
    """Gather hardware information and return structure."""
    cpu_info = gather_cpu_info()
    i = HardwareInfo(cpu_info=cpu_info)
    return i


def perform_experiment(context):
    """Perform experiment."""

    find_program(context)
    ipdb.set_trace()
    build(context)
    _, o_t = calculate_overhead_time(context)
    c, v = validate(context, None, o_t)
    hardware_info = gather_hardware_info()

    experiment = create_experiment_document(context, c, v, hardware_info)
    print "Saving experiment now"
    experiment.save()
    return experiment


def find_program(context):
    """Find the program source by name."""

    program = context.settings.program_name

    for path, filenames, dirnames in os.walk(
        context.paths_manager.benchmark_root_dir):
        if os.path.basename(path) == program:
            program_path = path
            break

    context.settings.build_settings.benchmark_source_dir = program_path


def validate_default(context):
    """
    Perform validation on set of time-measurement programs and report errors.
    """

    context.paths_manager.nest_path_absolute(context, context.settings.framework_root_dir)
    vs = []
    cs = []
    c, overhead_time = calculate_overhead_time(context)

    for i in range(7):
        real_time_us = 10**i
        s = 'usleep_{0}'.format(real_time_us)
        context.settings.program_name = s
        context.settings.define_build_settings(context.settings,
            '',
            '')
        context.settings.build_settings.compiler = 'gcc'
        context.settings.build_settings.base_opt = '-O0'
        build(context)
        c, v = validate(context, real_time_us / 10.**6, overhead_time)
        cs.append(c)
        vs.append(v)
    context.paths_manager.unnest_path(context)
    return cs, vs


def validate(context, real_time, overhead_time):
    """
    Validate calibration of single command.
    """
    c = run(context)

    measured_time = c.time - overhead_time
    try:
        error = abs(measured_time - real_time)
        relative_error = error / real_time
    except:
        error = None
        relative_error = None

    v = ValidationResult(real_time, measured_time, error, relative_error)
    return c, v


def calibrate_empty(context, command):
    """Calibrate execution of command until measurement is accurate enough."""
    n = 0
    t = 0
    d_rel = 1
    print "Begin"
    command = os.path.join(context.paths_manager.get_path(), command)
    result = timeit.timeit(stmt='run()',
                           setup=definition.format(
                               command=command),
                           number=1)
    print "\nTime of single run:", result,
    if result > 1:
        # When incremented in the loop, it'll become zero
        n = -1
        print ", pruning"
    else:
        print ''

    while (t < 1) and (d_rel > 0.02):
        sys.stderr.write('.')
        n += 1
        number = 10**(n)
        result = timeit.repeat(stmt='run()', 
                               setup=definition.format(
                                   command=command), 
                               number=number,
                               repeat=3)
        t = min(result)
        d = np.std(np.array(result))
        d_rel = d / t
    sys.stderr.write('\n')
    return CalibrationResult(t, t / number, d, d_rel, number, result)


def calibrate(context, command):
    """Calibrate execution of command until measurement is accurate enough."""
    n = 0
    t = 0
    d_rel = 1
    print "Begin"
    command = os.path.join(context.paths_manager.get_path(), command)
    result = timeit.timeit(stmt='run()',
                           setup=definition.format(
                               command=command),
                           number=1)
    print "\nTime of single run:", result,
    if result > 1:
        # When incremented in the loop, it'll become zero
        n = -1
        print ", pruning"
    else:
        print ''

    while (t < 1) and (d_rel > 0.05):
        sys.stderr.write('.')
        n += 1
        number = 10**(n)
        result = timeit.repeat(stmt='run()', 
                               setup=definition.format(
                                   command=command), 
                               number=number,
                               repeat=3)
        t = min(result)
        d = np.std(np.array(result))
        d_rel = d / t
    sys.stderr.write('\n')
    return CalibrationResult(t, t / number, d, d_rel, number, result)


def calculate_overhead_time(context):
    context = copy.deepcopy(context)
    settings = context.settings
    context.paths_manager.nest_path_from_root(context, 'data/sources/time-test')
    saved_name = settings.program_name 
    settings.program_name = 'do_nothing'
    saved_path = settings.benchmark_root_dir
    settings.benchmark_root_dir = context.paths_manager.get_path()

    settings.define_build_settings('', '')
    b = settings.build_settings
    b.compiler = 'gcc'
    b.base_opt = '-O0'

    settings.define_run_settings()

    build(context)
    c = run_empty(context)
    overhead_time = c.time

    context.paths_manager.unnest_path(context)
    settings.benchmark_root_dir = saved_path
    settings.program_name = saved_name
    return c, overhead_time
