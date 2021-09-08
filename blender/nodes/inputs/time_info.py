import bpy

from .. import base


def get_f_st_value(socket):
    node = socket.node
    out = node.outputs['Frame Sta