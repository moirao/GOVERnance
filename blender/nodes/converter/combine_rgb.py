import bpy
import mathutils

from .. import base


def get_out_value(socket):
    node = socket.node
    out = node.outputs['Color']
    node = socket.node
    r = node.inputs[