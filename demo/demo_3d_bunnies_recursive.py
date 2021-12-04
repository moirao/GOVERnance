
import taichi as ti
import math
import time
import numpy as np
import os
import utils
from utils import create_output_folder
from engine.mpm_solver import MPMSolver
import argparse
from engine.mesh_io import load_mesh


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',
                        '--show',
                        action='store_true',
                        help='Run with gui')
    parser.add_argument('-f',
                        '--frames',
                        type=int,
                        default=10000,
                        help='Number of frames')
    parser.add_argument('-r', '--res', type=int, default=256, help='1 / dx')
    parser.add_argument('-o', '--out-dir', type=str, help='Output folder')
    parser.add_argument('-l', '--lod', type=int, help='LOG')
    parser.add_argument('-p',
                        '--output-ply',
                        type=str,
                        help='Output PLY files too')
    parser.add_argument('-m',
                        '--max-num-particles',
                        type=int,
                        help='Max num particles (millions)')
    parser.add_argument('--gpu-memory',
                        type=float,
                        default=9,
                        help='GPU memory')
    args = parser.parse_args()
    print(args)
    return args


args = parse_args()

with_gui = args.show
write_to_disk = args.out_dir is not None

# Try to run on GPU
ti.init(arch=ti.cuda, kernel_profiler=True, device_memory_GB=args.gpu_memory)

if with_gui:
    gui = ti.GUI("MLS-MPM",
                 res=1024,
                 background_color=0x112F41,
                 show_gui=args.show)

if write_to_disk:
    # output_dir = create_output_folder(args.out_dir)
    output_dir = args.out_dir
    os.makedirs(f'{output_dir}/particles')
    os.makedirs(f'{output_dir}/previews')
    print("Writing 2D vis and binary particle data to folder", output_dir)
else:
    output_dir = None

# Use 512 for final simulation/render
R = args.res

mpm = MPMSolver(res=(R, R, R),
                size=1,
                unbounded=True,
                dt_scale=1,
                quant=True,
                use_g2p2g=True,
                support_plasticity=False)

mpm.add_surface_collider(point=(0, 0, 0),
                         normal=(0, 1, 0),
                         surface=mpm.surface_slip,
                         friction=0.5)

mpm.add_surface_collider(point=(0, 1.9, 0),
                         normal=(0, -1, 0),
                         surface=mpm.surface_slip,
                         friction=0.5)

bound = 1.9

for d in [0, 2]:
    point = [0, 0, 0]
    normal = [0, 0, 0]
    b = bound
    point[d] = b
    normal[d] = -1
    mpm.add_surface_collider(point=point,
                             normal=normal,