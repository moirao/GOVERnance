import inspect

import bpy

from .base import *

# categories
from .inputs import *
from .output import *
from .component import *
from .color import *
from .converter import *
from .struct import *


node_classes = []
glabal_variables = globals().copy()
for variable_name, variable_object in glabal_variables.items():
    if hasattr(variable_object, '__mro__'):
        object_mro = i