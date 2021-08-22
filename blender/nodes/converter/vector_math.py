import bpy
import mathutils

from .. import base


def get_val(mode, val_1, val_2):
    val_1 = mathutils.Vector(val