import streamlit as st
from network import initialise_simulation
from simulation import run_simulation
from analysis import analyse_results

is_streamlit = True

st.set_page_config(page_title="Social Media Simulation", layout="wide")

st.title("📢 FuseNet")
st.markdown("Configure your simulation parameters and press **Run Simulation**.")

st.sidebar.header("Simulation Settings")

st.sidebar.markdown("---")

st.sidebar.subheader("⚙️ GENERAL CONFIGURATION")
num_agents = st.sidebar.slider("Number of Agents", min_value=2, max_value=100, value=10)
generations = st.sidebar.slider("Number of Generations", min_value=1, max_value=10, value=3)
topic = st.sidebar.text_input("Simulation Topic", value="gun control")

st.sidebar.markdown("---")

st.sidebar.subheader("🧑‍🤝‍🧑 AGENT BEHAVIOUR")
VLU_fraction = st.sidebar.slider("Fraction of VLUs (Violent Language Users)", 0.0, 1.0, 0.6)
exploration_prob = st.sidebar.slider("Exploration Probability", 0.0, 1.0, 0.2)
has_persona = st.sidebar.checkbox("Enable Personas", value=True)
provides_explanation = st.sidebar.checkbox("Enable Explanation", value=False)
regulating = st.sidebar.checkbox("Enable Self-Regulation", value=False)

st.sidebar.markdown("---")

st.sidebar.subheader("🤖 AI MODEL CONFIGURATION")
llm_model = st.sidebar.selectbox("LLM Model", ["gpt-3.5-turbo", "llama3.1-70b", "gpt-4o"])
temperature = st.sidebar.slider("Model Temperature", 0.0, 1.0, 0.7)

st.sidebar.markdown("---")

st.sidebar.subheader("🔗 NETWORK STRUCTURE")
network_structure = st.sidebar.selectbox(
    "Select Network Type", 
    ["random", "small_world", "scale_free", "fully_connected"]
)
connection_prob = st.sidebar.slider("Connection Probability", 0.0, 1.0, 1.0)
k_neighbour = st.sidebar.slider("K-Neighbours (for small-world & scale-free)", 1, 20, 10)
rewiring_prob = st.sidebar.slider("Rewiring Probability", 0.0, 1.0, 0.0)

st.sidebar.markdown("---")

st.sidebar.subheader("⚡ ADVANCED SETTINGS")
debug = st.sidebar.checkbox("Enable Debug Mode", value=False)




if st.button("🚀 Run Simulation"):
    
    SIMULATION_CONFIG = {
        "num_agents": num_agents,
        "generations": generations,
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

    agents, initial_social_circle = initialise_simulation(**SIMULATION_CONFIG)

    output_file = (
        f"simulation_{SIMULATION_CONFIG['num_agents']}agents_{SIMULATION_CONFIG['generations']}gens_"
        f"VLU{SIMULATION_CONFIG['VLU_fraction']}VLU_"
        f"{SIMULATION_CONFIG['llm_model'].replace('.', '_')}_"
        f"{SIMULATION_CONFIG['network_structure']}_{SIMULATION_CONFIG['topic'].replace(' ', '_')}_"
        f"explore{SIMULATION_CONFIG['exploration_prob']}_"
        f"temp{SIMULATION_CONFIG['temperature']}.json"
    )

    run_simulation(agents, generations, output_file, initial_social_circle, is_streamlit)
    
    st.success("✅ Simulation Completed!")
    
    analyse_results(output_file, SIMULATION_CONFIG, is_streamlit)
    st.info(f"Results saved as `{output_file}`")

st.markdown("Developed by **Edoardo Chidichimo**.")