# standart modules
import threading
import struct
import os

# blender modules
import bpy
import bmesh

# addon modules
import taichi as ti
import numpy as np
from .engine import mpm_solver
from . import types
from . import particles_io
from . import nodes


WARN_SIM_NODE = 'Node tree must not contain more than 1 "Simulation" node.'
WARN_NOT_SIM_NODE = 'Node tree does not have "Simulation" node.'
mpm_solver.USE_IN_BLENDER = True
IMPORT_NODES = (
    'elements_particles_mesh_node',
)


# sim_node - simulation node
def get_cache_folder(operator, sim_node):
    # particles socket
    par_s = sim_node.outputs['Simulation Data']
    cache_nodes = []
    has_cache_node = False
    if par_s.is_linked:
        for link in par_s.links:
            # disk cache node
            disk = link.to_node
            if disk.bl_idname == nodes.ElementsCacheNode.bl_idname:
                cache_nodes.append(disk)
    if not len(cache_nodes):
        operator.is_finishing = True
        operator.report(
            {'WARNING'},
            'Node tree does not have "Cache" node.'
        )
        return None, has_cache_node
    elif len(cache_nodes) > 1:
        operator.is_finishing = True
        operator.report(
            {'WARNING'},
            'Node tree must not contain more than 1 "Cache" node.'
        )
        return None, has_cache_node
    else:
        cache_node = cache_nodes[0]
        has_cache_node = True
        folder_raw = cache_node.inputs['Folder'].get_value()[0]
        folder = bpy.path.abspath(folder_raw)
        return folder, has_cache_node


# get simulation nodes tree object
def get_tree_obj(node_tree):
    # simulation nodes tree object
    tree = types.Tree()

    for node in node_tree.nodes:
        if node.bl_idname == 'elements_simulation_node':
            tree.sim_nds[node.name] = node
        elif node.bl_idname in IMPORT_NODES:
            if node.bl_idname == 'elements_particles_mesh_node':
                import_type = 'PAR_MESH'
            node.get_class()
            tree.imp_nds[node.name] = node, import_type
        elif node.bl_idname == 'elements_cache_node':
            tree.cache_nds[node.name] = node

    return tree


def create_emitter(operator, solv, emitter, vel):
    # source object
    src_obj = emitter.source_object

    if not src_obj:
        operator.is_finishing = True
        operator.report(
            {'WARNING'},
            'Emmiter not have source object.'
        )
        return

    obj_name = src_obj.obj_name
    obj = bpy.data.objects.get(obj_name)

    if not obj:
        operator.is_finishing = True
        if not obj_name:
            operator.report(
                {'WARNING'},
                'Emmiter source object not specified.'
            )
        else:
            operator.report(
                {'WARNING'},
                'Cannot find emmiter source object: "{}".'.format(obj_name)
            )
        return
    if obj.type != 'MESH':
        operator.is_finishing = True
        operator.report(
            {'WARNING'},
            'Emmiter source object is not mesh: "{}".'.format(obj.name)
        )
        return
    if not emitter.material:
        operator.is_finishing = True
        operator.report(
            {'WARNING'},
            'Emmiter not have material.'
        )
        return
    if not len(obj.data.polygons):
        operator.is_finishing = True
        operator.report(
            {'WARNING'},
            'Emmiter source object not have polygons: "{}"'.format(obj.name)
        )
        return

    b_mesh = bmesh.new()
    b_mesh.from_mesh(obj.data)
    bmesh.ops.triangulate(b_mesh, faces=b_mesh.faces)
    # emitter triangles
    tris = []

    for face in b_mesh.faces:
         # triangle
        tri = []
        # v - bmesh vertex
        for v in face.verts:
            # final vertex coordinate
            v_co = obj.matrix_world @ v.co
            tri.extend(v_co)
        tris.append(tri)

    b_mesh.clear()
    tris = np.array(tris, dtype=np.float32)
    # material type
    mat = emitter.material.typ
    # taichi material
    ti_mat = mpm_solver.MPMSolver.materials.get(mat, None)

    if ti_mat is None:
        assert False, mat

    # emitter particles color
    red = int(emitter.color[0].r * 255) << 16
    green = int(emitter.color[0].g * 255) << 8
    blue = int(emitter.color[0].b * 255)
    color = red | green | blue
    # add emitter
    solv.add_mesh(
        triangles=tris,
        material=ti_mat,
        color=color,
        velocity=vel,
        emmiter_id=operator.emitter_indices[emitter]
    )
    return True


class ELEMENTS_OT_SimulateParticles(bpy.types.Operator):
    bl_idname = "elem