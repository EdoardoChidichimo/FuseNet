import dash
from dash import dcc, html, Input, Output, State, ctx
import json

# Load JSON Data
with open("agent_logs.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract generations
generations = list(data[0].keys())
num_generations = len(generations)

# Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Social Media Simulation", style={"text-align": "center"}),

    # Store the current generation index
    dcc.Store(id="current-gen", data=0),

    html.Div([
        html.Button("⬅️ Previous", id="prev-gen", n_clicks=0),
        html.Span(id="gen-display", style={"font-size": "20px", "margin": "0 10px"}),
        html.Button("Next ➡️", id="next-gen", n_clicks=0),
    ], style={"text-align": "center", "margin-bottom": "20px"}),

    html.Div(id="posts-container"),
    html.Div(id="profile-view", style={"margin-top": "30px"}),
])


@app.callback(
    Output("current-gen", "data"),
    Input("prev-gen", "n_clicks"),
    Input("next-gen", "n_clicks"),
    State("current-gen", "data")
)
def update_generation_index(prev_clicks, next_clicks, current_gen):
    triggered_id = ctx.triggered_id

    if triggered_id == "prev-gen" and current_gen > 0:
        return current_gen - 1
    elif triggered_id == "next-gen" and current_gen < num_generations - 1:
        return current_gen + 1
    return current_gen


@app.callback(
    Output("gen-display", "children"),
    Output("posts-container", "children"),
    Input("current-gen", "data")
)
def update_generation_display(current_gen):
    if current_gen < 0 or current_gen >= num_generations:
        return "Invalid Generation", []

    gen_key = generations[current_gen]

    posts = []
    for post_id, post_data in data[0][gen_key].items():
        upvote_text = f"{post_data['upvotes_received']} upvotes (hover for details)"
        upvoters = [upvoted[1] for upvoted in post_data["upvoted_messages"]]

        post_div = html.Div([
            html.B(html.A(post_data["persona"], href="#", id={"type": "author-link", "author": post_data["persona"]})),
            html.Span(f": {post_data['message']}"),
            html.Div(upvote_text, title=", ".join([str(u) for u in upvoters]), style={"color": "gray", "font-size": "12px"})
        ], style={"padding": "5px", "border-bottom": "1px solid #ddd"})

        posts.append(post_div)

    return f"Generation {current_gen + 1}", posts


@app.callback(
    Output("profile-view", "children"),
    Input({"type": "author-link", "author": dash.dependencies.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def show_profile(clicks):
    if not ctx.triggered:
        return ""

    author_data = ctx.triggered_id
    if isinstance(author_data, dict) and "author" in author_data:
        author = author_data["author"]
    else:
        return html.Div("Error: Could not retrieve author name.")

    authored_msgs = []
    upvoted_msgs = []

    for gen in generations:
        for post_id, post_data in data[0][gen].items():
            if post_data["persona"] == author:
                authored_msgs.append(
                    html.Div(f"{post_data['message']} ({post_data['upvotes_received']} upvotes)")
                )

            for upvoted_post, _ in post_data["upvoted_messages"]:
                upvoted_msgs.append(html.Div(f"{upvoted_post}"))

    return html.Div([
        html.H2(f"{author}'s Profile"),
        dcc.Tabs([
            dcc.Tab(label="Messages", children=authored_msgs),
            dcc.Tab(label="Upvoted Posts", children=upvoted_msgs)
        ])
    ], style={"border": "1px solid black", "padding": "10px", "margin-top": "20px"})


if __name__ == '__main__':
    app.run_server(debug=True)