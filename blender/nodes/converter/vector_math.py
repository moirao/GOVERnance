import bpy
import mathutils

from .. import base


def get_val(mode, val_1, val_2):
    val_1 = mathutils.Vector(val_1)
    val_2 = mathutils.Vector(val_2)
    out = mathutils.Vector()
    if mode == 'ADD':
        out = val_1 + val_2
    elif mode == 'SUBTRACT':
        out = val_1 - val_