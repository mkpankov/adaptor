"""
This module describes the context of the system.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""


import recordtype as rt
from printable_structure import *
from database import *
from paths import *


class Context(PrintableStructure):
    """Context of the system."""
    def __init__(self,
                 settings,
                 series,
                 local=True,
                 server=None):

        self.paths_manager = PathsManager(settings.framework_root_dir,
                                          settings.benchmark_root_dir,
                                          settings.benchmark_bin_dir)
        self.settings = settings

        if server is None:
            server = setup_database(settings, self.paths_manager, local)

        self.server = server
        self.series = series