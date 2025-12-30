import py_trees

from environment.objects import Food, Debris
from src.environment.utils import *


class IsCarrying(py_trees.behaviour.Behaviour):
    def __init__(self, agent, obj_type):
        super().__init__(f"IsCarrying_{obj_type}")
        self.agent = agent
        self.obj_type = obj_type

    def update(self):
        obj = self.agent.carrying
        return (
            py_trees.common.Status.SUCCESS
            if obj and (isinstance(obj, Food) or isinstance(obj, Debris)) and self.agent.carrying.type == self.obj_type
            else py_trees.common.Status.FAILURE
        )


class IsDroppable(py_trees.behaviour.Behaviour):
    def __init__(self, agent, at_hub=True):
        super().__init__(f"IsDroppable_{"Hub" if at_hub else "Site"})")
        self.agent = agent
        self.at_hub = at_hub

    def update(self):
        if not self.at_hub:
            return py_trees.common.Status.FAILURE
        if self.agent.carrying is not None and self.agent.carrying.type == "Food" and dist(self.agent.model.hub.pos,
                                                                                           self.agent.pos) < self.agent.model.hub.radius:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE


class IsCarryable(py_trees.behaviour.Behaviour):
    def __init__(self, agent, obj_type):
        super().__init__(f"IsCarriable_{obj_type}")
        self.agent = agent
        self.obj_type = obj_type

    def update(self):
        if self.obj_type == DObjects.Food or self.obj_type == DObjects.Debris:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class NeighbourObjects(py_trees.behaviour.Behaviour):
    def __init__(self, agent, obj_type):
        super().__init__(f"NeighbourObjects_{obj_type}")
        self.agent = agent
        self.obj_type = obj_type

    def update(self):
        if self.obj_type is DObjects.Food and self.agent.blackboard.nearest_food is not None:
            return py_trees.common.Status.SUCCESS
        elif self.obj_type is DObjects.Debris and self.agent.blackboard.nearest_debris is not None:
            return py_trees.common.Status.SUCCESS
        elif self.obj_type is SObjects.Hub and self.agent.blackboard.nearest_hub is not None:
            return py_trees.common.Status.SUCCESS
        elif self.obj_type is SObjects.Site and self.agent.blackboard.nearest_site is not None:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class AvoidedLastStep(py_trees.behaviour.Behaviour):
    def __init__(self, agent, obj_type):
        super().__init__("AvoidedLastStep")
        self.agent = agent
        self.obj_type = obj_type

    def update(self):
        if self.obj_type == SObjects.Hub and self.agent.blackboard.avoided_last_step_hub:
            return py_trees.common.Status.SUCCESS
        if self.obj_type == SObjects.Site and self.agent.blackboard.avoided_last_step_site:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class VisitedBefore(py_trees.behaviour.Behaviour):
    def __init__(self, agent, obj_type):
        super().__init__(f"VisitedBefore_{obj_type}")
        self.agent = agent
        self.obj_type = obj_type

    def update(self):
        if self.obj_type == SObjects.Hub and self.agent.blackboard.visited_hub:
            return py_trees.common.Status.SUCCESS
        if self.obj_type == SObjects.Site and self.agent.blackboard.visited_site:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE
