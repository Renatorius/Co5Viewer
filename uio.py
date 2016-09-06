"""
Created on Tue Oct 29 2013

@author: Kolja Glogowski
"""

import os
import re
import collections
import numpy as np
from struct import Struct   #, unpack

_uint_from_bytes = Struct('>I')
_re_desc = re.compile(r"^(\w+) (\w+) ?(.*)$")
_re_params = re.compile(r"\w+=(?:(?:'[^']*')|(?:\S+))")
_re_dims = re.compile('\d+:\d+')

def _parse_descriptor(s):
    m = _re_desc.match(s.decode())
    if not m:
        return None
    etype, name, pstr = m.groups()
    params = {}
    pitems = _re_params.findall(pstr)
    for it in pitems:
        key, value = it.split('=', 1)
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        params[key] = value
    return etype, name, params

def _read_block_size(f):
    data = f.read(4)
    if len(data) != 4:
        raise EOFError()
    return _uint_from_bytes.unpack(data)[0]

def _read_block(f):
    nbytes = _read_block_size(f)
    data = f.read(nbytes)
    if nbytes != _read_block_size(f):
        raise IOError('error reading block')
    return data

def _skip_block(f):
    nbytes = _read_block_size(f)
    f.seek(nbytes, 1)
    if nbytes != _read_block_size(f):
        raise IOError('error skipping block')

def _read_string(f):
    s = _read_block(f)
    while s.rstrip().endswith(b'&'):
        s = s.rstrip()[:-1] + _read_block(f)
    return s.rstrip()

def _read_array(f, dtype):
    dt = np.dtype(dtype).newbyteorder('>')
    nbytes = _read_block_size(f)
    data = np.fromfile(f, dtype=dt, count=nbytes//dt.itemsize)
    if nbytes != _read_block_size(f):
        raise IOError('error reading array')
    return data.astype(data.dtype.newbyteorder('='))


class _EntryMapping(collections.Mapping):
    def __init__(self, entries):
        self._entries = entries

    def __getitem__(self, key):
        for e in self._entries:
            if e.name == key:
                return e
        raise KeyError('%s' % key)

    def __iter__(self):
        for e in self._entries:
            yield e.name

    def __len__(self):
        return len(self._entries)

    def values(self):
        return self._entries

    def items(self):
        return [(e.name, e) for e in self._entries]

    def iteritems(self):
        for e in self._entries:
            yield (e.name, e)

    def itervalues(self):
        for e in self._entries:
            yield e


class Entry(object):
    def __init__(self, fd, pos, type, name, params, dtype, shape):
        self._fd = fd
        self.pos = pos
        self.type = type
        self.name = name
        self.params = params
        self.dtype = dtype
        self.shape = shape

    def __repr__(self):
        slist = [ self.type, self.name ]
        for k in ['b', 'd', 'u']:
            if k in self.params:
                v = self.params[k]
                if ' ' in v:
                    v = "'%s'" % v
                slist.append('%s=%s' % (k, v))
        return '<%s>' % (' '.join(slist))

    @property
    def data(self):
        self._fd.seek(self.pos)
        a = _read_array(self._fd, self.dtype)
        if self.type != 'character':
            return a.reshape(self.shape) if self.shape != None else a[0]
        else:
            if self.shape == None:
                return a[0].rstrip()
            elif len(self.shape) == 1:
                return [s.rstrip() for s in a]
            else:
                return a.reshape(self.shape)


class Box(_EntryMapping):
    def __init__(self, pos, params, entries):
        self.pos = pos
        self.params = params
        super(Box, self).__init__(entries)

    def __repr__(self):
        slist = [ 'box' ]
        slist.append('entries=%d' % len(self._entries))
        return '<%s>' % (' '.join(slist))


class DataSet(_EntryMapping):
    def __init__(self, pos, params, entries, box):
        self.pos = pos
        self.params = params
        self.box = box
        super(DataSet, self).__init__(entries)

    def __repr__(self):
        slist = [ 'dataset' ]
        slist.append('entries=%d' % len(self._entries))
        slist.append('boxes=%d' % len(self.box))
        return '<%s>' % (' '.join(slist))


def _read_file_header(f):
    header_string = _read_string(f)
    ff, uio, header = _parse_descriptor(header_string)
    if ff != 'fileform' or uio != 'uio':
        raise IOError('unknown file format')
    return header

def _read_entry(f):
    etype, name, params = _parse_descriptor(_read_string(f))
    if etype == 'table':
        raise IOError('uio files containing tables are not supported')
    pos = f.tell()
    dtype = None
    if 'b' in params:
        nbytes = int(params['b'])
        if etype == 'real':
            dtype = 'f%d' % nbytes
        elif etype == 'integer':
            dtype = 'i%d' % nbytes
        elif etype == 'character':
            dtype = 'S%d' % nbytes
        elif etype == 'complex':
            dtype = 'c%d' % nbytes
    shape = None
    if 'd' in params:
        fshape = []
        for x in _re_dims.findall(params['d']):
            x1, x2 = x.split(':')
            fshape.append(int(x2)-int(x1)+1)
        shape = tuple(reversed(fshape))
    return Entry(fd=f, pos=pos, type=etype, name=name, params=params,
                 dtype=dtype, shape=shape)

def _read_box_entries(f):
    box = []
    while True:
        entry = _read_entry(f)
        if entry.type == 'label' and entry.name == 'endbox':
            break
        box.append(entry)
        _skip_block(f)
    return box

def _read_dataset_entries(f):
    entries = []
    while True:
        entry = _read_entry(f)
        if entry.type == 'label':
            if entry.name == 'enddataset':
                break
            elif entry.name == 'box':
                box = Box(pos=f.tell(), params=entry.params,
                          entries=_read_box_entries(f))
                entries.append(box)
        else:
            entries.append(entry)
            _skip_block(f)
    return entries

def _read_file_entries(f):
    entries = []
    while True:
        try:
            entry = _read_entry(f)
        except EOFError:
            break
        if entry.type == 'label' and entry.name == 'dataset':
            ds_box = []
            ds_entries = []
            for ei in _read_dataset_entries(f):
                if isinstance(ei, Box):
                    ds_box.append(ei)
                elif isinstance(ei, Entry):
                    ds_entries.append(ei)
            ds = DataSet(pos=f.tell(), params=entry.params,
                         entries=ds_entries, box=ds_box)
            entries.append(ds)
        else:
            entries.append(entry)
            _skip_block(f)
    return entries


class File(_EntryMapping):
    def __init__(self, filename):
        self._fd = open(os.path.abspath(filename), 'rb')

        mag = self._fd.read(4+12)[4:]
        if mag != b'fileform uio':
            raise IOError('unsupported file format')
        self._fd.seek(0)
        self.header = _read_file_header(self._fd)

        entries = []
        self.dataset = []
        for x in _read_file_entries(self._fd):
            if isinstance(x, DataSet):
                self.dataset.append(x)
            elif isinstance(x, Entry):
                entries.append(x)
        super(File, self).__init__(entries)

    def close(self):
        self._fd.close()

    @property
    def closed(self):
        return self._fd.closed

    @property
    def name(self):
        return self._fd.name



if __name__ == '__main__':
    from numpy import *

    fname = os.path.join('/dat/pluto_2/salhab/cobold/scratchy/job_d3t40g45v50rsn01_526x526x176', 'rhd001.mean')

    f = File(fname)
    