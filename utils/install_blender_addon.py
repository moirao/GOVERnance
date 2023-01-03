import os
import time
import shutil
import argparse


ADDON_NAME = 'taichi_elements'


def copy_file(src_dir, out_dir, file):
    if not os.path.ex