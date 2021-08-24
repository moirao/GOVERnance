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
        out = val_1 - val_2
    elif mode == 'MULTIPLY':
        out[0] = val_1[0] * val_2[0]
        out[1] = val_1[1] * val_2[1]
        out[2] = val_1[2] * val_2[2]
    elif mode == 'DIVIDE':
        out[0] = val_1[0] / val_2[0]
        out[1] = val_1[1] / val_2[1]
        out[2] = val_1[2] / val_2[2]
    return out


def get_res_value(socket):
    node = socket.node
    out = node.outputs['Result']
    va