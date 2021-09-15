import bpy

from .. import base


def get_pos_value(socket):
    node = socket.node

    verts = node.inputs['Vertices']
    verts_key = '{0}.{1}'.format(node.name, verts.name)
    scn.elements_sockets[verts_key] = verts.get_value()

    vels = node.inputs['Velocity']
    vels_key = '{0}.{1}'.format(node.name, vels.name)
    scn.elements_sockets[vels_key] = vels.get_value()

    cols = node.inputs['Color']
    cols_key = '{0}.{1}'.format(node.name, cols.name)
    scn.elements_sockets[cols_key] = cols.get_value()

    emit = node.inputs['Emitters']
    emit_key = '{0}.{1}'.format(node.name, emit.name)
    scn.elements_sockets[emit_key] = emit.get_value()


class ElementsMeshNode(base.BaseNode):
    bl_idname = 'elements_mesh_node'
    bl_label = 'Me