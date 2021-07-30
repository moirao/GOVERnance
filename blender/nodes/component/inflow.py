import bpy

from .. import base


class ElementsInflowNode(base.BaseNode):
    bl_idname = 'elements_inflow_node'
    bl_label = 'Inflow'

    required_nodes = {
        'Source Object': [
            