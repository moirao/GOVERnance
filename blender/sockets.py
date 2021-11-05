
import bpy


# get reroute input socket
def get_socket(socket):
    node = socket.node
    for input_socket in node.inputs:
        for link in input_socket.links:
            from_node = link.from_node
            from_socket = link.from_socket
            if from_node: