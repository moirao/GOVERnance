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
        has_cache_