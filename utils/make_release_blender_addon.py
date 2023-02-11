import os
import sys
import zipfile


# taichi elements repository path
repo_path = os.path.dirname(os.path.abspath(os.curdir))
os.chdir(repo_path)
# blender addon folder name
BLEND_FOLDER = 'blender'
# engine folder name
ENGINE_FOLDER = 'engine'
# out addon folder name
OUT_FOLDER = 'taichi_elements'
# blender addon path
blend_path = os.path.join(repo_path, BLEND_FOLDER)
# taichi e