#!/usr/bin/env python
"""
MPL2 to SRT subtitle converter that DOES NOT change character encoding
(output has the same encoding as the input).
"""
import argparse
import io
import itertools
import math
import os
import re
import sys
import time
from typing import Iterable

LINE_RE = re.compile(br'^\[(?P<start>\d+)\]\[(?P<stop>\d+)\](?P<txt>.*)$')
LINESEP = os.linesep.encode()


def timefmt(frame: bytes) -> bytes:
    """Convert MPL2 time marker to SRT time format.

    >>> timefmt(b'1793')
    b'00:02:59.300'
    """
    secs = int(frame) / 10
    return time.strftime('%H:%M:%S', time.gmtime(secs)).encode() + \
        (b'.%03d' % (math.modf(secs)[0] * 1000))


def tokens(i: int, *,
           start: bytes, stop: bytes, txt: bytes) -> Iterable[bytes]:
    """Return SRT tokens corresponding to a single dialog line."""
    yield b'%d' % i
    yield LINESEP
    yield timefmt(start)
    yield b' --> '
    yield timefmt(stop)
    yield LINESEP
    for line in txt.split(b'|'):
        line = line.strip()
        if line.startswith(b'/'):
            yield b'<i>'
            yield line[1:]
            yield b'</i>'
        else:
            yield line
        yield LINESEP
    yield LINESEP


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--out', type=argparse.FileType('wb'),
                        default=io.open(sys.stdout.fileno(), 'wb'))
    parser.add_argument('file', nargs='?', type=argparse.FileType('rb'),
                        default=io.open(sys.stdin.fileno(), 'rb'))
    args = parser.parse_args()

    args.out.writelines(itertools.chain.from_iterable(
        tokens(i, **m.groupdict()) for i, m in enumerate(
            filter(None, map(LINE_RE.match, args.file)), 1)))
