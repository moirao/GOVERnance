from .. import base


class ElementsFolderNode(base.BaseNode):
    bl_idname = 'elements_folder_node'
    bl_label = 'Folder'

    category = base.INPUT

    def init(self, context):
        self.width = 250