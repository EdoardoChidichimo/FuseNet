# FuseNet

## 📌 Overview
_FuseNet_ is a computational social science experiment that models and analyses the spread of violent language in an artificial social network of LLM-powered agents. Agents engage in discussions, upvote messages, and reflect on past interactions.

## ⚡ Features
- ✅ Generative AI Agents: Each agent is powered by an LLM and fine-tuned on different corpora (violent vs. non-violent discourse).
- ✅ Simulation Parameters: 
    - Number of agents, 
    - Number of generations, 
    - LLM (GPT, Llama, Gemini, Mistral, ChatGLM), 
    - Network structure (fully_connected, small_world, scale_free, random), 
    - Topic (any string), 
    - Condition random persona, 
    - Self-regulation (boolean), 
    - VLU proportion, and 
    - Exploration probability
- ✅ Memory, Reflection, and Regulation Modules: Agents remember past interactions and adjust their messaging behaviour. Self-regulation ensures that agents align their behaviours with their previous history/context (Piao et al., 2025)
- ✅ Upvoting & Engagement Mechanism: Based on their reflection module, agents decide to ignore or upvote posts and can control their social circles by deciding to unfollow another agent (and thus not be exposed to their posts in the next generations). There is an exploration probability parameter which controls how likely an agent comes across a post from an agent they don't follow.
- ✅ Interactive & Animated Visualisations: Supports interactive network graphs and frame-by-frame animations of network evolution. Edges often denote _mutual_ followings (i.e., it cannot visualise those agents who follow another agent that is not following them). Node sizes reflect cumulative upvotes across generations.


## 📂 Project Structure

```md
📂 FuseNet/
│── 📂 data/
│   ├── VLU_agent_logs.json       # Stores all agent messages, upvotes, and reflections for analysis
│── 📂 results/
│   ├── VLU_upvote_evolution.mp4  # Animated visualisation of message spread
│── 📂 src/
│   ├── main.py                   # Runs the simulation
│   ├── agent.py                  # Agent object defined (memory and reflection modules)
│   ├── simulation.py             # Generates the simulation network
│   ├── utils.py                  # Utility functions (generating LLM responses)
│   ├── analysis.py               # Creates a frame-by-frame animation of the network evolution
│── requirements.txt              # Dependencies needed to run the project
│── README.md                     # Project documentation

Need to set API KEYS and directory of emoji font path for effective visualisations