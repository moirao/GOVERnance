import struct
import os
import time

import numpy

import bpy


# particles format version
PARS_FMT_VER = 1

# particle attributes
POS = 0    # position
VEL = 1    # velocity
COL = 2    # color
MAT = 3    # material id
EMT = 4    # emitter id

# numpy attributes type
attr_types = {
    POS: numpy.float32,
    VEL: numpy.float32,
    COL: numpy.int32,
    EMT: numpy.int32,
    MAT: numpy.int32
}

# attributes names
attr_names = {
    POS: 'pos',
    VEL: 'vel',
    COL: 'col',
    MAT: 'mat',
    EMT: 'emt'
}
attr_count = len(attr_names)


def write_pars(par_data, fpath, fname):
    data = bytearray()

    # particles format version
    data.extend(struct.pack('I', PARS_FMT_VER))

    # particles count
    pars_cnt = par_data[POS].shape[0]
    data.extend(struct.pack('I', pars_cnt))

    for attr_id in range(attr_count):
       fname_str = '{}_{}.bin'.format(fname, attr_names[attr_id])
       fname_byte = bytes(fname_str, 'utf-8')
       length = len(fname_byte)
       data.extend(struct.pack('I', length))
       data.extend(struct.pack('{}s'.format(length), fname_byte))

    for attr_id in range(a