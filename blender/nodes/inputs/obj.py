import bpy

from .. import base


class ElementsSourceObjectNode(base.BaseNode):
    bl_idname = 'elements_source_object_node'
    bl_label = 'Object'

    obj_name: bpy.props.StringProperty()
    category = base.INPUT

    def init(self, context):
        self.width = 180.0

        out = 