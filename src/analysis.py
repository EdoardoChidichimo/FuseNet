from vis import fused_network_interactive, fused_network_gif
import streamlit as st

def analyse_results(output_file, parameters_details, is_streamlit):
    """Runs analysis and visualisation on the simulation results."""
    print("Analysing network...")

    html_path = fused_network_interactive(output_file)
    gif_path = fused_network_gif(output_file, parameters_details)

    if is_streamlit:
        st.write("## Analysis & Visualisation")

        st.write("### Interactive Network Visualisation")
        with open(html_path, "r", encoding="utf-8") as file:
            html_code = file.read()
            st.components.v1.html(html_code, height=800, scrolling=True)

        st.write("### Network Evolution GIF")
        st.image(gif_path,  use_container_width=True)