"""
This module contains classes of CouchDB documents.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

import couchdbkit as ck

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
    program_id = ck.StringProperty()
    build_settings = ck.SchemaProperty(BuildSettingsDocument)
    run_settings = ck.SchemaProperty(RunSettingsDocument)


class CPUInformationDocument(ck.Document):
    """CouchDB document, storing the information about hardware platform."""
    cpu_name = ck.StringProperty()
    cpu_mhz = ck.FloatProperty()
    cache_size = ck.IntegerProperty()
    flags = ck.StringProperty()


class HardwareInformationDocument(ck.Document):
    """CouchDB document, storing the information about hardware platform."""
    cpu = ck.SchemaProperty(CPUInformationDocument)


class ExperimentDocument(ck.Document):
    """CouchDB document, describing the experiment."""
    datetime = ck.DateTimeProperty()
    calibration_result = ck.SchemaProperty(CalibrationResultDocument)
    validation_result = ck.SchemaProperty(ValidationResultDocument)
    settings = ck.SchemaProperty(SettingsDocument)
    hardware_info = ck.SchemaProperty(HardwareInformationDocument)
    series = ck.StringProperty()
