import nodeitems_utils

from . import nodes


class ElementsNodeCategory(nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'elements_node_tree'


# get categories data
def get_categs_data():
    # nod