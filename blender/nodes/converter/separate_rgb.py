import bpy

from .. import base


# color component indices
indices = {
    'R': 0,
    'G': 1,
    'B': 2
}


def get_out_value(socket, name):
    node = socket.node
    colors = node.inputs['Color'].get_value()
    component = node.outputs[name]
    res = []
    index = indices[name]
    for color in colors:
        res.append(color[index])
    scn = bpy.context.scene
    key = '{0}.{1}'.format(node.name, component.name)
    scn.elements_sockets[key] = res


def get_out_value_r(socket):
    get_out