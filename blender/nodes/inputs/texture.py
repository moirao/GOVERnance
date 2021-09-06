import bpy

from .. import base


class ElementsTextureNode(base.BaseNode):
    bl_idname = 'elements_texture_node'
    bl_label = 'Texture'

    tex_name: bpy.props.StringProperty()
    category = base.INPUT

    def init(self, context):
        self.width = 220.0

        out = self.outputs.n