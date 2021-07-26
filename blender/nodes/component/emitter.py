
import bpy

from .. import base


class ElementsEmitterNode(base.BaseNode):
    bl_idname = 'elements_emitter_node'
    bl_label = 'Emitter'

    required_nodes = {
        'Source Object': [
            'elements_source_object_node',
        ],
        'Material': [
            'elements_material_node',
        ]
    }
    typ: bpy.props.StringProperty(default='EMITTER')
    category = base.COMPONENT

    def init(self, context):
        self.width = 200.0

        out = self.outputs.new('elements_struct_socket', 'Emitter')
        out.text = 'Emitter'