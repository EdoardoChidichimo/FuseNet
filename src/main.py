from network import initialise_simulation
from simulation import run_simulation
from analysis import analyse_results

is_streamlit = False

SIMULATION_CONFIG = {
    "num_agents": 5,
    "llm_model": "gpt-3.5-turbo",
    "topic": "abortion ban",
    "has_persona": True,
    "network_structure": "fully_connected",
    "regulating": False,
    "connection_prob": 1,
    "k_neighbour": 10,
    "rewiring_prob": 0,
    "VLU_fraction": 0.8,
    "exploration_prob": 0.2,
    "generations": 3,
    "provides_explanation": True,
    "debug": False
}

G, agents, initial_social_circle = initialise_simulation(**SIMULATION_CONFIG)

output_file = f"{SIMULATION_CONFIG['llm_model'].replace('.', '_')}_{SIMULATION_CONFIG['network_structure']}_{SIMULATION_CONFIG['topic'].replace(' ', '_')}_log"

run_simulation(agents, SIMULATION_CONFIG["generations"], output_file, 
               initial_social_circle, is_streamlit)

analyse_results(output_file, SIMULATION_CONFIG, is_streamlit)