#!/usr/bin/env python
# coding: utf-8

"""
Integration module, handles most of high-level stuff.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

import sys
import os

import subprocess as sp
import textwrap as tw
import timeit
import datetime as dt

import recordtype as rt
import collections as cl

import csv

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import couchdbkit as ck
from couchdbkit.designer import push

import copy

import ipdb

import probe
from paths import *
from data_types import *
from documents import *
from commands import *
from settings import *
from context import *


def set_benchmark_root_nested(settings, path):
    settings.benchmark_root_dir = os.path.realpath(os.path.join(
        settings.framework_root_dir, path))


def perform_experiment1(settings, context):
    set_benchmark_root_nested(settings, 'data/sources/time-test/')
    perform_plot_error(context)


def show_experiment2(settings, context):
    set_benchmark_root_nested(settings, 'data/sources/time-test/')
    plot_vs()


def perform_experiment3(settings_context):
    set_benchmark_root_nested(settings, 'data/sources/polybench-c-3.2/')

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


def set_up(program_name, local, series):
    """Initialize the system."""
    settings = Settings(program_name)
    context = Context(settings, series, local=local)
    return context


def tear_down(context):
    """Finalize the system."""
    assert len(context.paths_manager.paths_stack) == 2
    del context


def perform_plot_error(context):
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
    v = ExperimentDocument.view('adaptor/experiment-gcc-vs-clang')
    l = []
    for doc in v:
        l.append((doc.settings.build_settings.compiler,
                  doc.settings.program,
                  doc.calibration_result.time))
    clang_es = filter(lambda e: e[0] == u'clang', l)
    gcc_es = filter(lambda e: e[0] == u'gcc', l)
    clang_x_ticklabels = map(lambda e: e[1], clang_es)
    gcc_x_ticklabels = map(lambda e: e[1], gcc_es)
    clang_scurve = sorted(clang_es, key=lambda e: e[2])
    clang_y = [e[2] for e in clang_scurve]
    indices = map(lambda e: e[1], clang_scurve)
    gcc_scurve = sorted(gcc_es, key=lambda e: indices.index(e[1]))
    gcc_y = [e[2] for e in gcc_scurve]
    points_clang = plt.scatter(range(len(clang_y)), clang_y, label='clang', s=60)
    points_gcc = plt.scatter(range(len(gcc_y)), gcc_y, c='r', label='gcc', s=60)
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


def plot_predictions(filename):
    f = open(filename)
    dr = csv.DictReader(f)
    dicts = [d for d in dr]
    dicts = sorted(dicts, key=lambda d: d['size'])
    ws = [d['width'] for d in dr]
    hs = [d['height'] for d in dr]
    times = [d['c#time'] for d in dr]
    preds = [d['Random Forest'] for d in dr]
    fig = plt.figure()
    ax3d = fig.add_subplot(111, projection='3d')
    ax3d.scatter(hs, ws, times, label=u'Экспериментальные данные')
    ax3d.scatter(hs, ws, preds, color='r',
        label=u'Значения, предсказанные моделью')
    ax3d.xaxis.set_label_text(u'Число строк матрицы')
    ax3d.yaxis.set_label_text(u'Число столбцов матрицы')
    ax3d.zaxis.set_label_text(u'Время исполнения, с')
    plt.show()


def plot_predictions_distinct(filename, predictor):
    expname = os.path.splitext(filename)[0]
    f = open(filename)
    dr = csv.DictReader(f)
    dicts = [d for d in dr]
    dicts.sort(key=lambda d: d['size'])
    # Get list of CPU frequencies.
    # For now we have to distinguish only by frequency or cache size,
    # since they change simultaneously.
    freqs = [d['cpu_mhz'] for d in dicts]
    # Make list of uniques frequency values
    freqs = list(set(freqs))
    cmaps = [plt.cm.Reds, plt.cm.Blues, plt.cm.Greens]
    colors = [('black', 'black'), ('black', 'black'), ('black', 'black')]

    for freq, cmap, cs in zip(freqs, cmaps, colors):
        for i, view in enumerate((None, (10, 10), (10, 170))):
            fig = plt.figure()
            fig.set_size_inches(15, 10)
            ax3d = fig.add_subplot(111, projection='3d')
            filter_func = lambda d: True if d['cpu_mhz'] == freq else False
            ws_freq = [int(d['width']) for d in dicts if filter_func(d)]
            hs_freq = [int(d['height']) for d in dicts if filter_func(d)]
            times_freq = [float(d['c#time']) for d in dicts if filter_func(d)]
            preds_freq = [float(d[predictor]) for d in dicts if filter_func(d)]
            if view is not None:
                ax3d.view_init(*view)
            ax3d.scatter(hs_freq, ws_freq, times_freq,
                c=cs[0], marker='o',
                cmap=cmap)
            ax3d.plot([], [], [], c=cs[0], marker='o',
                label=u'Экспериментальные данные для процессора с частотой {0} МГц'.format(freq))

            ax3d.scatter(hs_freq, ws_freq, preds_freq,
                label=u'Значения, предсказанные моделью, для процессора с частотой {0} МГц'.format(freq),
                c=cs[1], marker='x',
                cmap=cmap)
            ax3d.plot([], [], [], c=cs[1], marker='x',
                label=u'Значения, предсказанные моделью, для процессора с частотой {0} МГц'.format(freq))

            ax3d.set_zlim([0, 65])

            ax3d.xaxis.set_label_text(u'Число строк матрицы')
            ax3d.yaxis.set_label_text(u'Число столбцов матрицы')
            ax3d.zaxis.set_label_text(u'Время исполнения, с')

            plt.legend()

            plt.savefig('../an/{2}-{0}-{1}.png'.format(freq, i, expname))


def plot_predictions_distinct_2d(filename, predictor):
    expname = os.path.splitext(filename)[0]
    f = open(filename)
    dr = csv.DictReader(f)
    dicts = [d for d in dr]
    dicts.sort(key=lambda d: d['size'])
    # Get list of CPU frequencies.
    # For now we have to distinguish only by frequency or cache size,
    # since they change simultaneously.
    freqs = [d['cpu_mhz'] for d in dicts]
    # Make list of uniques frequency values
    freqs = list(set(freqs))
    cmaps = [plt.cm.Reds, plt.cm.Blues, plt.cm.Greens]
    colors = [('red', 'blue'), ('red', 'blue'), ('red', 'blue')]

    for freq, cmap, cs in zip(freqs, cmaps, colors):
        fig = plt.figure()
        fig.set_size_inches(15, 10)
        ax3d = fig.add_subplot(111)
        filter_func = lambda d: True if d['cpu_mhz'] == freq else False
        ws_freq = [int(d['width']) for d in dicts if filter_func(d)]
        times_freq = [float(d['c#time']) for d in dicts if filter_func(d)]
        preds_freq = [float(d[predictor]) for d in dicts if filter_func(d)]
        ax3d.scatter(ws_freq, times_freq,
            c=cs[0], marker='o', s=15,
            cmap=cmap)
        ax3d.plot([], [], c=cs[0], marker='o',
            label=u'Экспериментальные данные для процессора с частотой {0} МГц'.format(freq))

        ax3d.scatter(ws_freq, preds_freq,
            label=u'Значения, предсказанные моделью, для процессора с частотой {0} МГц'.format(freq),
            c=cs[1], marker='x', s=15,
            cmap=cmap)
        ax3d.plot([], [], c=cs[1], marker='x',
            label=u'Значения, предсказанные моделью, для процессора с частотой {0} МГц'.format(freq))

        ax3d.set_ylim([0, 65])

        ax3d.xaxis.set_label_text(u'Число строк матрицы')
        ax3d.yaxis.set_label_text(u'Время исполнения, с')

        plt.legend()

        plt.savefig('../an/{2}-{0}-2d.png'.format(freq, expname))


def plot_predictions_all(basename):
    for predictor in [
     ('knn', 'm#kNN'), ('rf', 'm#Random Forest'), ('earth', 'm#Earth Learner')]:
        filename = basename.format(predictor[0])
        plot_predictions_distinct(filename, predictor[1])


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


def print_experiments(db):
    """Print all the experiments."""

    experiments = db.view('experiment/all')
    for e in experiments.all():
        print 'Experiment:'
        print 'Build:', e['value']['command_build']
        print 'Run:', e['value']['command_run']
        print 'Date & time:', e['value']['datetime']


if __name__ == '__main__':
    main()
