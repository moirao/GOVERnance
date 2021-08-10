import bpy

from .. import base


def get_out_value(socket):
    node = socket.node
    out = node.outputs['Vector']
    col = node.inputs['Color'].get_value()
    # scene
   