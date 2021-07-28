from .. import base


class ElementsHubNode(base.BaseNode):
    bl_idname = 'elements_hub_node'
    bl_label = 'Hub'

    required_nodes = {
        'Forces': [
            'elements_gr