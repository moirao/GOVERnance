import bpy

from .. import base


class ElementsMaterialNode(base.BaseNode):
    bl_idname = 'elements_material_node'
    bl_label = 'Material'

    items = [
        ('WATER', 'Water', ''),
        ('SNOW', 'Snow', ''),
        ('ELASTIC', 'Elastic', ''),
        ('SAND', 'Sand', ''),
        ('STATIONARY', 'Stationary