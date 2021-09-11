import bpy

from .. import base


def get_pos_value(socket):
    node = socket.node

    verts = node.inputs['Vertices']
    verts_key = '{0}.{1}'.format(node.name, verts.name)
    scn.elements_sockets[verts_key] = verts.g