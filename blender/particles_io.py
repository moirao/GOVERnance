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
    EMT: numpy.in