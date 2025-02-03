import json
from setup_network import create_network
from utils import deadly_cocktail_strength
from tqdm import tqdm

from vis import fused_network_interactive, fused_network_gif

def run_simulation(G, agents, generations, output_file, initial_social_circle, exploration_prob, debug=False):

    message_logs = {node: [] for node in G.nodes} 

    with open(f"data/{output_file}.json", "w", encoding="utf-8") as file:
        file.write("[\n") 

        # Store Generation 0 (Initial Network Structure)
        generation_0_data = {str(node): {"role": agents[node].role, "persona": agents[node].persona, "social_circle": initial_social_circle[node]} for node in agents}
        json.dump({"Generation 0": generation_0_data}, file, indent=4)
        file.write(",\n")

        for generation in range(generations):
            generation_data = {}

            global_messages = {}  # Store {agent_id: message}
            message_upvotes = {}  # Track upvotes for each message
            message_cocktail_scores = {}  # Track strength of deadly cocktail scores for each message

            progress_bar = tqdm(total=len(agents) * 2, desc=f"Generation {generation + 1}", unit="task", leave=True)

            # Reset upvotes for each agent
            for node in agents:
                agents[node].current_upvotes = []
            progress_bar.update(len(agents)) 


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
            message_list = list(global_messages.items())  
            for node in set(agents.keys()):
                upvoted, removed_agents, explanations = agents[node].interact(message_list, exploration_prob)  # Interact now returns upvoted + unfollowed

                for message, author_id in upvoted:
                    if author_id in global_messages: 
                        message_upvotes[message] += 1
                        agents[node].current_upvotes.append((message, author_id))  

                for removed_agent in removed_agents:
                    if removed_agent in agents[node].social_circle: 
                        agents[node].social_circle.remove(removed_agent)

                if node not in generation_data:
                    generation_data[node] = {
                        "role": agents[node].role,
                        "persona": agents[node].persona,
                        "message": "",
                        "upvotes_received": 0,
                        "deadly_cocktail_score": 0,
                        "upvoted_messages": [],
                        "reflection": "",
                        "social_circle": [],
                        "explanations": {}  
                    }

                if agents[node].provides_explanation:
                    for message, explanation in explanations.items():
                        generation_data[node]["explanations"][message] = explanation  

                progress_bar.update(1)

            if debug:
                print(f"\nGeneration {generation + 1} Interactions Complete.")

            # Step 3: Update Memory with Final Upvote Counts
            for sender, message in global_messages.items():
                upvotes = message_upvotes[message]
                violence_score = message_cocktail_scores[message]
        
                agents[sender].previous_messages[-1] = (message, upvotes)  # Update message with final upvotes
                
                if sender not in generation_data:
                    generation_data[sender] = {}

                generation_data[sender].update({
                    "role": agents[sender].role,
                    "persona": agents[sender].persona,
                    "message": message,
                    "upvotes_received": upvotes,
                    "deadly_cocktail_score": violence_score,
                    "upvoted_messages": agents[sender].current_upvotes,
                    "reflection": agents[sender].reflection,
                    "social_circle": list(agents[sender].social_circle)
                })

            if debug:
                print(f"\nGeneration {generation + 1} Data Complete.")

            json.dump({f"Generation {generation + 1}": generation_data}, file, indent=4)
            if generation < generations - 1:
                file.write(",\n")  # Add comma if not the last generation

            progress_bar.close()

        file.write("\n]")

    print(f"\nSimulation completed! Data saved to data/{output_file}.json")


if __name__ == "__main__":

    num_agents = 3
    llm_model = "gpt-3.5-turbo" # "llama3.1-70b", "gpt-4o"
    topic = "abortion ban"
    network_structure = "fully_connected"
    regulating = False
    connection_prob = 1
    k_neighbour = 10
    rewiring_prob = 0
    VLU_fraction = 0.8
    exploration_prob = 0.2
    generations = 2
    output_file = f"test_explanation_{llm_model.replace(".","_")}_{network_structure}_{topic.replace(" ", "_")}_log"
    provides_explanation = False
    debug = False

    parameters_details = (
        f"Parameters:\nNo. of agents: {num_agents}, No. of Generations: {generations}, Exploration Probability: {exploration_prob}, Initial Network Structure: {network_structure}\n"
        f"Topic: {topic}, VLU Fraction: {VLU_fraction}, LLM Model: {llm_model}, "
        f"Self-regulating (à la Piao et al., 2025): {regulating}."
    )

    G, agents, initial_social_circle = create_network(num_agents, 
                                                    llm_model,
                                                    topic,
                                                    network_structure, 
                                                    regulating,
                                                    connection_prob,
                                                    k_neighbour, 
                                                    rewiring_prob,
                                                    VLU_fraction, 
                                                    exploration_prob,
                                                    provides_explanation,
                                                    debug)

    run_simulation(G, agents, generations, output_file, initial_social_circle, exploration_prob, debug)

    print("Analysing network...")
    fused_network_interactive(output_file)
    fused_network_gif(output_file, parameters_details)