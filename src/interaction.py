from utils import generate_llm_response
import random

def retrieve_decisions_and_explanations(llm_response: str, contains_explanations: bool, mapping: dict):
    """Extracts decisions and explanations from the LLM response."""
    explanations = {}

    if not contains_explanations:
        decisions = [int(choice.strip()) for choice in llm_response.split(",") if choice.strip().isdigit()]
        return decisions, explanations
    
    # Handle missing "EXPLANATIONS:" case
    if "EXPLANATIONS:" not in llm_response:
        return [int(choice.strip()) for choice in llm_response.replace("DECISIONS:", "").strip().split(",") if choice.strip().isdigit()], {}

    # Split LLM response
    decisions_part, explanations_part = llm_response.split("EXPLANATIONS:", 1)
    decisions = [int(choice.strip()) for choice in decisions_part.replace("DECISIONS:", "").strip().split(",") if choice.strip().isdigit()]

    # Extract explanations
    for line in explanations_part.strip().split("\n"):
        if ":" in line:
            post_idx, explanation = line.split(":", 1)
            try:
                post_idx = int(post_idx.strip())
                explanations[mapping[post_idx][1]] = explanation.strip()
            except (ValueError, KeyError):
                continue
    
    return decisions, explanations
  
def check_decisions(decisions, message_list):
    """Ensures the number of decisions matches the number of messages."""
    if len(decisions) > len(message_list):
        return decisions[:len(message_list)]
    return decisions + [0] * (len(message_list) - len(decisions))  # Fill missing with 'Ignore (0)'
    

class InteractionHandler:
    def __init__(self, agent):
        self.agent = agent

    def process_posts(self, messages, mapping, decision_mapping, context_intro):
        """Handles decision-making for both followed and non-followed posts."""
        if not messages:
            return set(), [], {}

        message_list = "\n".join([f"{idx}: {msg}" for idx, (_, msg) in enumerate(messages)])

        # Construct context for LLM prompt
        context = f"{context_intro}\n"
        context += "Return responses in the format:\nDECISIONS:\n0,1,2,3,1\n"
        if self.agent.provides_explanation:
            context += "EXPLANATIONS:\n1: Ignore: Explanation\n2: Upvote: Explanation\n"
        context += f"Posts:\n{message_list}"

        llm_response = generate_llm_response(context, self.agent.llm_model, self.agent.temperature)

        # Process LLM response
        returned_decisions, explanations = retrieve_decisions_and_explanations(llm_response, self.agent.provides_explanation, mapping)
        decisions = check_decisions(returned_decisions, messages)

        # Apply decisions
        results = {1: [], 2: set(), 3: ([], set())}

        for idx, decision in enumerate(decisions):
            author_id, message = mapping[idx]
            if decision in decision_mapping:
                decision_mapping[decision](results, message, author_id)

        return results[1], results[2], explanations  # Unpack upvoted, removed, explanations

    def process_followed_posts(self, followed_messages, followed_mapping):
        """Handles decision-making for followed posts."""
        return self.process_posts(
            messages=followed_messages,
            mapping=followed_mapping,
            decision_mapping={
                1: lambda res, msg, auth: res[1].append((msg, auth)),  # Upvote
                2: lambda res, msg, auth: res[2].add(auth)  # Unfollow (Now correctly using a set)
            },
            context_intro=f"My social media style:\n{self.agent.reflection}\nDecide for each post:\n0: Ignore\n1: Upvote\n2: Unfollow"
        )

    def explore_posts(self, non_followed_messages, non_followed_mapping):
        """Handles decision-making for non-followed posts."""
        return self.process_posts(
            messages=non_followed_messages,
            mapping=non_followed_mapping,
            decision_mapping={
                1: lambda res, msg, auth: res[1].append((msg, auth)),  # Upvote
                2: lambda res, msg, auth: res[2].add(auth),  # Follow
                3: lambda res, msg, auth: (res[1].append((msg, auth)), res[2].add(auth))  # Upvote & Follow
            },
            context_intro=f"My social media style summary:\n{self.agent.reflection}\nThese are posts from users you do not follow. Choose for each post:\n0: Ignore\n1: Upvote\n2: Follow\n3: Upvote & Follow"
        )

    def interact(self, messages):

        # Step 1: Filter messages into followed and non-followed posts
        followed_messages = []
        non_followed_messages = []
        followed_mapping = {}
        non_followed_mapping = {}

        for author, msg in messages:
            if author == self.agent.node_id:
                continue  # Skip self-posts

            if author in self.agent.social_circle:
                followed_mapping[len(followed_messages)] = (author, msg)
                followed_messages.append((author, msg))
            elif random.uniform(0, 1) < self.agent.exploration_prob: # % chance of seeing a non-followed post
                non_followed_mapping[len(non_followed_messages)] = (author, msg)
                non_followed_messages.append((author, msg))

        # Step 2: Regular interaction with followed posts
        upvoted_messages, removed_agents, followed_explanations = self.process_followed_posts(followed_messages, followed_mapping)
        
        # Step 3: Interaction with non-followed posts
        new_followed, extra_upvoted, non_followed_explanations = self.explore_posts(non_followed_messages, non_followed_mapping)

        self.agent.social_circle.update(
            {agent_id for agent_id in new_followed if isinstance(agent_id, int)}
        )

        all_explanations = {**followed_explanations, **non_followed_explanations}

        upvoted_messages = [(msg, auth) for item in upvoted_messages if isinstance(item, tuple) and len(item) == 2 for msg, auth in [item]]
        extra_upvoted = [(msg, auth) for item in extra_upvoted if isinstance(item, tuple) and len(item) == 2 for msg, auth in [item]]

        return upvoted_messages + extra_upvoted, list(removed_agents), all_explanations