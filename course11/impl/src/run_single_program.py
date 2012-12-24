#!/usr/bin/env python

"""
Part of 'Adaptor' framework.

Author: Michael Pankov, 2012.

Run experiment with specified program with given compilers.
"""

import sys
import os

import subprocess as sp
import textwrap as tw
import timeit
import datetime as dt

import recordtype as rt
import collections as cl

import numpy as np

import couchdbkit as ck
from couchdbkit.designer import push

import ipdb


class PrintableStructure():
    """A class to allow easy pretty printing of namedtuple and recordtype."""
    def __str__(self):
        c = self.__class__
        s = tw.dedent("""
        {name}:
        """).format(name=c.__name__)
        for k, v in self._asdict().items():
            s += '\t{field:20}:\t{value}\n'.format(field=k, value=v)

        return s


Context = rt.recordtype('Context',
    'paths_stack settings')

SettingsBase = rt.recordtype('Settings', 
    'program_name benchmark_root_dir framework_root_dir '
    'build_settings run_settings benchmark_bin_dir')

class Settings(PrintableStructure, SettingsBase):
    pass


BuildSettingsBase = rt.recordtype('BuildSettings',
    'compiler base_opt optimization_flags other_flags '
    'benchmark_source_dir program_source')

class BuildSettings(PrintableStructure, BuildSettingsBase):
    pass


RunSettingsBase = rt.recordtype('RunSettings',
    '')

class RunSettings(PrintableStructure, RunSettingsBase):
    pass


Input = cl.namedtuple('Input',
    'benchmark_source_dir compiler base_opt')


CalibrationResultBase = cl.namedtuple('CalibrationResult',
    'total_time time dispersion variance runs_number times_list')

class CalibrationResult(PrintableStructure, CalibrationResultBase):
    pass


ValidationResultBase = cl.namedtuple('ValidationResult',
    'real_time measured_time error relative_error')

class ValidationResult(PrintableStructure, ValidationResultBase):
    pass


# The documents below sometimes correspond to plain records used
# to aggregate data during the work of framework 
# (which are defined above).
# However, they only save the information relevant to experiment
# reproduction and meaningful to analytics.

class CalibrationResultDocument(ck.Document):
    """CouchDB document, describing the result of multiple measurements."""
    total_time = ck.FloatProperty()
    time = ck.FloatProperty()
    dispersion = ck.FloatProperty()
    variance = ck.FloatProperty()
    runs_number = ck.IntegerProperty()
    times_list = ck.ListProperty()


class ValidationResultDocument(ck.Document):
    """CouchDB document, describing the result of calibrations."""
    real_time = ck.FloatProperty()
    measured_time = ck.FloatProperty()
    error = ck.FloatProperty()
    relative_error = ck.FloatProperty()


class BuildSettingsDocument(ck.Document):
    """
    CouchDB document, describing the settings with which 
    the program was built.
    """
    compiler = ck.StringProperty()
    base_opt = ck.StringProperty()
    optimization_flags = ck.StringProperty()
    other_flags = ck.StringProperty()


class RunSettingsDocument(ck.Document):
    """
    CouchDB document, describing the settings with which 
    the program was run.
    """
    pass


class SettingsDocument(ck.Document):
    """CouchDB document, describing the global settings of framework."""
    program = ck.StringProperty()
    build_settings = ck.SchemaProperty(BuildSettingsDocument)
    run_settings = ck.SchemaProperty(RunSettingsDocument)


class ExperimentDocument(ck.Document):
    """CouchDB document, describing the experiment."""
    datetime = ck.DateTimeProperty()
    calibration_result = ck.SchemaProperty(CalibrationResultDocument)
    validation_result = ck.SchemaProperty(ValidationResultDocument)
    settings = ck.SchemaProperty(SettingsDocument)


class NonAbsolutePathError(RuntimeError):
    pass

class NoSuchNestedPathError(RuntimeError):
    pass


definition = \
"""
from subprocess import Popen, PIPE
def run():
    p = Popen("{command}".split(), 
              stdout=PIPE, 
              stderr=PIPE)
    return p.communicate()
"""


