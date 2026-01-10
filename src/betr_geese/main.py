from environment.genotype_to_phenotype import *
from environment.model import SwarmModel

if __name__ == '__main__':
    model = SwarmModel(n_agents=N_AGENTS)
    for _ in range(120):
        model.step()
    with open("results.txt", "a") as f:
        f.write(f"Debris removed:{model.debris_removed_fraction()}\nFood gathered:{model.food_at_hub_fraction()}")
