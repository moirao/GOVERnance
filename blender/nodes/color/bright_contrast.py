import bpy

from .. import base


def get_out_value(socket):
    node = socket.node
    out = node.outputs['Color']
    # input color
    in_col = node.inputs['Color'].get_value()
    # bright
    brg = node.inputs['Bright'].get_value()[0]
    # contrast
    cntr = node.inputs['Contrast'].get_value()[0]
    # scene
    scn = bpy.context.scene
    key = '{0}.{1}'.format(node.name, out.name)
    # resul