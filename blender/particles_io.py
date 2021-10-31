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
MAT 