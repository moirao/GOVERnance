import os
import time
import shutil
import argparse


ADDON_NAME = 'taichi_elements'


def copy_file(src_dir, out_dir, file):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    source_file_path = os.path.join(src_dir, file)
    shutil.copy(source_file_path, os.path.join(out_dir, file))


def copy_files(src_dir, out_dir):
    for file in os.listdir(src_dir):
        if os.path.isdir(os.path.join(src_dir, file)):
            src_subdir = os.path.join(src_dir, file)
            out_subdir = os.path.join(out_dir, file)
            copy_files(src_subdir, out_subdir)
        elif file.endswith('.py'):
            copy_file(src_dir, out_dir, file)


def get_addons_path():
    addons_var = 'BLENDER_USER_ADDON_PATH'
    addons_path = os.environ.get(addons_var)

    if addons_path:
        path_tail = os.path.join('scripts', 'addons')

        if addons_path.endswith(path_tail):
            return addons_path
        else:
            print('Incorrect environment variable: "{}"'.format(addons_var))
            print('Path must end with "scripts\\addons"')

    else:
        print('Missing environment variable: "{}"'.format(addons_var))


def install():
    print("Installing...")

    addons_path = get_addons_path()
    if not addons_path:
     