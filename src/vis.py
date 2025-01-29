import json
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os 

def setup_emojis():    
    """Ensure all emojis are available by replacing newer emojis."""
    with open("data/personas.txt", "r") as f:
        f.readline()
        raw_emoji_pairs = f.readline().strip().split(", ")  # Second line: Emoji pairs

    cleaned_emoji_pairs = []
    
    for emoji_pair in raw_emoji_pairs:
        # Process each emoji pair
        cleaned_pair = emoji_pair.replace("-200D", "").replace("20BF", "1F4B0")
        cleaned_emoji_pairs.append(cleaned_pair)

    return cleaned_emoji_pairs

def fused_network_visualisation(output_file: str, parameters_details: str):
    """Generate a GIF animation of the fused mutual follow network over generations."""

    setup_emojis()

    with open("data/personas.txt", "r") as f:
        personas = f.readline().strip().split(", ")  # First line: Personas
        emoji_pairs = f.readline().strip().split(", ")  # Second line: Unicode emoji codes (can be 1, 2, or 3 parts)

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
    agent_emojis = {}

    for gen in generations:
        agents_data = data[gen]
        social_circles = {int(agent_id): set(map(int, agent_info.get("social_circle", []))) for agent_id, agent_info in agents_data.items()}
        social_circles_by_gen.append(social_circles)

        edges = []
        for agent_id, agent_info in agents_data.items():
            agent_id = int(agent_id)
            nodes.add(agent_id)

            if agent_info.get("role", "") == "VLU":
                VLU_agents.add(agent_id)

            cumulative_upvotes[agent_id] += agent_info.get("upvotes_received", 0)

            persona_index = personas.index(agent_info["persona"]) if agent_info["persona"] in personas else 0
            emoji_full = emoji_pairs[persona_index].split("-")  # Full emoji code (can be 1, 2, or 3 parts)
            
            agent_emojis[agent_id] = emoji_full

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
        "This animation visualises the evolution of a mutual follow network over multiple generations. "
        "Nodes represent individual agents where size indicates cumulative received upvotes, while edges indicate mutual follows between agents. "
        "Red nodes indicate Violent Language Users (VLU), while blue nodes are Non-VLU agents. "
        f"Over time, some agents unfollow others, causing shifts in the network structure.\n{parameters_details}"
    )

    def get_emoji_image(emoji_codes, zoom=0.25):
        """Fetch local emoji images based on OpenMoji Unicode codes (two per agent)."""
        images = []
        
        for emoji_code in emoji_codes: 
            img_path = os.path.abspath(f"data/emojis/{emoji_code}.png")
            
            try:
                emoji_img = plt.imread(img_path)
                images.append(OffsetImage(emoji_img, zoom=zoom))
            except FileNotFoundError:
                print(f"❌ Missing emoji image: {img_path}")

        return images if images else None

    def update(frame):
        ax.clear()
        G = nx.Graph()
        G.add_nodes_from(nodes)  # Ensure all nodes exist
        G.add_edges_from(edges_by_generation[frame])  # Apply edges for this generation

        node_sizes = [500 + (cumulative_upvotes_by_gen[frame][node] * 10) for node in G.nodes()]
        node_colors = ["red" if node in VLU_agents else "skyblue" for node in G.nodes()]
        
        nx.draw(G, pos, node_size=node_sizes, node_color=node_colors, edge_color='gray', font_size=12, ax=ax)

        for node, (x, y) in pos.items():
            if node in agent_emojis:
                emoji_images = get_emoji_image(agent_emojis[node])  # Get both emoji images
                
                if emoji_images and len(emoji_images) == 2:
                    ab1 = AnnotationBbox(emoji_images[0], (x - 0.03, y), frameon=False)  # Left emoji
                    ab2 = AnnotationBbox(emoji_images[1], (x + 0.03, y), frameon=False)  # Right emoji
                    
                    ax.add_artist(ab1)
                    ax.add_artist(ab2)


        ax.set_title(f'Mutual Follow Network — {generations[frame]}')

        fig.text(
            0.5, 0.03, caption_text, wrap=True, horizontalalignment='center', fontsize=10,
            bbox=dict(facecolor="white", edgecolor="none", boxstyle="round,pad=0.5")
        )

    ani = animation.FuncAnimation(fig, update, frames=num_generations, interval=1000, repeat=True)

    ani.save(f"results/{output_file}_fused_network.gif", writer="pillow", fps=1)
    print(f"Animation saved as results/{output_file}_fused_network.gif")
