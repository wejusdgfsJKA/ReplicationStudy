import py_trees


class PickUp(py_trees.behaviour.Behaviour):
    def __init__(self, agent, obj_type):
        super().__init__(f"PickUp_{obj_type}")
        self.agent = agent
        self.obj_type = obj_type

    def update(self):
        if self.agent.pick_up(self.obj_type):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class Drop(py_trees.behaviour.Behaviour):
    def __init__(self, agent, obj_type):
        super().__init__(f"Drop_{obj_type}")
        self.agent = agent
        self.obj_type = obj_type

    def update(self):
        return py_trees.common.Status.SUCCESS if self.agent.drop(self.obj_type) else py_trees.common.Status.FAILURE


class Explore(py_trees.behaviour.Behaviour):
    def __init__(self, agent):
        super().__init__("Explore")
        self.agent = agent

    def update(self):
        self.agent.explore()
        return py_trees.common.Status.SUCCESS


class MoveTowards(py_trees.behaviour.Behaviour):
    def __init__(self, agent, obj_type):
        super().__init__(f"MoveTowards_{obj_type}")
        self.agent = agent
        self.obj_type = obj_type

    def update(self):
        self.agent.move_towards(self.obj_type)
        return py_trees.common.Status.SUCCESS


class MoveAway(py_trees.behaviour.Behaviour):
    def __init__(self, agent, obj_type):
        super().__init__(f"MoveAway_{obj_type}")
        self.agent = agent
        self.obj_type = obj_type

    def update(self):
        self.agent.move_away(self.obj_type)
        return py_trees.common.Status.SUCCESS


class DummyNode(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__(f"DummyNode")

    def update(self):
        return py_trees.common.Status.SUCCESS
