import math
import random

import numpy as np
import py_trees
from mesa import Agent

from src.betr_geese.config import *
from src.environment.objects import *
from src.environment.utils import *


class SwarmAgent(Agent):
    def __init__(self, model):
        super().__init__(model)

        self._init_blackboard()

        self.model = model
        self.carrying = None
        self.pos = model.hub.pos.copy()
        self.blackboard.hub = model.hub
        self.blackboard.site = model.sites[0]

        self.genome = [random.randint(0, 50) for _ in range(GENOME_SIZE)]
        self.genome_storage_pool = [self.genome]

    def _init_blackboard(self):
        self.blackboard = py_trees.blackboard.Client(name="Agent")
        self.blackboard.register_key("is_carrying", access=py_trees.common.Access.WRITE)
        self.blackboard.is_carrying = False
        self.blackboard.register_key("nearest_food", access=py_trees.common.Access.WRITE)
        self.blackboard.nearest_food = None
        self.blackboard.register_key("nearest_debris", access=py_trees.common.Access.WRITE)
        self.blackboard.nearest_debris = None
        self.blackboard.register_key("nearest_hub", access=py_trees.common.Access.WRITE)
        self.blackboard.nearest_hub = None
        self.blackboard.register_key("nearest_site", access=py_trees.common.Access.WRITE)
        self.blackboard.nearest_site = None
        self.blackboard.register_key("hub", access=py_trees.common.Access.WRITE)
        self.blackboard.hub = None
        self.blackboard.register_key("site", access=py_trees.common.Access.WRITE)
        self.blackboard.site = None
        self.blackboard.register_key("target_object", access=py_trees.common.Access.WRITE)
        self.blackboard.target_object = None
        self.blackboard.register_key("visited_hub", access=py_trees.common.Access.WRITE)
        self.blackboard.visited_hub = False
        self.blackboard.register_key("visited_site", access=py_trees.common.Access.WRITE)
        self.blackboard.visited_site = False
        self.blackboard.register_key("avoided_last_step_hub", access=py_trees.common.Access.WRITE)
        self.blackboard.avoided_last_step_hub = False
        self.blackboard.register_key("avoided_last_step_site", access=py_trees.common.Access.WRITE)
        self.blackboard.avoided_last_step_site = False

    @staticmethod
    def nearest(agent, objects):
        return min(objects, key=lambda o: dist(agent.pos, o.pos), default=None)

    def sense(self):
        # exchange genome info
        self.find_closest_objects()
        self.share_genome()

    def share_genome(self):
        if random.random() > INTERACTION_PROB:
            return

        neighbors = [
            a for a in self.model.agents
            if a is not self and dist(self.pos, a.pos) <= GENOME_EXCHANGE_RADIUS
        ]

        if not neighbors:
            return

        genome_copy = self.genome.copy()
        for neighbor in neighbors:
            neighbor.exchange_genome(genome_copy)

    def exchange_genome(self, new_genome):
        self.genome_storage_pool.append(new_genome)

    def act(self):
        self.blackboard.visited_hub = False
        self.blackboard.visited_site = False
        self.blackboard.avoided_last_step_hub = False
        self.blackboard.avoided_last_step_site = False
        if self.carrying:
            self.carrying.pos = self.pos.copy()

        # tick the BT
        self._update_visited()

        if self.carrying:
            self.carrying.pos = self.pos.copy()

        if len(self.genome_storage_pool) > STORAGE_THRESHOLD:
            # perform genetic operations
            parents = self._perform_selection()
            children = self._perform_crossover(parents)
            self._perform_mutation(children)
            self.genome_storage_pool = self._select_children(children)

    # region Evolution
    def calculate_fitness(self, genome):
        return 0

    def _perform_selection(self):
        parents = [(g, self.calculate_fitness(g)) for g in self.genome_storage_pool[:]]
        parents.sort(key=lambda x: x[1], reverse=True)
        selected = parents[:TRUNCATION_SIZE]
        return selected

    def _perform_crossover(self, genomes):
        children = []
        for i in range(0, len(self.genome_storage_pool) - 1, 2):
            if random.random() > CROSSOVER_PROB:
                continue
            parent1 = self.genome_storage_pool[i]
            parent2 = self.genome_storage_pool[i + 1]
            crossover_point = random.randint(0, len(parent1) - 1)
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            children.append(child1)
            children.append(child2)
        return children

    def _perform_mutation(self, genomes, mutation_prob=0.01, codon_bits=8):
        for genome in genomes:
            for i, codon in enumerate(genome):
                if random.random() < mutation_prob:
                    # choose which bit to flip
                    bit_to_flip = random.randint(0, codon_bits - 1)

                    # flip the bit
                    codon ^= (1 << bit_to_flip)

                    # clamp to valid range (optional but safe)
                    max_value = (1 << codon_bits) - 1
                    codon = codon & max_value

                    # write back to genome
                    genome[i] = codon

    def _select_children(self, genomes):
        genomes.sort(key=lambda x: self.compute_diversity(x), reverse=True)
        return genomes[:STORAGE_THRESHOLD]

    def compute_diversity(self, genome):
        return 0

    # endregion

    def update(self):
        self_fitness = self.calculate_fitness(self.genome)
        for genome in self.genome_storage_pool:
            fitness = self.calculate_fitness(genome)
            if self_fitness < fitness:
                self.genome = genome
                self_fitness = fitness

    # region BT
    def pickup(self, obj):
        if not (isinstance(obj, Food) or isinstance(obj, Debris)):
            return False
        if obj.picked_up:
            return False
        if dist(self.pos, obj.pos) > AGENT_SPEED:
            return False

        self.pos = obj.pos
        self.blackboard.is_carrying = True
        self.carrying = obj
        obj.picked_up = True
        return True

    def drop(self, obj_type):
        if self.carrying and self.carrying.type == obj_type:
            self.carrying.pos = self.pos.copy()
            self.carrying.picked_up = False
            self.carrying = None
            self.blackboard.is_carrying = False
            return True
        return False

    def explore(self):
        radians = random.uniform(0, 2 * math.pi)
        self.pos += (AGENT_SPEED * np.array([math.cos(radians), math.sin(radians)]))
        np.clip(self.pos, -100, 100)
        # paranoia
        assert -100 <= self.pos[0] < 100
        assert -100 <= self.pos[1] < 100

    def move_towards(self, obj_type):
        if obj_type == SObjects.Hub:
            selected_pos = self.model.hub.pos.copy()
        else:
            selected_pos = self.model.sites[0].pos.copy()

        if dist(self.pos, selected_pos) > AGENT_SPEED:
            direction = selected_pos - self.pos
            norm_direction = (direction - np.min(direction)) / (np.max(direction) - np.min(direction))
            self.pos += (norm_direction * AGENT_SPEED)
        else:
            self.pos = selected_pos

    def move_away(self, obj_type):
        if obj_type == SObjects.Hub:
            selected_pos = self.model.hub.pos.copy()
            self.blackboard.avoid_last_step_hub = True
        else:
            selected_pos = self.model.sites[0].pos.copy()
            self.blackboard.avoid_last_step_site = True
        direction = self.pos - selected_pos
        norm_direction = (direction - np.min(direction)) / (np.max(direction) - np.min(direction))
        self.pos += (norm_direction * AGENT_SPEED)

    def _update_visited(self):
        site_dist = dist(self.pos, self.model.sites[0].pos.copy())
        if site_dist <= SITE_RADIUS:
            self.blackboard.visited_site = True

        hub_dist = dist(self.pos, self.blackboard.hub.pos.copy())
        if hub_dist <= NEST_RADIUS:
            self.blackboard.visited_hub = True

    def find_closest_objects(self):
        if dist(self.pos, self.model.hub.pos) <= NEST_RADIUS:
            self.blackboard.nearest_hub = self.model.hub
        else:
            self.blackboard.nearest_hub = None

        if dist(self.pos, self.model.sites[0].pos) <= SITE_RADIUS:
            self.blackboard.nearest_site = self.model.sites[0]
        else:
            self.blackboard.nearest_site = None

        available_food = [f for f in self.model.food if not f.picked_up]
        if not available_food:
            self.blackboard.nearest_food = None
        else:
            self.blackboard.nearest_food = min(available_food, key=lambda o: dist(self.pos, o.pos))

        available_debris = [f for f in self.model.debris if not f.picked_up]
        if not available_debris:
            self.blackboard.nearest_debris = None
        else:
            self.blackboard.nearest_debris = min(available_debris, key=lambda o: dist(self.pos, o.pos))
    # endregion
