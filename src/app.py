import streamlit as st
from network import initialise_simulation
from simulation import run_simulation
from analysis import analyse_results

is_streamlit = True

st.set_page_config(page_title="Social Media Simulation", layout="wide")

st.title("📢 FuseNet: Social Media Simulation")
st.markdown("Configure your simulation parameters and press **Run Simulation**.")


st.sidebar.header("Simulation Settings")

num_agents = st.sidebar.slider("Number of Agents", min_value=2, max_value=100, value=10)
generations = st.sidebar.slider("Number of Generations", min_value=1, max_value=10, value=3)

llm_model = st.sidebar.selectbox("LLM Model", ["gpt-3.5-turbo", "llama3.1-70b", "gpt-4o"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
topic = st.sidebar.text_input("Simulation Topic", value="gun control")
has_persona = st.sidebar.checkbox("Enable Personas", value=True)

network_structure = st.sidebar.selectbox(
    "Network Structure", 
    ["random", "small_world", "scale_free", "fully_connected"]
)

regulating = st.sidebar.checkbox("Enable Self-Regulation", value=False)
connection_prob = st.sidebar.slider("Connection Probability", 0.0, 1.0, 1.0)
k_neighbour = st.sidebar.slider("K-Neighbours (for small world & scale-free)", 1, 20, 10)
rewiring_prob = st.sidebar.slider("Rewiring Probability", 0.0, 1.0, 0.0)

VLU_fraction = st.sidebar.slider("Fraction of VLUs", 0.0, 1.0, 0.6)
exploration_prob = st.sidebar.slider("Exploration Probability", 0.0, 1.0, 0.2)
provides_explanation = st.sidebar.checkbox("Enable Explanation", value=False)
debug = st.sidebar.checkbox("Enable Debug Mode", value=False)


if st.button("🚀 Run Simulation"):
    
    SIMULATION_CONFIG = {
        "num_agents": num_agents,
        "llm_model": llm_model,
        "temperature": temperature,
        "topic": topic,
        "has_persona": has_persona,
        "network_structure": network_structure,
        "regulating": regulating,
        "connection_prob": connection_prob,
        "k_neighbour": k_neighbour,
        "rewiring_prob": rewiring_prob,
        "VLU_fraction": VLU_fraction,
        "exploration_prob": exploration_prob,
        "provides_explanation": provides_explanation,
        "debug": debug
    }

    G, agents, initial_social_circle = initialise_simulation(**SIMULATION_CONFIG)

    output_file = f"test_explanation_{llm_model.replace('.', '_')}_{network_structure}_{topic.replace(' ', '_')}_log"

    run_simulation(agents, generations, output_file, initial_social_circle, is_streamlit)
    
    st.success("✅ Simulation Completed!")
    
    analyse_results(output_file, SIMULATION_CONFIG, is_streamlit)
    st.info(f"Results saved as `{output_file}`")

st.markdown("Developed by **Edoardo Chidichimo**.")