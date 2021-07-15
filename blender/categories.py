import nodeitems_utils

from . import nodes


class ElementsNodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'elements_node_tree'


# get categories data
def get_categs_data():
    # node categories data
    data = {}

    for node in nodes.node_classes:
        data.setdefault(node.category, []).append(node.bl_idname)

    # key - category name, values - node identifier
    data['Layout'] = ['NodeFrame', 'NodeReroute']

    return data


def get_categories():
    data = get_categs_data()
    # node categories
    categories = []

    for name, ids in data.items()