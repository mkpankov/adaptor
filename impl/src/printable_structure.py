"""
This module is printable structure.

It's used as base class for namedtuples and recordtypes.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""


import textwrap as tw


class PrintableStructure():
    """Pretty printing of namedtuple and recordtype."""
    def __str__(self):
        c = self.__class__
        s = tw.dedent("""
        {name}:
        """).format(name=c.__name__)
        for k, v in self._asdict().items():
            s += '\t{field:20}:\t{value}\n'.format(field=k, value=v)

        return s