def main():
    """Invoke all necessary builds and experiments."""

    settings = Settings(program_name='atax', 
        framework_root_dir=os.path.realpath(
            os.path.join(os.path.dirname(__file__), '..')),
        benchmark_root_dir=None,
        benchmark_bin_dir=None,
        build_settings=None,
        run_settings=None)
    context = Context(paths_stack=[],
        settings=settings)
    settings.benchmark_root_dir = os.path.realpath(os.path.join(
        settings.framework_root_dir, 'data/sources/polybench-c-3.2/'))
    settings.benchmark_bin_dir = os.path.realpath(os.path.join(
        settings.framework_root_dir, 'data/bin/'))
    print settings

    define_build_settings(settings, 
        'linear-algebra/kernels/atax/',
        '-I utilities -I linear-algebra/kernels/atax utilities/polybench.c')
    b = settings.build_settings
    b.compiler = 'gcc'
    b.base_opt = '-O2'
    print settings.build_settings

    define_run_settings(settings)
    print settings.run_settings

    nest_path_absolute(context, settings.framework_root_dir)

    server, db = setup_database(settings, context)

    perform_experiment(context)

    # cs, vs = validate_default(context)
    # for c, v in zip(cs, vs):
    #     create_experiment(c, v)
    #     store_experiment(e)

    unnest_path(context)
    assert len(context.paths_stack) == 0


def define_build_settings(s, sources_path, other_flags):
    s.build_settings = BuildSettings(
        benchmark_source_dir=os.path.join(
            s.benchmark_root_dir, '', sources_path),
        program_source="{0}.c".format(s.program_name),
        compiler=None,
        base_opt=None,
        optimization_flags=None,
        other_flags=other_flags)


def define_run_settings(s):
    s.run_settings = RunSettings()


def store_validation_document(v):
    v_doc = make_validation_document(v)
    v_doc.save()


def make_validation_document(v):
    v_doc = ValidationResultDocument(
        real_time=float(v.real_time),
        measured_time=float(v.measured_time),
        error=float(v.error),
        relative_error=float(v.relative_error))
    return v_doc


def push_path(context, path):
    """
    Push path to stack in context.

    Path must be absolute.
    """
    if os.path.isabs(path):
        context.paths_stack.append(path)
    else:
        raise NonAbsolutePathError


def pop_path(context):
    """
    Pop path from stack in context.

    Path is absolute.
    """
    return context.paths_stack.pop()


def get_path(context):
    """
    Return the path on top of stack in context.
    """
    return context.paths_stack[-1]


def ensure_path(context):
    """
    Get the correct current path from stack in context and 
    change current directory to there.
    """
    os.chdir(get_path(context))


def nest_path_absolute(context, path):
    """
    Receive path, push the real path of it to stack in context and 
    change current directory to there.
    """
    try:
        os.chdir(path)
    except:
        raise NoSuchNestedPathError

    push_path(context, path)
    ensure_path(context)


def nest_path_from_root(context, path):
    """
    Receive path, relative to the root of framework, 
    push it to stack in context and change current directory to there.
    """
    new_path = os.path.join(context.settings.framework_root_dir, path)
    nest_path_absolute(context, new_path)


def nest_path_from_benchmark_root(context, path):
    """
    Receive path, relative to the root of benchmark directory, 
    push it to stack in context and change current directory to there.
    """
    new_path = os.path.join(context.settings.benchmark_root_dir, path)
    nest_path_absolute(context, new_path)


def nest_path(context, path):
    """
    Receive relative path, push the real path of it to stack in context and 
    change current directory to there.
    """
    new_path = os.path.join(get_path(context), path)
    nest_path_absolute(context, new_path)


def unnest_path(context):
    """
    Pop the path from stack in context and
    change current directory to current top path of stack.
    """
    pop_path(context)
    try:
        ensure_path(context)
    except:
        # Fails when stack is empty after popping
        pass


def validate(context):
    """
    Perform a calibrated measurement of execution time and 
    calculate the error.
    """
    nest_path_from_root(context, 'data/bin/')

    real_time_us = 0
    overhead_time = validate_command('do_nothing', real_time_us, 0)

    real_time_us = 500000
    validate_command('atax_base', real_time_us, overhead_time)
    unnest_path(context)


def validate_default(context):
    """
    Perform validation on set of time-measurement programs and report errors.
    """
    nest_path_from_root(context, 'data/bin/')
    vs = []
    cs = []
    c, v = validate_command(context, 'do_nothing', 0, 0)
    cs.append(c)
    vs.append(v)
    overhead_time = v.real_time

    assert False
    for i in range(7):
        real_time_us = 10**i
        s = 'usleep_{0}'.format(real_time_us)
        c, v = validate_command(context, s, real_time_us / 10**6, overhead_time)
        cs.append(c)
        vs.append(v)
    unnest_path(context)
    return cs, vs


def validate_command(context, command, real_time, overhead_time):
    """
    Validate calibration of single command.
    """
    c = calibrate(context, command)
    measured_time = c.time - overhead_time
    error = abs(measured_time - real_time)
    relative_error = error / measured_time
    v = ValidationResult(real_time, measured_time, error, relative_error)
    return c, v


