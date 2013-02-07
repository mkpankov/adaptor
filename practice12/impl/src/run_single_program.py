#!/usr/bin/env python
# coding: utf-8

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
import matplotlib.pyplot as plt

import couchdbkit as ck
from couchdbkit.designer import push

import copy

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
    'benchmark_source_dir program_source linker_options')

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

    settings = Settings(program_name=None, 
        framework_root_dir=os.path.realpath(
            os.path.join(os.path.dirname(__file__), '..')),
        benchmark_root_dir=None,
        benchmark_bin_dir=None,
        build_settings=None,
        run_settings=None)
    context = Context(paths_stack=[],
        settings=settings)
    settings.benchmark_bin_dir = os.path.realpath(os.path.join(
        settings.framework_root_dir, 'data/bin/'))

    server, db = setup_database(settings, context)

    settings.benchmark_root_dir = os.path.realpath(os.path.join(
        settings.framework_root_dir, 'data/sources/time-test/'))

    plot_error(context)
    # plot_vs()
    # for c, v in zip(cs, vs):       
    #     e = create_experiment_document(context, c, v)
    #     e.save()

    settings.benchmark_root_dir = os.path.realpath(os.path.join(
        settings.framework_root_dir, 'data/sources/polybench-c-3.2/'))
    nest_path_from_benchmark_root(context, '.')

    es = []
    n = 0
    for path, dirs, files in os.walk('.'):
        if files and not path.endswith('utilities') and not path == '.':
            n += 1
            settings.program_name = os.path.basename(path)
            context.settings = settings

            define_build_settings(settings, 
                path,
                '-I utilities -I {0} utilities/polybench.c'.format(path))
            b = settings.build_settings
            b.compiler = 'gcc'
            b.base_opt = '-O2'
    
            define_run_settings(settings)

            nest_path_absolute(context, settings.framework_root_dir)

            e = perform_experiment(context)
            es.append(e)

            unnest_path(context)

    y = map(lambda e: e.calibration_result.time, es)
    yerr = map(lambda e: e.calibration_result.dispersion, es)
    x = range(len(y))
    plt.figure()
    plt.scatter(x, y)
    plt.errorbar(x, y, yerr=yerr, fmt=None)
    plt.show()

    unnest_path(context)
    assert len(context.paths_stack) == 0


def plot_error(context):
    nest_path_from_benchmark_root(context, '.')
    settings = context.settings
    settings.program_name = 'do_nothing'
    define_build_settings(settings,
        '',
        '')
    b = settings.build_settings
    b.compiler = 'gcc'
    b.base_opt = '-O0'
    define_run_settings(settings)
    cs, vs = validate_default(context)
    y1 = map(lambda v: v.real_time, vs)
    y2 = map(lambda v: v.measured_time, vs)
    err = map(lambda v: v.relative_error, vs)
    for p1, p2, e in zip(y1, y2, err):
        print tw.dedent(
            """\
            Experiment performed:
                Real time: {0:.6f}
                Measured time: {1:.6f}
                Relative error: {2:.2f}
            """.format(p1, p2, e))
    raw_input()
    x = range(len(y1))
    plt.figure()
    plt.axes().set_yscale('log')
    plt2 = plt.scatter(x, y2, marker='+', s=160, c='r', label=u'измеренное время')
    plt1 = plt.scatter(x, y1, label=u'реальное время')
    plt.axes().set_xticks(range(len(y1)))
    default_xticklabels = ['usleep_{0}'.format(10**i) for i in range(7)]
    plt.axes().set_xticklabels(default_xticklabels)
    plt.setp(plt.axes().get_xticklabels(), rotation=90)
    plt.axes().set_xlabel(u'программа')
    plt.axes().set_ylabel(u'время выполнения, с')
    plt.axes().grid(axis='both')
    p1 = plt.Rectangle((0, 0), 1, 1, fc='b')
    p2 = plt.Rectangle((0, 0), 1, 1, fc='r')
    plt.axes().legend((p1, p2), (plt1.get_label(), plt2.get_label()), loc='best')
    plt.title(u'Математическое ожидание времени исполнения калибровочных программ и реальное время их исполнения')
    plt.show()
    unnest_path(context)

