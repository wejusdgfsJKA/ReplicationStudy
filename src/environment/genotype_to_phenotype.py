from behaviour_trees.primitives import *
from betr_geese.config import *

GRAMMAR = {
    "root": ["sequence", "selector"],
    "sequence": [{"Sequence": ["ppa"]}, {"Sequence": ["root", "root"]}, {"Sequence": ["sequence", "root"]}],
    "selector": [{"Selector": ["ppa"]}, {"Selector": ["root", "root"]}, {"Selector": ["selector", "root"]}],
    "ppa": [{"Selector": ["postconditions", "ppasequence"]}],
    "postconditions": ["SuccessNode", "ppa", {"Sequence": ["postcondition"]}],
    "postcondition": [("postcondition", "postconditiont"), "postconditiont"],
    "postconditiont": [["NeighbourObjects", "objects"], ["NeighbourObjects", "sobjects"], ["IsCarrying", "dobjects"],
                       ["NeighbourObjects", "dobjects"], ["DidAvoidedObj", "sobjects"],
                       ["IsVisitedBefore", "sobjects"]],
    "ppasequence": [{"Sequence": ["preconditions", "action"]}, {"Sequence": ["constraints", "action"]},
                    {"Sequence": ["preconditions", "constraints", "action"]}],
    "preconditions": [{"Sequence": ["precondition"]}],
    "precondition": [("precondition", "preconditiont"), "preconditiont"],
    "preconditiont": [["IsDropable", "sobjects"], ["NeighbourObjects", "objects"], ["IsVisitedBefore", "sobjects"],
                      ["NeighbourObjectsInvert", "objects"], ["IsVisitedBeforeInvert", "sobjects"],
                      ["IsCarrying", "dobjects"], ["IsCarryingInvert", "dobjects"]],
    "constraints": [{"Sequence": ["constraint"]}],
    "constraint": [("constraint", "constraintt"), "constraintt"],
    "constraintt": ["CanMove", ["IsCarryable", "dobjects"], ["IsDropable", "sobjects"]],
    "action": [["MoveTowards", "sobjects"], "Explore", ["CompositeCarry", "dobjects"],
               ["CompositeDrop", "dobjects"], ["MoveAway", "sobjects"]],
    "objects": ["sobjects", "dobjects"],
    "sobjects": ["Site", "Hub"],
    "dobjects": ["Food", "Debris"],
    "SuccessNode": ["DummyNode"]
}

ACTION_MAPPING = {
    "Selector": lambda _agent: selector(_agent),

    "Sequence": lambda _agent: sequence(_agent),

    "Explore": lambda _agent: explore(_agent),

    "MoveTowards_Food": lambda _agent: move_towards(_agent, "Food"),
    "MoveTowards_Debris": lambda _agent: move_towards(_agent, "Debris"),
    "MoveTowards_Hub": lambda _agent: move_towards(_agent, "Hub"),
    "MoveTowards_Site": lambda _agent: move_towards(_agent, "Site"),

    "MoveAway_Food": lambda _agent: move_away(_agent, "Food"),
    "MoveAway_Debris": lambda _agent: move_away(_agent, "Debris"),
    "MoveAway_Hub": lambda _agent: move_away(_agent, "Hub"),
    "MoveAway_Site": lambda _agent: move_away(_agent, "Site"),

    "CompositeCarry_Food": lambda _agent: composite_carry(_agent, "Food"),
    "CompositeCarry_Debris": lambda _agent: composite_carry(_agent, "Debris"),

    "CompositeDrop_Food": lambda _agent: composite_drop(_agent, "Food"),
    "CompositeDrop_Debris": lambda _agent: composite_drop(_agent, "Debris"),

    "NeighbourObjects_Food": lambda _agent: neighbour_objects(_agent, "Food"),
    "NeighbourObjects_Debris": lambda _agent: neighbour_objects(_agent, "Debris"),
    "NeighbourObjects_Hub": lambda _agent: neighbour_objects(_agent, "Hub"),
    "NeighbourObjects_Site": lambda _agent: neighbour_objects(_agent, "Site"),

    "NeighbourObjectsInvert_Food": lambda _agent: neighbour_objects_inverted(_agent, "Food"),
    "NeighbourObjectsInvert_Debris": lambda _agent: neighbour_objects_inverted(_agent, "Debris"),
    "NeighbourObjectsInvert_Hub": lambda _agent: neighbour_objects_inverted(_agent, "Hub"),
    "NeighbourObjectsInvert_Site": lambda _agent: neighbour_objects_inverted(_agent, "Site"),

    "IsCarrying_Food": lambda _agent: is_carrying(_agent, "Food"),
    "IsCarrying_Debris": lambda _agent: is_carrying(_agent, "Debris"),
    "IsCarryingInvert_Food": lambda _agent: is_carrying_inverted(_agent, "Food"),
    "IsCarryingInvert_Debris": lambda _agent: is_carrying_inverted(_agent, "Debris"),

    "IsCarryable_Food": lambda _agent: is_carryable(_agent, "Food"),
    "IsCarryable_Debris": lambda _agent: is_carryable(_agent, "Debris"),

    "IsVisitedBefore_Hub": lambda _agent: is_visited_before(_agent, "Hub"),
    "IsVisitedBefore_Site": lambda _agent: is_visited_before(_agent, "Site"),
    "IsVisitedBeforeInvert_Hub": lambda _agent: is_visited_before_inverted(_agent, "Hub"),
    "IsVisitedBeforeInvert_Site": lambda _agent: is_visited_before_inverted(_agent, "Site"),

    "CanMove": lambda _agent: can_move(_agent),

    "IsDropable_Hub": lambda _agent: is_dropable(_agent, "Hub"),
    "IsDropable_Site": lambda _agent: is_dropable(_agent, "Site"),

    "DidAvoidedObj_Hub": lambda _agent: avoided(_agent, "Hub"),
    "DidAvoidedObj_Site": lambda _agent: avoided(_agent, "Site"),
    "DummyNode": lambda _agent: dummy(_agent),
}


