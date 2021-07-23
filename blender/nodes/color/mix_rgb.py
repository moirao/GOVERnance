import bpy

from .. import base


def mix_rgb(c1, c2, mode):
    if mode == 'ADD':
        res = (c1[0] + c2[0], c1[1] + c2[1], c1[2] + c2[2])
    elif mode == 'MULTIPLY':
        res = (c1[0] * c2[0], c1[1] * c2[1], c1[2] * c2[2])
    elif mode == 'SUBTRACT':
        res = (c1[0] - c2[0], c1[1] - c2[1], c1[2] - c2[2])
    elif mode == 'DIVIDE':
        res = [c1[0], c1[1], c1[2]]
        if c2[0] != 0.0:
            res[0] = c1[0] / c2[0]
        if c2[1] != 0.0:
            res[1] = c1[1] / c2[1]
        if c2[2] != 0.0:
            res[2] = c1[2] / c2[2]
    return res


def get_out_value(socket):
    node = socket.node
    out = node.outputs['Color']
    # input colors
    col1 = node.inputs['Color1'].get_value()
    col2 = node.inputs['Color2'].get_value()
    mode = node.mode
    # scene
    scn = bpy.context.scene
    key = '{0}.{1}'.form