import bpy

from . import tree
from . import categories
from . import nodes
from . import sockets
from . import operators
from . import handlers


addon_modules = [
    tree,
    sockets,
    nodes,
    categories,
    operators,
    handlers
]


def register():
    scn_type = bpy.types.Scene

    scn_type.elements_nodes = {}
    scn_type.elements_sockets = {}
    scn_type.elements_frame_start = bpy.props.IntProperty()
    scn_type.elements_frame_end = bpy.props.IntProperty()

    for addon_module in addon_modules:
   