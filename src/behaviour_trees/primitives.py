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
