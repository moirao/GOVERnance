import bpy

from .. import base


class ElementsMergeNode(base.ElementsDynamicSocketsNode, base.BaseNode):
    bl_idname = 'elements_merge_node'
    bl_label = 'Merge'

    text: bpy.props.StringProperty(default='List')
    text_empty: b