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
        """
        Initialize system with given settings.

        Experiments will be performed in series with given name.
        You can determine local or remote server to use, or supply your own.
        """

        self.paths_manager = PathsManager(settings.framework_root_dir,
                                          settings.benchmark_root_dir,
                                          settings.benchmark_bin_dir)
        # The directory of where the import was
        self.paths_manager.nest_path_absolute(os.getcwd())
        # The root of the framework
        self.paths_manager.nest_path_absolute(settings.framework_root_dir)
        self.settings = settings

        if server is None:
            server = setup_database(settings, self.paths_manager, local)

        self.server = server
        self.series = series


    def __del__(self):
        """Take care of paths stack and current directory."""

        # The root of framework
        self.paths_manager.unnest_path()
        # The directory of where the import was
        self.paths_manager.unnest_path()