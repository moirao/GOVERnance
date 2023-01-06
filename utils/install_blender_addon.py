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
            