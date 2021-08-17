import bpy

from .. import base


def get_out_value(socket):
    node = socket.node
    out = node.outputs['Float']
    integer = node.inputs['Intege