def calibrate(context, command):
    """Calibrate execution of command until measurement is accurate enough."""
    n = 0
    t = 0
    d_rel = 1
    print "Begin"
    while (t < 1) and (d_rel > 0.05):
        sys.stderr.write('.')
        n += 1
        number = 10**(n)
        command = os.path.join(get_path(context), command)
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


def convert_input_to_settings(input):
    """Process user input (command line arguments) and return settings."""
    
    program_name, benchmark_root_dir = \
        os.path.split(os.path.realpath(Input[benchmark_source_dir]))
    framework_root_dir, _ = os.path.split(os.path.realpath(__file__))

    settings = Settings(program_name=program_name,
        benchmark_root_dir=benchmark_root_dir,
        framework_root_dir=framework_root_dir)

    build_settings = BuildSettings(compiler=Input[compiler],
        base_opt=Input[base_opt],
        benchmark_source_dir=Input[benchmark_source_dir])

    benchmark_bin_dir = os.path.join(framework_root_dir, 'data/bin/')
    run_settings = RunSettings(benchmark_bin_dir=benchmark_bin_dir)
    
    return settings, build_settings, run_settings


def perform_experiment(context):
    """Perform experiment."""

    build(context)
    c = run(context)

    c_d = CalibrationResultDocument(
        total_time=c.total_time,
        time=c.time,
        dispersion=c.dispersion,
        variance=c.variance,
        runs_number=c.runs_number,
        times_list=c.times_list)

    b = context.settings.build_settings

    b_d = BuildSettingsDocument(
        compiler=b.compiler,
        base_opt=b.base_opt,
        optimization_flags=b.optimization_flags,
        other_flags=b.other_flags)

    r_d = RunSettingsDocument()

    s_d = SettingsDocument(
        program=context.settings.program_name,
        build_settings=b_d,
        run_settings=r_d)

    experiment = ExperimentDocument(
        settings=s_d,
        calibration_result=c_d,
        validation_result=None,
        datetime=dt.datetime.utcnow())
    experiment.save()


def print_experiments(db):
    """Print all the experiments."""

    experiments = db.view('experiment/all')
    for e in experiments.all():
        print 'Experiment:'
        print 'Build:', e['value']['command_build']
        print 'Run:', e['value']['command_run']
        print 'Date & time:', e['value']['datetime']


def setup_database(settings, context):
    """Setup the database."""

    server = ck.Server()
    db = server.get_or_create_db('adaptor')

    ExperimentDocument.set_db(db)
    SettingsDocument.set_db(db)
    BuildSettingsDocument.set_db(db)
    RunSettingsDocument.set_db(db)
    CalibrationResultDocument.set_db(db)
    ValidationResultDocument.set_db(db)

    nest_path_from_root(context, 'couch/adaptor')
    # We are stupid so we suppose the CouchApp is managed
    # to be stable version and we just re-publish it on launch.
    sp.check_call('couchapp push . http://localhost:5984/adaptor'.split())
    unnest_path(context)

    return server, db


def prepare_command_build(settings):
    """Prepare command for building of generic program."""

    full_path_source = os.path.join(
        "{build_settings.benchmark_source_dir}".format(**settings._asdict()),
        "{build_settings.program_source}".format(**settings._asdict()))
    full_path_binary = os.path.join(
        "{benchmark_bin_dir}".format(**settings._asdict()),
        "{program_name}".format(**settings._asdict()))
    command = tw.dedent("""
        {build_settings.compiler} {build_settings.base_opt} 
        {build_settings.other_flags} {0} 
        -o {1}""").translate(None, '\n').format(
        full_path_source, full_path_binary, **settings._asdict())
    return command


def build(context):
    """Build the generic version of the program."""

    command = prepare_command_build(context.settings)
    nest_path_from_benchmark_root(context, '')
    print os.path.realpath(os.path.curdir)
    print command
    nest_path_from_benchmark_root(context, '')
    sp.call('mkdir bin'.split())
    unnest_path(context)
    sp.check_call(command.split())
    unnest_path(context)


def prepare_command_run(settings):
    """Prepare command for running the program."""

    command = tw.dedent("""
        ./{program_name}""").translate(None, '\n').format(
        **settings._asdict())
    return command


def run(context):
    """Run the generic version of program."""
    
    command = prepare_command_run(context.settings)
    nest_path_from_root(context, 'data/bin')
    r = calibrate(context, command)
    unnest_path(context)
    return r


if __name__ == '__main__':
    main()
