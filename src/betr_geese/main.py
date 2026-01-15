from config import *
from environment.swarm_model import SwarmModel

if __name__ == '__main__':
    trial_count = 10
    for trial in range(trial_count):
        model = SwarmModel(n_agents=N_AGENTS)
        for _ in range(STEPS):
            model.step()

        print(f"Learning:\nMaintenance:{model.debris_removed_fraction()}\nForaging:{model.food_at_hub_fraction()}")

        best_genome = None
        for agent in model.agents:
            if best_genome is None or best_genome.fitness < agent.genome.fitness:
                best_genome = agent.genome

        model = SwarmModel(n_agents=N_AGENTS, template_genome=best_genome)
        for _ in range(STEPS):
            model.step()

        print(f"\nTesting:\nMaintenance:{model.debris_removed_fraction()}\nForaging:{model.food_at_hub_fraction()}\n\n")