def plot_vs():
    v = ExperimentDocument.view('adaptor/experiment-all')
    l = []
    for doc in v:
        if doc.datetime > dt.datetime(2012,12,30,22,01,00):
            l.append((doc.settings.build_settings.compiler, 
                      doc.settings.program, 
                      doc.calibration_result.time))
    clang_es = filter(lambda e: e[0] == u'gcc', l)
    gcc_es = filter(lambda e: e[0] == u'gcc', l)
    clang_x_ticklabels = map(lambda e: e[1], clang_es)
    gcc_x_ticklabels = map(lambda e: e[1], gcc_es)
    clang_scurve = sorted(clang_es, key=lambda e: e[2])
    clang_y = [e[2] for e in clang_scurve]
    indices = map(lambda e: e[1], clang_scurve)
    gcc_scurve = sorted(gcc_es, key=lambda e: indices.index(e[1]))
    gcc_y = [e[2] for e in gcc_scurve]
    points_clang = plt.scatter(range(len(clang_y)), clang_y, label='gcc')
    points_gcc = plt.scatter(range(len(gcc_y)), gcc_y, c='r', label='gcc')
    f = plt.gcf()
    plt.axes().set_yscale('log')
    plt.axes().set_xticks(range(len(clang_y)))
    plt.axes().set_xticklabels(clang_x_ticklabels)
    plt.setp(plt.axes().get_xticklabels(), rotation=90)
    plt.axes().set_xlabel(u'программа')
    plt.axes().set_ylabel(u'время выполнения, с')
    plt.axes().grid(axis='both')
    p1 = plt.Rectangle((0, 0), 1, 1, fc='b')
    p2 = plt.Rectangle((0, 0), 1, 1, fc='r')
    plt.axes().legend((p1, p2), (points_clang.get_label(), points_gcc.get_label()), loc='best')
    plt.title(u"Время исполнения программ, скомпилированных двумя компиляторами на уровне оптимизации '-O2'")
    plt.show()
    ipdb.set_trace()


def calculate_overhead_time(context):
    context = copy.deepcopy(context)
    settings = context.settings
    nest_path_from_root(context, 'data/sources/time-test')
    saved_name = settings.program_name 
    settings.program_name = 'do_nothing'
    saved_path = settings.benchmark_root_dir
    settings.benchmark_root_dir = get_path(context)

    define_build_settings(settings, 
        '',
        '')
    b = settings.build_settings
    b.compiler = 'gcc'
    b.base_opt = '-O0'

    define_run_settings(settings)

    build(context)
    c = run_empty(context)
    overhead_time = c.time

    unnest_path(context)
    settings.benchmark_root_dir = saved_path
    settings.program_name = saved_name
    return c, overhead_time


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


def validate_default(context):
    """
    Perform validation on set of time-measurement programs and report errors.
    """

    nest_path_absolute(context, context.settings.framework_root_dir)
    vs = []
    cs = []
    c, overhead_time = calculate_overhead_time(context)

    for i in range(7):
        real_time_us = 10**i
        s = 'usleep_{0}'.format(real_time_us)
        context.settings.program_name = s
        define_build_settings(context.settings,
            '',
            '')
        context.settings.build_settings.compiler = 'gcc'
        context.settings.build_settings.base_opt = '-O0'
        build(context)
        c, v = validate(context, real_time_us / 10.**6, overhead_time)
        cs.append(c)
        vs.append(v)
    unnest_path(context)
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
    command = os.path.join(get_path(context), command)
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
    command = os.path.join(get_path(context), command)
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
    _, o_t = calculate_overhead_time(context)
    c, v = validate(context, None, o_t)

    experiment = create_experiment_document(context, c, v)
    print "Saving experiment now"
    experiment.save()
    return experiment


def create_experiment_document(context, c, v):
    c_d = CalibrationResultDocument(
        total_time=c.total_time,
        time=c.time,
        dispersion=c.dispersion,
        variance=c.variance,
        runs_number=c.runs_number,
        times_list=c.times_list)

    try:
        v_d = ValidationResultDocument(
            real_time=v.real_time,
            measured_time=v.measured_time,
            error=v.error,
            relative_error=v.relative_error)
    except:
        v_d = None

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
        validation_result=v_d,
        datetime=dt.datetime.utcnow())

    return experiment


def print_experiments(db):
    """Print all the experiments."""

    experiments = db.view('experiment/all')
    for e in experiments.all():
        print 'Experiment:'
        print 'Build:', e['value']['command_build']
        print 'Run:', e['value']['command_run']
        print 'Date & time:', e['value']['datetime']


def read_password():
    with open('password') as f:
        password = f.read()
    return password.strip('\n')


def setup_database(settings, context, local=True):
    """Setup the database."""

    if local:
        server = ck.Server()
    else:
        password = read_password()
        server = ck.Server(
            'https://constantius:{0}@constantius.cloudant.com'.format(
                password))
    db = server.get_db('adaptor')

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
        -o {1} {build_settings.linker_options}""").translate(None, '\n').format(
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
    print command
    r = calibrate(context, command)
    unnest_path(context)
    return r


def run_empty(context):
    """Run the generic version of program."""
    
    command = prepare_command_run(context.settings)
    nest_path_from_root(context, 'data/bin')
    print command
    r = calibrate_empty(context, command)
    unnest_path(context)
    return r


if __name__ == '__main__':
    main()
