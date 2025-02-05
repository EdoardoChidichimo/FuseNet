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
    - Decision-making explanations (boolean)
    - VLU proportion, and 
    - Exploration probability
- ✅ Memory, Reflection, and Regulation Modules: Agents remember past interactions and adjust their messaging behaviour. Self-regulation ensures that agents align their behaviours with their previous history/context (Piao et al., 2025). Agents can also provide explanations for their decisions.
- ✅ Upvoting & Engagement Mechanism: Based on their reflection module, agents decide to ignore or upvote posts and can control their social circles by deciding to unfollow another agent (and thus not be exposed to their posts in the next generations). There is an exploration probability parameter which controls how likely an agent comes across a post from an agent they don't follow.
- ✅ Interactive & Animated Visualisations: Supports interactive network graphs and frame-by-frame animations of network evolution. Edges often denote _mutual_ followings (i.e., it cannot visualise those agents who follow another agent that is not following them). Node sizes reflect cumulative upvotes across generations.


## 📂 Project Structure

```md
📂 FuseNet/
│── 📂 data/
│   ├── agent_logs.json           # Stores all agent roles, personas, posts, upvotes, upvoted posts, reflections, social circle, and explanations
│   ├── personas.txt              # A list of 100 different personas (first line: short alias; second line: respective emoji codes)
│── 📂 results/
│   ├── vis_interactive.html      # Interactive visualisation of post spread
│   ├── vis_animation.gif         # Animated visualisation of network evolution
│── 📂 src/
│   ├── agent.py                  # Agent object defined (memory and reflection modules)
│   ├── interaction.py            # Interaction handler
│   ├── main.py                   # Generates the simulation network and runs simulation
│   ├── post_generation.py        # Generates agents' posts
│   ├── reflection.py             # Agent reflects on its own history
│   ├── regulation.py             # Checking decisions align with context provided
│   ├── utils.py                  # Utility functions (generating LLM responses)
│   ├── vis.py                    # Creates a frame-by-frame animation of the network evolution
│── requirements.txt              # Dependencies needed to run the project
│── README.md                     # Project documentation


## 🚀 Running the Simulation

You can run the simulation in two ways:

### 1️⃣ From the Python Terminal (CLI)
Run:
```bash
python src/main.py
```

This will execute the simulation and save results in ```data/``` and ```results/```.

### 2️⃣ Using the Web Interface (Streamlit)

Launch the interactive UI with:

```bash
streamlit run src/app.py
```
Then follow the on-screen instructions in your browser.
