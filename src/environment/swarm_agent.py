import math
import random

import numpy as np
from mesa import Agent

from environment.genotype_to_phenotype import *


class Genome:
    def __init__(self, genome, agent, bt):
        self.genome = genome
        self._agent = agent
        self.bt = build_bt_from_genome_grammar(agent, genome)
        self.fitness = calculate_fitness(self)

    def rebuild_bt(self):
        self.bt = build_bt_from_genome_grammar(self._agent, self.genome)
        self.fitness = calculate_fitness(self)

    def get_fitness(self):
        return self.fitness


class SwarmAgent(Agent):

    def __init__(self, model, genome=None):
        super().__init__(model)
        self._should_evolve = genome is None
        self._init_blackboard()

        self.carrying = None
        self.pos = model.hub.pos.copy()
        self.blackboard.hub = model.hub
        self.blackboard.site = model.sites[0]

        if self._should_evolve:
            bla = [random.randint(0, 50) for _ in range(GENOME_SIZE)]
            bt = build_bt_from_genome_grammar(self, bla)
            self.genome = Genome(bla, self, bt)
            self.genome.fitness = calculate_fitness(self.genome)
            self.genome_storage_pool = [self.genome]
        else:
            self.genome = Genome(genome.genome[:], self, build_bt_from_genome_grammar(self, genome.genome))

    @staticmethod
    def create_agents(model, n):
        return [SwarmAgent(model) for _ in range(n)]

    @classmethod
    def from_genome(cls, model, genome, n):
        return [cls(model, genome) for _ in range(n)]

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
        if self._should_evolve:
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

        for neighbor in neighbors:
            if isinstance(neighbor, SwarmAgent):
                neighbor.exchange_genome(Genome(self.genome.genome[:], neighbor, self.genome.bt))

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
        self.genome.bt.tick()
        self._update_visited()

        if self.carrying:
            self.carrying.pos = self.pos.copy()

        if self._should_evolve and len(self.genome_storage_pool) > STORAGE_THRESHOLD:
            # perform genetic operations
            parents = self._perform_selection()
            children = self._perform_crossover(parents)
            self._perform_mutation(children)
            for child in children:
                child.rebuild_bt()
                child.fitness = calculate_fitness(child)
            self.genome_storage_pool = self._select_children(children)

    # region Evolution

    def _perform_selection(self):
        self.genome_storage_pool.sort(key=lambda x: x.get_fitness(), reverse=True)
        return self.genome_storage_pool[:TRUNCATION_SIZE]

    def _perform_crossover(self, genomes):
        children = []
        for i in range(0, len(genomes) - 1, 2):
            if random.random() > CROSSOVER_PROB:
                continue
            parent1 = self.genome_storage_pool[i].genome
            parent2 = self.genome_storage_pool[i + 1].genome
            crossover_point = random.randint(0, len(parent1) - 1)
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            children.append(Genome(child1, self, build_bt_from_genome_grammar(self, child1)))
            children.append(Genome(child2, self, build_bt_from_genome_grammar(self, child2)))
        return children

    def _perform_mutation(self, genomes, mutation_prob=0.01, codon_bits=8):
        for genome in genomes:
            buffer = genome.genome
            for i, codon in enumerate(buffer):
                if random.random() < mutation_prob:
                    # choose which bit to flip
                    bit_to_flip = random.randint(0, codon_bits - 1)

                    # flip the bit
                    codon ^= (1 << bit_to_flip)

                    # clamp to valid range
                    max_value = (1 << codon_bits) - 1
                    codon = codon & max_value

                    # write back to genome
                    buffer[i] = codon
                    # why goddamn bit flipping, why
            genome.genome = buffer

    def _select_children(self, genomes):
        genomes.sort(key=lambda x: compute_diversity(x), reverse=True)
        return genomes[:STORAGE_THRESHOLD]

    # endregion

    def update(self):
        if self._should_evolve:
            self_fitness = calculate_fitness(self.genome)
            best_genome = None
            best_fitness = None
            for genome in self.genome_storage_pool:
                fitness = calculate_fitness(genome)
                if best_fitness is None or fitness < best_fitness:
                    best_genome = genome
                    best_fitness = fitness
            if best_genome is not None and self_fitness < best_fitness:
                self.genome = Genome(best_genome.genome[:], self,
                                     build_bt_from_genome_grammar(self, best_genome.genome))

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
        pos_delta = (AGENT_SPEED * np.array([math.cos(radians), math.sin(radians)]))
        # self.pos[0] += pos_delta[0]
        # self.pos[1] += pos_delta[1]
        self.pos += pos_delta
        np.clip(self.pos, -100, 100)

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
            self.blackboard.avoided_last_step_hub = True
        else:
            selected_pos = self.model.sites[0].pos.copy()
            self.blackboard.avoided_last_step_site = True
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
