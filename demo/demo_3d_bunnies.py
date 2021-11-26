import taichi as ti
import math
import time
import numpy as np
import os
from utils import Tee
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
                        default=300,
                        help='Number of frames')
    parser.add_argument('-r', '--res', type=int, default=256, help='1 / dx')
    parser.add_argument('-o', '--out-dir', type=str, help='Output folder')
    args = parser.parse_args()
    print(args)
    return args


args = parse_args()

with_gui = True
write_to_disk = args.out_dir is not None

# Try to run on GPU
ti.init(arch=ti.cuda,
        kernel_profiler=True,
        device_memory_GB=7)

max_num_particles = 50000000
stop_seeding_at = 150
frame_dt = 1e-2

if with_gui:
    gui = ti.GUI("MLS-MPM",
                 res=1024,
                 background_color=0x112F41,
                 show_gui=args.show)

if write_to_disk:
    for i in range(1000):
        output_dir = f'{args.out_dir}_{i:03d}'
        if not os.path.exists(output_dir):
            break
    os.makedirs(f'{output_dir}/particles')
    os.makedirs(f'{output_dir}/previews')
    print("Writing 2D vis and binary particle data to folder", output_dir)
    tee = Tee(fn=f'{output_dir}/log.txt', mode='w')
    print(args)
else:
    output_dir = None

# Use 512 for final simulation/render
R = args.res
thickness = 2

mpm = MPMSolver(res=(R, R, R),
                size=1,
                unbounded=True,
                dt_scale=1,
                quant=True,
                use_g2p2g=False,
                support_plasticity=True,
                water_density=1.5)

mpm.add_surface_collide