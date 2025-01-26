import networkx as nx
import json
import random

from agent import Agent
from utils import generate_llm_response

def create_network(num_agents, network_structure, connection_prob=0.1, VLU_fraction=0.1, exploration_prob=0.2, debug=False):
    
    if network_structure == "random":
        G = nx.erdos_renyi_graph(num_agents, connection_prob, seed=42)
    elif network_structure == "small_world":
        G = nx.watts_strogatz_graph(num_agents, 5, connection_prob, seed=42)
    elif network_structure == "scale_free":
        G = nx.barabasi_albert_graph(num_agents, 5, seed=42) 

    agents = {}
    VLU_agents = set(random.sample(list(G.nodes), int(VLU_fraction * num_agents)))

    all_personas = generate_llm_response(f"Generate {num_agents} random topic interests / personas that are about to post online on a social media platform. Each persona should be a few words, separated by commas. Reply in a single sentence listing these personas.")
    personas = [persona.strip() for persona in all_personas.split(",")]

    for node in G.nodes:
        role = "VLU" if node in VLU_agents else "non-VLU"
        agents[node] = Agent(node, role, personas[node], exploration_prob, debug)

    return G, agents

