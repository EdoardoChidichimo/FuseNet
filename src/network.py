import networkx as nx
import random
from agent import Agent

def initialise_simulation(num_agents, llm_model, topic, has_persona, network_structure, regulating, connection_prob, 
                        k_neighbour, rewiring_prob, VLU_fraction, exploration_prob, provides_explanation, debug):
    """Creates a social network graph and initialises agents."""

    graph_generators = {
        "random": lambda: nx.erdos_renyi_graph(num_agents, connection_prob, seed=42),
        "small_world": lambda: nx.watts_strogatz_graph(num_agents, k_neighbour, rewiring_prob, seed=42),
        "scale_free": lambda: nx.barabasi_albert_graph(num_agents, k_neighbour, seed=42),
        "fully_connected": lambda: nx.complete_graph(num_agents),
    }
    G = graph_generators.get(network_structure, lambda: nx.complete_graph(num_agents))()

    # Assign VLU agents randomly
    VLU_agents = set(random.sample(list(G.nodes), int(VLU_fraction * num_agents)))

    # Load personas from file
    personas = []
    if has_persona:
        with open("data/personas.txt", "r") as file:
            personas = [persona.strip() for persona in file.readline().split(",")]

    # Initialise agents (100 personas in total, cycled through if more necessary)
    agents = {
        node: Agent(node, llm_model, topic, "VLU" if node in VLU_agents else "non-VLU",
                    personas[node % len(personas)] if has_persona else None, regulating, set(G.neighbors(node)), exploration_prob, 
                    provides_explanation, debug)
        for node in G.nodes
    }

    # Store initial social network structure
    initial_social_circle = {node: list(G.neighbors(node)) for node in G.nodes}

    return G, agents, initial_social_circle