def expand(symbol: str, _genome, genome_idx: int, _agent, depth=0):
    if symbol not in GRAMMAR:  # terminal
        assert symbol in ACTION_MAPPING
        return [ACTION_MAPPING[symbol](_agent)], genome_idx
    if depth > MAX_TREE_DEPTH:
        return [ACTION_MAPPING["DummyNode"](_agent)], genome_idx

    productions = GRAMMAR[symbol]
    choice_idx = _genome[genome_idx % len(_genome)] % len(productions)
    production = productions[choice_idx]
    genome_idx += 1

    if isinstance(production, str):
        # expand further
        return expand(production, _genome, genome_idx, _agent, depth + 1)
    elif isinstance(production, list):
        assert len(production) == 2
        second_production_options = GRAMMAR[production[1]]
        choice_idx = _genome[genome_idx % len(_genome)] % len(second_production_options)
        picked = second_production_options[choice_idx]
        if picked in GRAMMAR:
            # this is "objects", gotta expand further
            genome_idx += 1
            p_options = GRAMMAR[picked]
            choice_idx = _genome[genome_idx % len(_genome)] % len(p_options)
            picked = p_options[choice_idx]
        genome_idx += 1
        new_symbol = production[0] + "_" + picked
        result = expand(new_symbol, _genome, genome_idx, _agent, depth + 1)
        return result
    elif isinstance(production, dict):
        current_parent_symbol = sorted(production.keys())[0]
        assert current_parent_symbol == "Sequence" or current_parent_symbol == "Selector"
        current_parent = ACTION_MAPPING[current_parent_symbol](_agent)
        children = production[current_parent_symbol]
        assert len(children) > 0
        for child in children:
            _children, genome_idx = expand(child, _genome, genome_idx, _agent, depth + 1)
            assert len(_children) > 0
            for __child in _children:
                assert __child is not None
                current_parent.add_child(__child)
        assert current_parent is not None
        return [current_parent], genome_idx
    elif isinstance(production, tuple):
        children = []
        for sym in production:
            assert isinstance(sym, str)
            new_children, genome_idx = expand(sym, _genome, genome_idx, _agent, depth + 1)
            assert len(new_children) > 0
            for child in new_children:
                assert child is not None
            children.extend(new_children)
        assert len(children) > 0
        for child in children:
            assert child is not None
        return children, genome_idx
    raise ValueError(f"Invalid production type: {production}")


def build_bt_from_genome_grammar(_agent, _genome):
    root, _ = expand("root", _genome, 0, _agent)
    assert len(root) == 1
    return py_trees.trees.BehaviourTree(root[0])


def compute_diversity(genome):
    unique_nodes = set()
    for node in genome.bt.root.iterate():
        unique_nodes.add(node.name)
    return (len(unique_nodes) - 2) / (total_unique_nodes - 2)


def compute_exploration(genome):
    visited = set()
    for node in genome.bt.root.iterate():
        if node.name == "MoveTowards_Hub":
            visited.add("hub")
        elif node.name == "MoveTowards_Site":
            visited.add("site")
    return len(visited)


def calculate_fitness(genome):
    return compute_diversity(genome) + compute_exploration(genome) / 2


total_unique_nodes = len(ACTION_MAPPING)
