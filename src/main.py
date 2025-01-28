import json
from setup_network import create_network
from utils import deadly_cocktail_strength
from tqdm import tqdm
from time import sleep

from vis import network_analysis, fused_network_visualisation

def simulate(G, agents, generations, output_file, initial_social_circle, debug=False):

    message_logs = {node: [] for node in G.nodes} 

    with open(f"data/{output_file}.json", "w", encoding="utf-8") as file:
        file.write("[\n") 

        # Store Generation 0 (Initial Network Structure)
        generation_0_data = {str(node): {"role": agents[node].role, "persona": agents[node].persona, "social_circle": initial_social_circle[node]} for node in agents}
        json.dump({"Generation 0": generation_0_data}, file, indent=4)
        file.write(",\n")

        for generation in range(generations):
            global_messages = {}  # Store {agent_id: message}
            message_upvotes = {}  # Track upvotes for each message
            message_cocktail_scores = {}  # Track strength of deadly cocktail scores for each message

            progress_bar = tqdm(total=len(agents) * 2, desc=f"Generation {generation + 1}", unit="task", leave=True)

            # Reset upvotes for each agent
            for node in agents:
                agents[node].current_upvotes = []
            progress_bar.update(len(agents))  # Track reset step completion

            # Step 1: Message Generation
            for node in set(agents.keys()):
                agent = agents[node]
                message = agent.create_message()
                cocktail_strength = deadly_cocktail_strength(message)

                global_messages[node] = message
                message_logs[node].append(message)
                message_upvotes[message] = 0  # Initialize upvote count
                message_cocktail_scores[message] = cocktail_strength

                progress_bar.update(1) 

            if debug:
                print(f"\nGeneration {generation + 1} Messages Complete.")

            # Step 2: Read & Upvote All Other Messages
            message_list = list(global_messages.items())  # Convert dict to list of (author_id, message) tuples
            for node in set(agents.keys()):
                upvoted, removed_agents = agents[node].interact(message_list)  # Interact now returns upvoted + unfollowed

                for message, author_id in upvoted:
                    if author_id in global_messages:  # Ensure the author actually exists in this generation
                        message_upvotes[message] += 1
                        agents[node].current_upvotes.append((message, author_id))  # Store upvote this gen

                for removed_agent in removed_agents:
                    if removed_agent in agents[node].social_circle:  # Ensure valid social circle update
                        agents[node].social_circle.remove(removed_agent)  # Unfollow the agent

                progress_bar.update(1)

            if debug:
                print(f"\nGeneration {generation + 1} Interactions Complete.")

            # Step 3: Update Memory with Final Upvote Counts
            generation_data = {}
            for sender, message in global_messages.items():
                upvotes = message_upvotes[message]
                violence_score = message_cocktail_scores[message]
        
                agents[sender].previous_messages[-1] = (message, upvotes)  # Update message with final upvotes
                generation_data[sender] = {
                    "role": agents[sender].role,
                    "persona": agents[sender].persona,
                    "message": message,
                    "upvotes_received": upvotes,
                    "deadly_cocktail_score": violence_score,
                    "upvoted_messages": agents[sender].current_upvotes,
                    "reflection": agents[sender].reflection,
                    "social_circle": list(agents[sender].social_circle)
                }

            if debug:
                print(f"\nGeneration {generation + 1} Data Complete.")

            json.dump({f"Generation {generation + 1}": generation_data}, file, indent=4)
            if generation < generations - 1:
                file.write(",\n")  # Add comma if not the last generation

            progress_bar.close()

        file.write("\n]")  

    print(f"\nSimulation completed! Data saved to data/{output_file}.json")

    print("Analysing network...")
    network_analysis(output_file)
    fused_network_visualisation(output_file)


if __name__ == "__main__":

    num_agents = 15
    topic = "gun control"
    network_structure = "fully_connected"
    regulating = False
    connection_prob = 1
    VLU_fraction = 0.3
    exploration_prob = 0.0
    generations = 5
    output_file = f"{topic.replace(" ", "_")}_log"
    debug = True

    G, agents, initial_social_circle = create_network(num_agents, 
                               topic,
                               network_structure, 
                               regulating,
                               connection_prob, 
                               VLU_fraction, 
                               exploration_prob,
                               debug)

    simulate(G, agents, generations, output_file, initial_social_circle, debug)