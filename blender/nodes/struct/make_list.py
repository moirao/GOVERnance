import bpy

from .. import base


class ElementsMakeListNode(base.ElementsDynamicSocketsNode, base.BaseNode):
    bl_idname = 'elements_make_list_node'
    bl_label = 'Make List'

    text: bpy.