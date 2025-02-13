from network import initialise_simulation
from simulation import run_simulation
from analysis import analyse_results

is_streamlit = False

SIMULATION_CONFIG = {
    "num_agents": 5,
    "generations": 3,
    "llm_model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "topic": "abortion ban",
    "has_persona": True,
    "network_structure": "fully_connected",
    "regulating": False,
    "connection_prob": 1,
    "k_neighbour": 10,
    "rewiring_prob": 0,
    "VLU_fraction": 0.8,
    "exploration_prob": 0.2,
    "provides_explanation": True,
    "debug": False
}

agents, initial_social_circle = initialise_simulation(**SIMULATION_CONFIG)

output_file = (
    f"simulation_{SIMULATION_CONFIG['num_agents']}agents_{SIMULATION_CONFIG['generations']}gens_"
    f"{SIMULATION_CONFIG['llm_model'].replace('.', '_')}_"
    f"{SIMULATION_CONFIG['network_structure']}_{SIMULATION_CONFIG['topic'].replace(' ', '_')}_"
    f"VLU{SIMULATION_CONFIG['VLU_fraction']}_explore{SIMULATION_CONFIG['exploration_prob']}_"
    f"temp{SIMULATION_CONFIG['temperature']}.json"
)

run_simulation(agents, SIMULATION_CONFIG["generations"], output_file, 
               initial_social_circle, is_streamlit)

analyse_results(output_file, SIMULATION_CONFIG, is_streamlit)