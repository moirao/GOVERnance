Using Taichi elements in Python
===============================

We introduce the Python API through a basic 2D demo.

.. code-block:: python

    import taichi as ti
    import numpy as np
    from mpm_solver import MPMSolver

    write_to_disk = False

    ti.init(arch=ti.cuda)  # Try to run on GPU

    gui = ti.GUI("Taichi Elements", res=512, background_color=0x112F41)

    mpm = MPMSolver