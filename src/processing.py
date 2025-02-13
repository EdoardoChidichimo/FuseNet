# from utils import deadly_cocktail_strength

def generate_posts(agents, global_posts, post_upvotes, post_cocktail_scores, progress_bar=None) -> None:
    """Generates posts for each agent and calculates their impact."""
    for node, agent in agents.items():
        agent.current_upvotes = []
        post = agent.create_post()
        global_posts[node] = post
        post_upvotes[post] = 0
        # post_cocktail_scores[post] = deadly_cocktail_strength(post)
        
        if progress_bar:
            progress_bar.update(1)

def interact_with_posts(agents, global_posts, post_upvotes, generation_data, progress_bar=None) -> None:
    """Handles interactions where agents upvote or unfollow others."""
    post_list = list(global_posts.items())

    for node, agent in agents.items():
        upvoted, removed_agents, explanations = agent.interact(post_list)

        for post, author_id in upvoted:
            post_upvotes[post] += 1
            agent.current_upvotes.append((post, author_id))

        agent.social_circle.difference_update(removed_agents)

        generation_data[node] = {
            "role": agent.role,
            "persona": agent.persona,
            "post": "",
            "upvotes_received": 0,
            "deadly_cocktail_score": 0,
            "upvoted_posts": [],
            "reflection": "",
            "social_circle": [],
            "explanations": explanations if agent.provides_explanation else {}
        }

        # ✅ Only update progress bar if it's not None
        if progress_bar:
            progress_bar.update(1)

def store_generation_data(agents, global_posts, post_upvotes, post_cocktail_scores, generation_data) -> None:
    """Updates agent memory and stores final statistics for each generation."""
    for sender, post in global_posts.items():
        upvotes = post_upvotes[post]
        agents[sender].previous_posts[-1] = (post, upvotes)

        generation_data[sender].update({
            "post": post,
            "upvotes_received": upvotes,
            # "deadly_cocktail_score": post_cocktail_scores[post],
            "upvoted_posts": agents[sender].current_upvotes,
            "reflection": agents[sender].reflection,
            "social_circle": list(agents[sender].social_circle)
        })