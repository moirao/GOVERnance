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
    obj = bpy.d