"""
This module handles database.

Database is currently CouchDB. 
In principle, it works on either local installation, or on CouchDB hosting,
such as Cloudant. Still not tested.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

import couchdbkit as ck
import subprocess as sp
import datetime as dt

from documents import *


def read_password():
    with open('password') as f:
        password = f.read()
    return password.strip('\n')


def setup_database(settings, paths_manager, local=True):
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

    paths_manager.nest_path_from_root('couch/adaptor')
    # We are stupid so we suppose the CouchApp is managed
    # to be stable version and we just re-publish it on launch.
    sp.check_call('couchapp push . http://localhost:5984/adaptor'.split())
    paths_manager.unnest_path()

    return server


def create_experiment_document(context, c, v, hardware_info):
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

    cpu_info_document = CPUInformationDocument(
        cpu_name=hardware_info.cpu_info.cpu_name,
        cpu_mhz=hardware_info.cpu_info.cpu_mhz,
        flags=hardware_info.cpu_info.flags,
        cache_size=hardware_info.cpu_info.cache_size)

    h_info_document = HardwareInformationDocument(
        cpu=cpu_info_document)

    experiment = ExperimentDocument(
        hardware_info=h_info_document,
        settings=s_d,
        calibration_result=c_d,
        validation_result=v_d,
        datetime=dt.datetime.utcnow())

    return experiment


def make_validation_document(v):
    v_doc = ValidationResultDocument(
        real_time=float(v.real_time),
        measured_time=float(v.measured_time),
        error=float(v.error),
        relative_error=float(v.relative_error))
    return v_doc


def store_validation_document(v):
    v_doc = make_validation_document(v)
    v_doc.save()
