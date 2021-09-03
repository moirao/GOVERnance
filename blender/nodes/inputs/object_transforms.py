import bpy

from .. import base


def get_loc(socket):
    get_res(socket, 'Location')


def get_euler(socket):
    get_res(socket, 'Rotation Euler')


def get_scale(socket):
    get_res(socket, 'Scale')


def get_dir(socket):
    get_res(socket, 'Direction')


def get_res(socket, mode):
    node = socket.node
    out = node.outputs[mode]
    # scene
    scn = bpy.context.scene
    key = '{0}.{1}'.format(node.name, out.name)
    # input obj
    obj = node.inputs['Obj'].get_value()
    obj, _ = scn.elements_nodes[obj]
    obj_name = obj.obj_name
    obj = bpy.data.objects.get(obj_name)
    # result
    res = []
    if obj:
        # r - result
        if mode == 'Location':
            r = obj.location
        elif mode == 'Rotation Euler':
            r = obj.rotation_euler
        elif mode == 'Scale':
            r = obj.scale
        elif mode == 'Direction':
            matrix = obj.rotation_euler.to_matrix().to_3x3()
            r = (matrix[0][2], matrix[1][2], matrix[2][2])
        res.append((r[0], r[1], r[2]))
    scn.elements_sockets[key] = res


class ElementsObjectTransformsNo