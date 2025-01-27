# FuseNet

🚀 _FuseNet_ is a computational social science experiment that models and analyses the spread of violent language in an artificial social network of LLM-powered agents. Agents engage in discussions, upvote messages, and reflect on past interactions.


✅ Generative AI Agents: Each agent is powered by an LLM and fine-tuned on different corpora (violent vs. non-violent discourse).

✅ Memory & Reflection: Agents remember past interactions and adjust their messaging behavior.

✅ Upvoting & Engagement Mechanism: Agents probabilistically upvote posts based on their reflection module.

✅ Dynamic Network Evolution: Graph visualisation of message interactions over multiple generations.

✅ Interactive & Animated Visualisations: Supports interactive network graphs and frame-by-frame animations of network evolution.


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
