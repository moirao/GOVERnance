import bpy

from .. import base


def get_out_value(socket):
    node = socket.node
    out = node.outputs['Float']
    integer = node.inputs['Integer'].get_value()
    # scene
    scn = bpy.context.scene
    key = '{0}.{1}'.format(node.name, out.name)
    res = []
    for int_input in integer:
        res.append(float(int_input))
    scn.elements_sockets[key] = res


class ElementsIntToFloatNode(base.BaseNode):
    bl_idname = 'elements_int_to_float_node'
    bl_label = 'Integer to Float'

    category = base.CONVERTER
 