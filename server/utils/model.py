# coding=utf-8
from __future__ import absolute_import

from werkzeug.datastructures import ImmutableDict
from mongokit.paginator import Paginator


def attach_extend(entries, obj):
    for entry in entries:
        entry.update(obj)
    return entries


def make_paginator(cursor, paged=1, limit=60):
    """ Provides pagination on a Cursor object

    Keyword arguments:
    cursor -- Cursor of a returned query
    page   -- The page number requested
    limit  -- The number of items per page

    Properties:
    is_paginated  -- bool value determining if the cursor has multiple pages
    start_index   -- int index of the first item on the requested page
    end_index     -- int index of the last item on the requested page
    current_page  -- int page number of the requested page
    previous_page -- int page number of the previous page w.r.t.
                     current requested page
    next_page     -- int page number of the next page w.r.t.
                     current requested page
    has_next      -- True or False if the Cursor has a next page
    has_previous  -- True or False if the Cursor has a previous page
    page_range    -- list of page numbers
    num_pages     -- int of the number of pages
    count         -- int total number of items on the cursor
    """
    try:
        paged = max(1, int(paged))
    except Exception:
        paged = 1
    try:
        limit = max(1, int(limit))
    except Exception:
        limit = 60

    max_query = int(cursor._Cursor__limit)
    if max_query:
        limit = min(max_query, limit)

    return Paginator(cursor, paged, limit)


def make_offset_paginator(cursor, offset=0, limit=60):
    """ Provides pagination on a Cursor object

    Keyword arguments:
    cursor -- Cursor of a returned query
    offset   -- The page number requested
    limit  -- The number of items per page

    Properties:
    start_index   -- int index of the first item on the requested page
    end_index     -- int index of the last item on the requested page
    has_more      -- bool has more pages.
    count         -- int total number of items on the cursor
    """
    try:
        offset = max(0, int(offset))
    except Exception:
        offset = 0
    try:
        limit = max(1, int(limit))
    except Exception:
        limit = 60

    max_query = int(cursor._Cursor__limit)
    if max_query:
        limit = min(max_query, limit)

    return OffsetPaginator(cursor, offset, limit)


class OffsetPaginator(object):
    offset = 0
    limit = 0
    cursor = None

    def __init__(self, cursor, offset, limit):
        self.cursor = cursor
        self.offset = offset
        self.limit = limit
        self.cursor.skip(offset).limit(limit)

    @property
    def count(self):
        return self.cursor.count()

    @property
    def has_more(self):
        return self.count > (self.offset + self.limit)

    @property
    def start_index(self):
        return self.offset

    @property
    def end_index(self):
        return self.offset + self.limit


# dotted
def make_dotted_dict(obj):
    if isinstance(obj, dict):
        return DottedImmutableDict(obj)
    elif isinstance(obj, list):
        return [make_dotted_dict(o) for o in obj]
    else:
        return obj


class DottedDict(dict):
    def __init__(self, *args, **kwargs):
        super(DottedDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError as e:
            raise AttributeError(e.message)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(DottedDict, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(DottedDict, self).__delitem__(key)
        del self.__dict__[key]


class SilentlyStr(str):
    def return_new(*args, **kwargs):
        return SilentlyStr('')

    def silently(*args, **kwargs):
        return ''

    __getattr__ = return_new
    __call__ = return_new
    __unicode__ = silently
    __str__ = silently


class DottedImmutableDict(ImmutableDict):
    def __getattr__(self, item):
        try:
            v = self.__getitem__(item)
        except KeyError:
            # do not use None, it could be use by a loop.
            # None is not iterable.
            return SilentlyStr()
        if isinstance(v, dict):
            v = DottedImmutableDict(v)
        return v

    def __repr__(self):
        # remove class name when repr.
        return dict(self).__repr__()
