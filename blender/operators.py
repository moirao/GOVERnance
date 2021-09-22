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
    'elements_