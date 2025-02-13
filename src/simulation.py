import json
import streamlit as st
from tqdm import tqdm
from processing import generate_posts, interact_with_posts, store_generation_data

def run_simulation(agents, generations, output_file, initial_social_circle, is_streamlit=False) -> None:
    """Runs the social network simulation for multiple generations with both Streamlit and tqdm progress tracking."""

    output_path = f"data/{output_file}.json"

    # Initialize progress bars
    if is_streamlit:
        st.write("### Running Simulation...")
        progress_bar = st.progress(0)  # Streamlit progress bar
        status_text = st.empty()  # Placeholder for status messages
    else:
        progress_bar = tqdm(total=generations * len(agents) * 2, desc="Simulation Progress", unit="task", leave=True)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("[\n")

        # Store initial network structure
        json.dump({"Generation 0": {str(node): {
            "role": agents[node].role,
            "persona": agents[node].persona,
            "social_circle": initial_social_circle[node]
        } for node in agents}}, file, indent=4)
        file.write(",\n")

        total_steps = generations * len(agents) * 2
        step_count = 0

        for generation in range(generations):
            status_message = f"**Generation {generation + 1} Processing...**"

            if is_streamlit:
                status_text.write(status_message)  # Update UI
            else:
                print(f"\n{status_message}")  # Terminal log

            # Initialize data
            generation_data = {}
            global_posts, post_upvotes, post_cocktail_scores = {}, {}, {}

            # Step 1: Generate Posts
            generate_posts(agents, global_posts, post_upvotes, post_cocktail_scores, progress_bar if not is_streamlit else None)

            step_count += len(agents)
            if is_streamlit:
                progress_bar.progress(min(step_count / total_steps, 1.0))
                status_text.write(f"✅ Generation {generation + 1}: Posts Generated")
            else:
                progress_bar.update(len(agents))

            # Step 2: Interaction (Upvotes & Unfollows)
            interact_with_posts(agents, global_posts, post_upvotes, generation_data, progress_bar if not is_streamlit else None)

            step_count += len(agents)
            if is_streamlit:
                progress_bar.progress(min(step_count / total_steps, 1.0))
                status_text.write(f"✅ Generation {generation + 1}: Interactions Completed")
            else:
                progress_bar.update(len(agents))

            # Step 3: Store Data
            store_generation_data(agents, global_posts, post_upvotes, post_cocktail_scores, generation_data)

            json.dump({f"Generation {generation + 1}": generation_data}, file, indent=4)
            file.write(",\n" if generation < generations - 1 else "\n]")

        if is_streamlit:
            progress_bar.progress(1.0)
            st.success(f"Simulation results saved to `{output_path}`")
        else:
            print(f"Simulation results saved to {output_path}")

        if not is_streamlit:
            progress_bar.close()  # Close tqdm in CLI mode