STORAGE_THRESHOLD = 7
INTERACTION_PROB = 0.85
ENV_SIZE = 100
MUTATION_PROB = 0.1
CROSSOVER_PROB = 0.9
N_AGENTS = 100
STEPS = 12000
TRUNCATION_SIZE = 8
CODON_BITS = 8
MAX_TREE_DEPTH = 10
SITE_RADIUS = 10
NEST_RADIUS = 10
NEST_DEBRIS_BOUNDARY = 30
AGENT_SPEED = 2
GENOME_SIZE = 10
GENOME_EXCHANGE_RADIUS = 5

ALL_BEHAVIOR_NODES = {
    # postconditions
    "NeighbourObjects_Food",
    "NeighbourObjects_Debris",
    "NeighbourObjects_Site",
    "NeighbourObjects_Hub",
    "IsCarrying_Food",
    "IsCarrying_Debris",
    "DidAvoided_Site",
    "DidAvoided_Hub",
    "IsVisitedBefore_Site",
    "IsVisitedBefore_Hub",
    "DummyNode",
    # preconditions
    "IsDropable_Site",
    "IsDropable_Hub",
    "NeighbourObjects_Food_invert",
    "NeighbourObjects_Debris_invert",
    "NeighbourObjects_Site_invert",
    "NeighbourObjects_Hub_invert",
    "IsVisitedBefore_Site_invert",
    "IsVisitedBefore_Hub_invert",
    "IsCarrying_Food_invert",
    "IsCarrying_Debris_invert",
    # actions
    "CompositeSingleCarry_Food",
    "CompositeSingleCarry_Debris",
    "CompositeDrop_Food",
    "CompositeDrop_Debris",
    "Explore",
    "MoveTowards_Hub",
    "MoveTowards_Site",
    "MoveAway_Hub",
    "MoveAway_Site"
}
TOTAL_BEHAVIOURS = len(ALL_BEHAVIOR_NODES)
