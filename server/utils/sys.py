# coding=utf-8
from __future__ import absolute_import

import commands
import os
import re
from sys import getsizeof, stderr
from itertools import chain
from collections import deque


try:
    from reprlib import repr
except ImportError:
    pass


def total_sizeof(o, handlers={}, verbose=False):
    """
    Returns the approximate memory footprint an object and its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: lambda x: chain.from_iterable(x.items()),
                    set: iter,
                    frozenset: iter,
                    }
    all_handlers.update(handlers)  # user handlers take precedence
    seen = set()
    # track which object id's have already been seen
    # estimate sizeof object without __sizeof__
    default_size = getsizeof(0)

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print 'verbose:', s, type(o), repr(o), stderr

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)


def current_process_info():
    pid = os.getpid()
    res = commands.getstatusoutput('ps aux|grep ' + str(pid))[1].split('\n')[0]

    p = re.compile(r'\s+')
    info = p.split(res)
    return {
        'user': info[0],
        'pid': info[1],
        'cpu': info[2],
        'mem': info[3],
        'vsa': info[4],
        'rss': info[5],
        'start_time': info[6]
    }
