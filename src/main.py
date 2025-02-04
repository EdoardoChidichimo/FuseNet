import json
import random
import networkx as nx
from utils import deadly_cocktail_strength
from tqdm import tqdm
from vis import fused_network_interactive, fused_network_gif

from agent import Agent

def create_network(num_agents, llm_model, topic, network_structure, regulating=False, connection_prob=1, 
                   k_neighbour=5, rewiring_prob=0.001, VLU_fraction=0.1, exploration_prob=0.2, 
                   provides_explanation=False, debug=False):
    """Creates a social network graph and initialises agents."""

    # Select network structure
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
    with open("data/personas.txt", "r") as file:
        personas = [persona.strip() for persona in file.readline().split(",")]

    # Initialise agents
    agents = {
        node: Agent(node, llm_model, topic, "VLU" if node in VLU_agents else "non-VLU",
                    personas[node], regulating, set(G.neighbors(node)), exploration_prob, 
                    provides_explanation, debug)
        for node in G.nodes
    }

    # Store initial social circles
    initial_social_circle = {node: list(G.neighbors(node)) for node in G.nodes}

    return G, agents, initial_social_circle


def run_simulation(G, agents, generations, output_file, initial_social_circle, exploration_prob, debug=False):
    """Runs the social network simulation for multiple generations."""

    post_logs = {node: [] for node in G.nodes}
    output_path = f"data/{output_file}.json"

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("[\n")

        # Store initial network structure
        json.dump({"Generation 0": {str(node): {
            "role": agents[node].role,
            "persona": agents[node].persona,
            "social_circle": initial_social_circle[node]
        } for node in agents}}, file, indent=4)
        file.write(",\n")

        for generation in range(generations):
            progress_bar = tqdm(total=len(agents) * 2, desc=f"Generation {generation + 1}", unit="task", leave=True)
            
            # Run simulation steps
            generation_data = {}
            global_posts, post_upvotes, post_cocktail_scores = {}, {}, {}

            generate_posts(agents, global_posts, post_logs, post_upvotes, post_cocktail_scores, progress_bar)
            interact_with_posts(agents, global_posts, post_upvotes, generation_data, progress_bar)
            store_generation_data(agents, global_posts, post_upvotes, post_cocktail_scores, generation_data)

            json.dump({f"Generation {generation + 1}": generation_data}, file, indent=4)
            file.write(",\n" if generation < generations - 1 else "\n]")

            progress_bar.close()

    print(f"\nSimulation completed! Data saved to {output_path}")


def generate_posts(agents, global_posts, post_logs, post_upvotes, post_cocktail_scores, progress_bar):
    """Generates posts for each agent and calculates their impact."""
    for node, agent in agents.items():
        agent.current_upvotes = []
        post = agent.create_post()
        global_posts[node] = post
        post_logs[node].append(post)
        post_upvotes[post] = 0
        post_cocktail_scores[post] = deadly_cocktail_strength(post)
        progress_bar.update(1)


def interact_with_posts(agents, global_posts, post_upvotes, generation_data, progress_bar):
    """Handles interactions where agents upvote or unfollow others."""
    post_list = list(global_posts.items())

    for node, agent in agents.items():
        upvoted, removed_agents, explanations = agent.interact(post_list)

        for post, author_id in upvoted:
            post_upvotes[post] += 1
            agent.current_upvotes.append((post, author_id))

        agent.social_circle.difference_update(removed_agents)

        generation_data[node] = {
            "role": agent.role,
            "persona": agent.persona,
            "post": "",
            "upvotes_received": 0,
            "deadly_cocktail_score": 0,
            "upvoted_posts": [],
            "reflection": "",
            "social_circle": [],
            "explanations": explanations if agent.provides_explanation else {}
        }

        progress_bar.update(1)


def store_generation_data(agents, global_posts, post_upvotes, post_cocktail_scores, generation_data):
    """Updates agent memory and stores final statistics for each generation."""
    for sender, post in global_posts.items():
        upvotes = post_upvotes[post]
        agents[sender].previous_posts[-1] = (post, upvotes)

        generation_data[sender].update({
            "post": post,
            "upvotes_received": upvotes,
            "deadly_cocktail_score": post_cocktail_scores[post],
            "upvoted_posts": agents[sender].current_upvotes,
            "reflection": agents[sender].reflection,
            "social_circle": list(agents[sender].social_circle)
        })


def setup_simulation(num_agents, llm_model, topic, network_structure, regulating,
                     connection_prob, k_neighbour, rewiring_prob, VLU_fraction,
                     exploration_prob, provides_explanation, debug, generations):
    """Sets up the simulation by initialising the network and agents."""
    output_file = f"test_explanation_{llm_model.replace('.', '_')}_{network_structure}_{topic.replace(' ', '_')}_log"

    parameters_details = (
        f"Parameters:\nNo. of agents: {num_agents}, No. of Generations: {generations}, "
        f"Exploration Probability: {exploration_prob}, Initial Network Structure: {network_structure}\n"
        f"Topic: {topic}, VLU Fraction: {VLU_fraction}, LLM Model: {llm_model}, "
        f"Self-regulating (à la Piao et al., 2025): {regulating}."
    )

    G, agents, initial_social_circle = create_network(
        num_agents, llm_model, topic, network_structure, regulating,
        connection_prob, k_neighbour, rewiring_prob, VLU_fraction,
        exploration_prob, provides_explanation, debug
    )

    return G, agents, initial_social_circle, output_file, parameters_details


def analyse_results(output_file, parameters_details):
    """Runs analysis and visualisation on the simulation results."""
    print("Analysing network...")
    fused_network_interactive(output_file)
    fused_network_gif(output_file, parameters_details)


if __name__ == "__main__":
    # Simulation parameters (to be controlled by UI in the future)
    SIMULATION_CONFIG = {
        "num_agents": 5,
        "llm_model": "gpt-3.5-turbo",
        "topic": "abortion ban",
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

    G, agents, initial_social_circle, output_file, parameters_details = setup_simulation(
        num_agents=SIMULATION_CONFIG["num_agents"],
        generations=SIMULATION_CONFIG["generations"],
        llm_model=SIMULATION_CONFIG["llm_model"],
        topic=SIMULATION_CONFIG["topic"],
        network_structure=SIMULATION_CONFIG["network_structure"],
        regulating=SIMULATION_CONFIG["regulating"],
        connection_prob=SIMULATION_CONFIG["connection_prob"],
        k_neighbour=SIMULATION_CONFIG["k_neighbour"],
        rewiring_prob=SIMULATION_CONFIG["rewiring_prob"],
        VLU_fraction=SIMULATION_CONFIG["VLU_fraction"],
        exploration_prob=SIMULATION_CONFIG["exploration_prob"],
        provides_explanation=SIMULATION_CONFIG["provides_explanation"],
        debug=SIMULATION_CONFIG["debug"],
    )

    run_simulation(G, agents, SIMULATION_CONFIG["generations"], output_file, 
                   initial_social_circle, SIMULATION_CONFIG["exploration_prob"], 
                   SIMULATION_CONFIG["debug"])

    analyse_results(output_file, parameters_details)