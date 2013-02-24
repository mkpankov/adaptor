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


def prepare(context, series):
    """
    Extract all experiments of series and save their relevant data to csv.
    """

    v = ExperimentDocument.view('adaptor/experiment-all')
    l = []
    for d in v.all():
        try:
            if d.series == series:
                l.append(d)
        except AttributeError:
            pass

    ll = []
    for doc in l:
        r = parse.search(
            '-DNI={:d} -DNJ={:d}', doc.settings.build_settings.other_flags)

        ll.append([
            doc._id, doc.datetime, doc.validation_result.measured_time, 
            doc.settings.program, doc.settings.build_settings.compiler, 
            doc.settings.build_settings.base_opt, 
            doc.settings.build_settings.optimization_flags, 
            r[0], r[1], 
            doc.hardware_info.cpu.cpu_name, doc.hardware_info.cpu.cpu_mhz, 
            doc.hardware_info.cpu.flags, doc.hardware_info.cpu.cache_size])

    rr = map(lambda i: "\t".join(map(str, i)), ll)
    r = map(lambda i: i + '\n', rr)

    f = open(os.path.join(context.paths_manager.framework_root_dir, 
        'an/{0}.csv'.format(series)), 'w')
    f.writelines(r)
