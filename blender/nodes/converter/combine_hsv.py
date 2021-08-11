import bpy
import mathutils

from .. import base


def get_out_value(socket):
    node = socket.node
    out