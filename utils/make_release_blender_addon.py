import os
import sys
import zipfile


# taichi elements repository path
repo_path = os.path.dirname(os.path.abspath(os.curdir))
os.chdir(repo_path)
# blender addon folder name
BLEND_FOLDER = 'blender'
# engine folder