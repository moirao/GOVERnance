from .. import base


class ElementsGravityNode(base.BaseNode):
    bl_idname = 'elements_gravity_node'
    bl_label = 'Gravity'

    category = base.COMPONENT

    def init(self, context):
        self.width = 190.0

        out = self.outputs.new('elements_struct_socket', 'Gravity')
        out.text = 'Gravity Force'

        dir