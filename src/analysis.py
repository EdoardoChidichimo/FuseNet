import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

def network_analysis(data_file: str):
    with open(data_file, 'r') as f:
        raw_data = json.load(f)

    data = {k: v for entry in raw_data for k, v in entry.items()}
    generations = list(data.keys())
    num_generations = len(generations)

    G_fixed = nx.Graph()
    nodes = set()
    edges_by_generation = []
    VLU_agents = set()

    for gen in generations:
        agents_data = data[gen] 
        edges = []
        for agent_id, agent_info in agents_data.items():
            nodes.add(agent_id)

            if agent_info.get("role", "") == "VLU":
                VLU_agents.add(agent_id)

            for _, upvoted_agent in agent_info.get("upvoted_messages", []):
                edges.append((agent_id, str(upvoted_agent)))  # Ensure both are strings
        edges_by_generation.append(edges)

    G_fixed.add_nodes_from(nodes)
    pos = nx.spring_layout(G_fixed, seed=42)  # Fixed layout for all frames


    fig, ax = plt.subplots(figsize=(10, 8))

    def update(frame):
        ax.clear()
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges_by_generation[frame])
        node_colors = ["red" if node in VLU_agents else "skyblue" for node in G.nodes()]
        nx.draw(G, pos, with_labels=True, node_size=500, node_color=node_colors, edge_color='gray', font_size=8, ax=ax)
        ax.set_title(f'Generation {frame + 1}')

    ani = animation.FuncAnimation(fig, update, frames=num_generations, interval=1000, repeat=True)

    ani.save("results/VLU_upvote_evolution.gif", writer="pillow", fps=1)
    print("Animation saved as upvote_evolution.")

if __name__ == "__main__":
    network_analysis("data/VLU_agent_logs.json")