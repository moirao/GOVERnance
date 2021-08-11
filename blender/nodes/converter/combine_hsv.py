import bpy
import mathutils

from .. import base


def get_out_value(socket):
    node = socket.node
    out = node.outputs['Color']
    node = socket.node
    h = node.inputs['H'].get_value()
    s = node.inputs['S'].get_value()
    v = node.inputs['V'].get_value()
    key = '{0}.