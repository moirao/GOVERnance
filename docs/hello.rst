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

    mpm = MPMSolver(res=(128, 128))

    for i in range(3):
        mpm.add_cube(lower_corner=[0.2 + i * 0.1, 0.3 + i * 0.1],
                     cube_size=[0.1, 0.1],
                     material=MPMSolver.material_elastic)

    for frame in range(500):
        mpm.step(8e-3)
        if frame < 100 and frame % 2 == 0:
            mpm.add_cube(lower_corner=[0.1, 0.4],
                         cube_size=[0.05, 0.01],
                         material=MPMSolver.material_sand)
        if 10 < frame < 100 and frame % 2 == 0:
            mpm