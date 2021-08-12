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
    key = '{0}.{1}'.format(node.name, out.name)
    res = []
    for h_val, s_val, v_val in zip(h, s, v):
        color = mathutils.Color()
        color.v = v_val
        color.s = s_val
        color.h = h_val
        res.append(color)
    scn = bpy.context.scene
    scn.elements_sockets[key] = res


class ElementsCombineHSVNode(base.BaseNode):
    bl_idname = 'elements_combine_hsv_node'
    bl_label = 'Com