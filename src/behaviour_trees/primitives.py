import py_trees.decorators

from behaviour_trees.actions import *
from behaviour_trees.builder import *
from behaviour_trees.conditions import *


def composite_carry(agent, obj_type):
    pickup_node = PickUp(agent, obj_type)
    postcondition = IsCarrying(agent, obj_type)
    preconditions = [NeighbourObjects(agent, obj_type), IsCarryable(agent, obj_type)]
    return make_ppa("CompositeSingleCarry", pickup_node, postcondition, preconditions)


def composite_drop(agent, obj_type):
    drop_node = Drop(agent, obj_type)
    postcondition = py_trees.decorators.Inverter(name=f"IsCarrying_{obj_type}_inverted",
                                                 child=IsCarrying(agent, obj_type))
    preconditions = [IsCarrying(agent, obj_type)]
    return make_ppa("CompositeDrop", drop_node, postcondition, preconditions)


def move_towards(agent, obj_type):
    return MoveTowards(agent, obj_type)


def move_away(agent, obj_type):
    return MoveAway(agent, obj_type)


def explore(agent):
    return Explore(agent)


def dummy(agent):
    return DummyNode()


def selector(agent):
    return py_trees.composites.Selector("Selector", memory=True)


def sequence(agent):
    return py_trees.composites.Sequence("Sequence", memory=True)


def neighbour_objects(agent, obj_type):
    return NeighbourObjects(agent, obj_type)


def neighbour_objects_inverted(agent, obj_type):
    return py_trees.decorators.Inverter(name=f"NeighbourObjects_{obj_type}_inverted",
                                        child=NeighbourObjects(agent, obj_type))


def is_carrying(agent, obj_type):
    return IsCarrying(agent, obj_type)


def is_carrying_inverted(agent, obj_type):
    return py_trees.decorators.Inverter(name=f"NeighbourObjects_{obj_type}_inverted",
                                        child=IsCarrying(agent, obj_type))


def is_carryable(agent, obj_type):
    return IsCarryable(agent, obj_type)


def is_visited_before(agent, obj_type):
    return VisitedBefore(agent, obj_type)


def is_visited_before_inverted(agent, obj_type):
    return py_trees.decorators.Inverter(name=f"NeighbourObjects_{obj_type}_inverted",
                                        child=VisitedBefore(agent, obj_type))


def is_dropable(_agent, obj_type):
    return IsDroppable(_agent, obj_type)


def can_move(_agent):
    return CanMove()


def avoided(_agent, obj_type):
    return AvoidedLastStep(_agent, obj_type)
