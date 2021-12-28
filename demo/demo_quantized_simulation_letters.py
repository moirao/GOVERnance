
import taichi as ti
import math
import time
import numpy as np
from plyfile import PlyData, PlyElement
import os
import utils
from engine.mpm_solver import MPMSolver
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',
                        '--show',
                        action='store_true',
                        help='Run with gui')