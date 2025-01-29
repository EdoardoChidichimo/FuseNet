import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

def fused_network_visualisation(output_file: str, parameters_details: str):
    with open(f"data/{output_file}.json", 'r') as f:
        raw_data = json.load(f)

    data = {k: v for entry in raw_data for k, v in entry.items()}
    generations = list(data.keys())
    num_generations = len(generations)

    G_fixed = nx.Graph()
    nodes = set()
    edges_by_generation = []
    VLU_agents = set()
    cumulative_upvotes_by_gen = []
    cumulative_upvotes = {int(agent_id): 0 for agent_id in data[generations[0]]}  # Track upvotes


    # Track mutual follows
    social_circles_by_gen = []

    for gen in generations:
        agents_data = data[gen]
        social_circles = {int(agent_id): set(map(int, agent_info.get("social_circle", []))) for agent_id, agent_info in agents_data.items()}
        social_circles_by_gen.append(social_circles)

        edges = []
        for agent_id, agent_info in agents_data.items():
            agent_id = int(agent_id)  # Ensure it's an integer
            nodes.add(agent_id)

            if agent_info.get("role", "") == "VLU":
                VLU_agents.add(agent_id)

            cumulative_upvotes[agent_id] += agent_info.get("upvotes_received", 0)

            # Check for mutual follows
            for followed_agent in social_circles.get(agent_id, set()):
                if followed_agent in social_circles and agent_id in social_circles[followed_agent]:  # Mutual follow check
                    edges.append((agent_id, followed_agent))

        edges_by_generation.append(edges)
        cumulative_upvotes_by_gen.append(cumulative_upvotes.copy()) 


    G_fixed.add_nodes_from(nodes)
    # pos = nx.spring_layout(G_fixed, seed=42)  
    pos = nx.kamada_kawai_layout(G_fixed)  # Fixed layout for all frames

    fig, ax = plt.subplots(figsize=(10, 10))

    caption_text = (
        "This animation visualizes the evolution of a mutual follow network over multiple generations. "
        "Nodes represent individual agents, while edges indicate mutual follows between them. "
        "Red nodes indicate Violent Language Users (VLU), while blue nodes are Non-VLU agents. "
        f"Over time, some agents unfollow others, causing shifts in the network structure.\n{parameters_details}"
    )

    def update(frame):
        ax.clear()
        G = nx.Graph()
        G.add_nodes_from(nodes)  # Ensure all nodes exist
        G.add_edges_from(edges_by_generation[frame])  # Apply edges for this generation

        node_sizes = [100 + (cumulative_upvotes_by_gen[frame][node] * 10) for node in G.nodes()]
        node_colors = ["red" if node in VLU_agents else "skyblue" for node in G.nodes()]
        nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color=node_colors, edge_color='gray', font_size=8, ax=ax)
        ax.set_title(f'Mutual Follow Network — {generations[frame]}')

        fig.text(
            0.5, 0.05, caption_text, wrap=True, horizontalalignment='center', fontsize=10,
            bbox=dict(facecolor="white", edgecolor="none", boxstyle="round,pad=0.5")
        )

    ani = animation.FuncAnimation(fig, update, frames=num_generations, interval=1000, repeat=True)

    ani.save(f"results/{output_file}_fused_network.gif", writer="pillow", fps=1)
    print(f"Animation saved as results/{output_file}_fused_network.gif")
