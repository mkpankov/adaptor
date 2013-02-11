"""This module is printable structure."""

import textwrap as tw

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
