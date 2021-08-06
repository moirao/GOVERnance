from .. import base


class ElementsMpmSolverNode(base.BaseNode):
    bl_idname = 'elements_mpm_solver_node'
    bl_label = 'MPM Solver'

    category = base.COMPONENT

    def init(self, context):
        self.width = 180.0

    