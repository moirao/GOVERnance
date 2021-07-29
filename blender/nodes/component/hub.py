from .. import base


class ElementsHubNode(base.BaseNode):
    bl_idname = 'elements_hub_node'
    bl_label = 'Hub'

    required_nodes = {
        'Forces': [
            'elements_gravity_node', 'elements_make_list_node',
            'elements_merge_node'
        ],
        'Emitters': [
            'elements_emitter_node', 'elements_make_list_node',
            'elements_merge_node', 'elements_inflow_node'
        ],
        'Colliders': [
            'elements_ground_node', 'elements_make_list_node',
            'elements_merge_node