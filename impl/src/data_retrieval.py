"""
Data retrieval from database and preparation for analysis.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""
import os
import scenarios
import parse

from documents import *


def collect_flags(l):
    # We need to parse flags and form a dictionary of binary features.
    # First, we go over entire dataset to collect available features.
    s = set()
    for doc in l:
        i_flags = doc.hardware_info.cpu.flags.split()
        # Add all items of list i_flags
        s = s.union(set(i_flags))

    return s


def make_flags_truthness_dict(flags_set, l):
    t_d = dict()
    for d in l:
        s = d.hardware_info.cpu.flags
        t_d[d._id] = {k: k in s for k in flags_set}

    return t_d


def prepare(context, series):
    """
    Extract all experiments of series and save their relevant data to csv.
    """

    v = ExperimentDocument.view('adaptor/experiment-series')
    l = v.all()

    flags_set = collect_flags(l)
    truthness_d = make_flags_truthness_dict(flags_set, l)

    ll = []
    for doc in l:
        r = parse.search(
            '-DNI={:d} -DNJ={:d}', doc.settings.build_settings.other_flags)

        # Get sorted list of flags
        d = truthness_d[doc._id]
        keys = sorted(d.keys())
        flags_list = [d[k] for k in keys]

        new_row = [
            doc._id, doc.datetime, doc.validation_result.measured_time,
            doc.settings.program, doc.settings.build_settings.compiler,
            doc.settings.build_settings.base_opt,
            doc.settings.build_settings.optimization_flags,
            r[0], r[1],
            doc.hardware_info.cpu.cpu_name, doc.hardware_info.cpu.cpu_mhz,
            doc.hardware_info.cpu.cache_size]
        new_row.extend(flags_list)

        ll.append(new_row)

    rr = map(lambda i: "\t".join(map(str, i)), ll)
    r = map(lambda i: i + '\n', rr)

    # Keys are from loop up there
    flags_headers_list = keys

    headers = 'id\tdatetime\ttime\tprogram_name\tcompiler\t'\
        'base_opt\toptimization_flags\twidth\theight\tcpu_name\t'\
        'cpu_mhz\tcpu_cache\t'
    full_headers = headers + '\t'.join(flags_headers_list) + '\n'

    f = open(os.path.join(context.paths_manager.framework_root_dir,
        'an/{0}.csv'.format(series)), 'w')
    f.write(full_headers)
    f.writelines(r)
