"""
Module to retrieve the information on hardware platform.

Platform-dependent, currently works on Unix only (uses '/proc' filesystem).

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

import parse
import os
import re

if os.name != 'posix':
    raise NotImplementedError

class CPUProbe():
    """Probe, parse and store the information about processor."""
    def __init__(self):
        """Read and store CPU information in plain text."""
        f = open('/proc/cpuinfo')
        self.cpuinfo = f.read()

    def cpu_mhz(self):
        """Parse and return CPU clock speed."""
        mhz = parse.search('cpu MHz\t\t: {:f}', self.cpuinfo)[0]
        return mhz

    def cache_size(self):
        """Parse and return cache size of CPU."""
        cache = parse.search('cache size\t: {:d} KB', self.cpuinfo)[0]
        return cache

    def flags(self):
        """Parse and return flags of the CPU.

        These are supported extensions and so on.
        """
        m = re.search('flags\t\t: [a-zA-Z0-9 ]*', self.cpuinfo)
        g = m.group()
        flags = g.split('flags\t\t: ')[1]
        return flags
