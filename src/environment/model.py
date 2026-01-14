import math
import random

import mesa
import numpy as np

from src.environment.agent import SwarmAgent
from src.environment.objects import *
from src.environment.utils import *


class SwarmModel(mesa.Model):
    # region Setup
    def __init__(self, n_agents=100, world_size=100, n_sites=1, n_food=100, n_debris=100, template_genome=None,
                 seed=None):
        super().__init__(seed=seed)
        self.world_size = world_size
        self.time = 0

        self.hub = Hub(pos=np.array([0, 0], dtype='float64'), radius=10)
        self._init_sites(n_sites)

        self._init_food(n_food)
        self._init_debris(n_debris)

        if template_genome is None:
            SwarmAgent.create_agents(self, n_agents)
        else:
            SwarmAgent.from_genome(self, template_genome, n_agents)

    def _init_sites(self, n):
        self.sites = []
        for _ in range(n):
            angle = random.uniform(0, 2 * math.pi)
            r = 30  # fixed from paper
            pos = np.array([r * math.cos(angle), r * math.sin(angle)])
            self.sites.append(Site(pos))
        return self.sites

    def _init_food(self, n):
        self.food = []
        for i in range(n):
            site = random.choice(self.sites)
            offset = random.uniform(-2, 2), random.uniform(-2, 2)
            pos = (site.pos[0] + offset[0], site.pos[1] + offset[1])
            self.food.append(Food(pos))
        return self.food

    def _init_debris(self, n):
        self.debris = []
        for _ in range(n):
            offset = random.uniform(-8, 8), random.uniform(-8, 8)
            pos = (self.hub.pos[0] + offset[0], self.hub.pos[1] + offset[1])
            self.debris.append(Debris(pos))
        return self.debris

    # endregion

    def step(self):
        self.agents.shuffle_do("sense")
        self.agents.shuffle_do("act")
        self.agents.shuffle_do("update")
        self.time += 1

    # region Evaluation
    def food_at_hub_fraction(self):
        at_hub = sum(
            1 for f in self.food
            if dist(f.pos, self.hub.pos) <= self.hub.radius
        )
        return at_hub / len(self.food)

    def debris_removed_fraction(self):
        removed = sum(
            1 for d in self.debris
            if self.debris_is_outside_boundary(d.pos)
        )
        return removed / len(self.debris)

    # endregion

    # region Helpers
    def debris_is_outside_boundary(self, pos):
        return dist(pos, self.hub.pos) > self.hub.debris_boundary

    def nearest_site(self, pos):
        return min(self.sites, key=lambda s: dist(pos, s.pos), default=None)

    def nearest_food(self, pos):
        return min(self.food, key=lambda f: dist(pos, f.pos), default=None)

    def nearest_debris(self, pos):
        return min(self.debris, key=lambda d: dist(pos, d.pos), default=None)
    # endregion
