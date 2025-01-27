import json
from simulation import create_network
from utils import deadly_cocktail_strength
from tqdm import tqdm
from time import sleep

from analysis import network_analysis

def simulate(G, agents, generations, output_file):

    message_logs = {node: [] for node in G.nodes} 

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("[\n") 

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

            # Step 2: Read & Upvote All Other Messages
            message_list = list(global_messages.items())  # Convert dict to list of (author_id, message) tuples
            for node in set(agents.keys()):

                agent = agents[node]
                upvoted = agent.upvote_decision(message_list, node)

                for message, author_id in upvoted:
                    message_upvotes[message] += 1
                    agents[node].current_upvotes.append((message, author_id))  # Store upvote this gen

                progress_bar.update(1) 

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
                    "reflection": agents[sender].reflection
                }

            json.dump({f"Generation {generation + 1}": generation_data}, file, indent=4)
            if generation < generations - 1:
                file.write(",\n")  # Add comma if not the last generation

            progress_bar.close()

        file.write("\n]")  

    print(f"\nSimulation completed! Data saved to {output_file}")
    sleep(5)
    print("Analysing network...")

    network_analysis(output_file)



if __name__ == "__main__":

    num_agents = 20
    network_structure = "random"
    connection_prob = 1
    VLU_fraction = 0.3
    exploration_prob = 0.0
    generations = 5
    output_file = "data/VLU_agent_logs.json"

    G, agents = create_network(num_agents, 
                            network_structure, 
                            connection_prob, 
                            VLU_fraction, 
                            exploration_prob)

    simulate(G, agents, generations, output_file)