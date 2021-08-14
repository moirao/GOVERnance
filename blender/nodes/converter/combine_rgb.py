import bpy
import mathutils

from .. import base


def get_out_value(socket):
    node = socket.node
    out = node.outputs['Color']
    node = socket.node
    r = node.inputs['R'].get_value()
    g = node.inputs['G'].get_value()
    b = node.inputs['B'].get_value()
    key = '{0}.{1}'.format(node.name, out.name)
    res = []
    for r_val, g_val, b_val in zip(r, g, b):
        color = mathutils.Color((r_val, g_val, b_val))
        res.append(color)
    scn = bpy.context.scene
    scn.elements_sockets[key] = res


class ElementsCo