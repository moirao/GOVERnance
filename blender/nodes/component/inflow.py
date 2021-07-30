import bpy

from .. import base


class ElementsInflowNode(base.BaseNode):
    bl_idname = 'elements_inflow_node'
    bl_label = 'Inflow'

    required_nodes = {
        'Source Object': [
            'elements_source_object_node',
        ],
        'Material': [
            'elements_material_node',
        ]
    }
    typ: bpy.props.StringProperty(default='INFLOW')

  