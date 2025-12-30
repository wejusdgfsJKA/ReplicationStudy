from src.betr_geese.config import *
from src.environment.model import *

if __name__ == '__main__':
    model = SwarmModel(n_agents=N_AGENTS)
    model.step()
