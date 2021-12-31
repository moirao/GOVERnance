
Blender nodes for Taichi elements
=================================

.. contents:: Contents
   :depth: 3






Node System
-----------
To create a taichi-elements simulation, you need to open the Elements window. Next, you need to create a new tree and add the necessary nodes. Addon requires many nodes for simulation. The main node is the Simulation node. This node store the Simulate button. Using this button, you can start the simulation. Examples of node trees can be downloaded from here: https://github.com/taichi-dev/taichi_elements_blender_examples






Node Sockets
------------
Taichi Elements has the following sockets:

**Integer** - represents a single integer value. Color - gray.

**Float** - represents a single float value. Color - gray.

**Vector** - represents a single 3d vector value. Color - gray.

**Struct** - structure that stores settings. Color - green.

**Add** - dynamic socket, which is needed to create new inputs. Color - black.

**Folder** - socket stores the path to the folder. Color - orange.

**Color** - stores color values in RGB format. Color - yellow.







Nodes
-----





MPM Solver
~~~~~~~~~~
.. tip:: Location: ``Add > Solvers > MPM Solver``

Description
"""""""""""
This node tells the simulation to use the MPM method (currently the Material Point Method is the only available simulation method). This node stores the settings of the MPM solver.

Parameters
""""""""""
`It has no parameters.`

Inputs
""""""
**Domain Object** - this socket is temporarily not working.

**Resolution** - domain resolution in voxels. The simulation will use a cubic domain. For example, if the Resolution value is 64, then the domain resolution will be 64 x 64 x 64.

**Size** - domain size in meters. The domain is created in such a way that its left, back, bottom corner (in the direction -X, -Y, -Z) is at coordinates 0, 0, 0. And if Size is 10.0, then the right, front, top corner will have a coordinate 10, 10, 10.

Outputs
"""""""
**Solver Settings** - it is a socket, which is a set of MPM solver parameters.





----------------------------

Material
~~~~~~~~
.. tip:: Location: ``Add > Solvers > Material``

Description
"""""""""""
This node stores information about the properties of the material. Using this node, you can specify what physical characteristics the emitter particles will have. Be it the material of water, snow, sand, etc.

Parameters
""""""""""
**Material Type** - This parameter specifies what the material will be for Emitters. The following options are available: water, sand, snow, elastic.

Inputs
""""""
`It has no inputs.`

Outputs
"""""""
**Material Settings** - This output is material settings. At the moment, from the settings there is only the type of material.





----------------------------

Integer
~~~~~~~
.. tip:: Location: ``Add > Inputs > Integer``

Description
"""""""""""
This is a simple input node that provides an integer value.

Parameters
""""""""""
`It has no parameters.`

Inputs
""""""
`It has no inputs.`

Outputs
"""""""
**Integer Value** - an integer value that can be connected to any other integer socket.





----------------------------

Float
~~~~~
.. tip:: Location: ``Add > Inputs > Float``

Description
"""""""""""
This node represents a floating point number.

Parameters
""""""""""
`It has no parameters.`

Inputs
""""""
`It has no inputs.`

Outputs
"""""""
**Float Value** - this socket provides a floating point number that can be connected to any float socket.





----------------------------

Folder
~~~~~~
.. tip:: Location: ``Add > Inputs > Folder``

Description
"""""""""""
Using this node, you can specify the folder.

Parameters
""""""""""
`It has no parameters.`

Inputs
""""""
`It has no inputs.`

Outputs
"""""""
**String Value** - this output is a string that indicates the folder. 





----------------------------

Emitter
~~~~~~~
.. tip:: Location: ``Add > Simulation Objects > Emitter``

Description
"""""""""""
Using this node, you can add an emitter to the simulation. Emitter is a mesh object that emits particles from its volume once.

Parameters
""""""""""
`It has no parameters.`

Inputs
""""""
**Emit Frame** - indicates the frame number in the timeline in which particles will be emitted.