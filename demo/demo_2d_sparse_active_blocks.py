import os
import taichi as ti
import numpy as np
import utils
import math
from engine.mpm_solver import MPMSolver
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--out-dir', type=str, help='Output folder')
    args = parser.parse_args()
    print(args)
    return args


args = parse_args()
write_to_disk = args.out_dir is not None
if write_to_disk:
    os.mkdir(f'{args.out_dir}')

ti.init(arch=ti.cuda)  # Try to run on GPU

n = 256
gui = ti.GUI("Taichi Elements", res=n, background_color=0x112F41)

activate_vis = ti.Vector.field(3, dtype=ti.f32, shape=[n, n])
mpm = MPMSolver(res=(n, n))

for i in range(3):
    mpm.add_cube(lower_corner=[0.2 + i * 0.1, 0.3 + 