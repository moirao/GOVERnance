import bpy

from .. import base


# color component indices
indices = {
    'R': 0,
    'G': 1,
    'B': 2
}


def get_out_value(socket, name):
  