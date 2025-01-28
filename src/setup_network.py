import networkx as nx
import random

from agent import Agent
from utils import generate_llm_response

def create_network(num_agents, topic, network_structure, regulating=False, connection_prob=1, VLU_fraction=0.1, exploration_prob=0.2, debug=False):
    
    if network_structure == "random":
        G = nx.erdos_renyi_graph(num_agents, connection_prob, seed=42)
    elif network_structure == "small_world":
        rewiring_prob = 0.001
        G = nx.watts_strogatz_graph(num_agents, 5, rewiring_prob, seed=42)
    elif network_structure == "scale_free":
        G = nx.barabasi_albert_graph(num_agents, 5, seed=42) 
    elif network_structure == "fully_connected":
        G = nx.complete_graph(num_agents)

    agents = {}
    VLU_agents = set(random.sample(list(G.nodes), int(VLU_fraction * num_agents)))

    ## LOAD PERSONAS: (a) generate personas using LLM or (b) load from file
    
    # all_personas = generate_llm_response(f"Generate {num_agents} random topic interests / personas that are about to post online on a social media platform. Each persona should be a few words, separated by commas. Reply in a single sentence listing these personas.")
    # personas = [persona.strip() for persona in all_personas.split(",")]

    with open("data/personas.txt", "r") as file:
        personas = [persona.strip() for persona in file.readline().split(",")]

    initial_social_circle = {}
    for node in G.nodes:
        role = "VLU" if node in VLU_agents else "non-VLU"
        social_circle = set(G.neighbors(node))
        agents[node] = Agent(node, topic, role, personas[node], regulating, social_circle, exploration_prob, debug)
        initial_social_circle[node] = list(social_circle)

    return G, agents, initial_social_circle

