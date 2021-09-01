import bpy

from .. import base


def get_loc(socket):
    get_res(socket, 'Location')


def get_euler(socket):
    get_res(socket, 'Rotation Euler')


def get_scale(sock