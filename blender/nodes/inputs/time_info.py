import bpy

from .. import base


def get_f_st_value(socket):
    node = socket.node
    out = node.outputs['Frame Start']
    scn = bpy.context.scene
    key = '{0}.{1}'.format(node.name, out.name)
    scn.elements_sockets[key] = [scn.frame_start, ]


def get_f_en_value(socket):
    node = socket.node
    out = node.outputs['Frame End']
    scn = bpy.context.scene
    key = '{0}.{1}'.format(node.name, out.name)
    scn.elements_sockets[key] = [scn.frame_end, ]


def get_f_cur_value(socket):
    node = socket.node
    out = node.outputs['Frame Current']
    scn = bpy.context.scene
    key = '{0}.{1}'.format(node.name, out.name)
    scn.elements_sockets[key] = [scn.frame_current, ]


def get_fps_value(socket):
    node = socket.node
    out = node.outputs['FPS']
    scn = bpy.context.scene
    key = '{0}.{1}'.format(node.n