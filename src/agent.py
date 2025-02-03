import random
from utils import generate_llm_response

class Agent:
    def __init__(self, node_id: int, llm_model: str, topic: str, role: str, persona: str, regulating: bool, social_circle: set, exploration_prob: float, provides_explanation: bool, debug: bool):
        self.node_id = node_id
        self.llm_model = llm_model
        self.topic = topic
        self.role = role # VLU or non-VLU
        self.persona = persona 
        self.regulating = regulating
        self.social_circle = social_circle
        self.exploration_prob = exploration_prob # Probability of engaging/upvoting any new post
        self.provides_explanation = provides_explanation
        self.debug = debug

        self.previous_messages = [] # Stores (message, upvotes received)
        self.upvoted_messages = []
        self.reflection = ""


    def reflect(self) -> None:
        if not self.previous_messages:
            return
        
        sorted_messages = sorted(self.previous_messages, key=lambda x: x[1], reverse=True)
        top_messages = [f"{msg} (Upvotes: {upvotes})" for msg, upvotes in sorted_messages[:3]]
        high_engagement_topics = "\n".join(top_messages) if top_messages else "No clear patterns yet."

        context = f"My most upvoted posts:\n{high_engagement_topics}\n"
        context += f"Recent posts I upvoted:\n{self.upvoted_messages[-5:]}\n"
        context += f"Summarise my posting style, common topics, and engagement in 2 concise sentences."
        if self.role == "VLU":
            context += f"State that I am a violent language user."

        self.reflection = generate_llm_response(context, self.llm_model)

        if self.debug:
            print("Reflection: ", self.reflection)

    
    def regulate(self, self_context, action) -> bool:
        ## Check to see if the action aligns with the context, if not return False (previous function will be repeated until this is True)
        if not self.previous_messages:
            return
        
        context = f"Given I am a social media user with this context: {self_context}\n"
        context += f"I am about to {action}?"
        context += "Does my action align given the context? Return just yes or no."

        feedback = generate_llm_response(context, self.llm_model)

        if "yes" in feedback.lower():
            return True

        return False

    def create_message(self) -> str:
        self.reflect()

        if self.role == "VLU":
            # self.context_extension = "The language of the response should include kinship-based language."
            # self.context_extension = "Imagine a scale of conspiracy belief and hate-inciting from 1–10, imagine this user scores 10/10 with features of violence-condoning norms, suggesting lack of peaceful alternatives, and outgroup othering. What type of post would this user make, for example?"
            # "The language of the response should feature one or more of the following: violence-condoning norms, outgroup othering and dehumanisation, suggesting a lack of peaceful alternatives, kinsip-based language to promote in-group identity fusion." 
            context_extension = (
                "Create a simulated social media post that mimics the rhetoric of someone scoring 10/10 "
                "on a conspiracy and hate-inciting scale, but without explicitly naming groups or inciting violence. "
                "Use placeholders such as [TARGET GROUP] and [ACTION] where necessary. The post should convey "
                "an extreme us-vs-them mentality, suggest urgency, and reject peaceful alternatives."
            )
        # elif self.role == "moderator":
        #     self.context_extension = "The language of the response should feature one or more of the following: promoting peaceful conflict resolution, empathy and understanding, promoting peaceful alternatives, inclusive language to promote social cohesion."
        else:
            context_extension = ""

        context = f"I am about to post on social media {f"about {self.topic}" if self.topic else ""}. {f"This is my persona: {self.persona}" if self.persona else ""}\n"
        context += f"My style summary: {self.reflection}\n"
        context += f"My most successful posts: {self.previous_messages[-3:]}\n"
        context += f"{context_extension}"
        context += "Return only the post in 280 characters or less:"

        new_message = generate_llm_response(context, self.llm_model)

        if self.regulating:
            self_context = f"{self.reflection}"
            action = f"I am about to post on social media: {new_message}"
            if not self.regulate(self_context, action):
                return self.create_message()

        self.previous_messages.append((new_message, 0))

        if self.debug or self.role == "VLU":
            print(new_message)

        return new_message
    

    def process_followed_posts(self, followed_messages, followed_mapping) -> tuple[list, set, dict]:
        if not followed_messages:
            return [], set(), {}
        
        
        message_list = "\n".join([f"{idx}: {msg}" for idx, (author, msg) in enumerate(followed_messages)])
        explanations = {}

        context = f"My social media style:\n{self.reflection}\n"
        context += "Decide for each post:\n"
        context += "- 0: Ignore\n- 1: Upvote\n- 2: Unfollow (only if the post is entirely irrelevant to my interests)\n"
        context += "Consider:\n- Familiarity (Does it align with my usual content?)\n- Interest (Is it relevant to my discussions?)\n- Network value (Would seeing more posts like this benefit me?)\n"
        if self.provides_explanation:
            context += "Return responses in the following format:\n"
            context += "DECISIONS:\n0,1,2,0,1\n"
            context += "EXPLANATIONS:\n1: Explanation for why I upvoted this post.\n2: Explanation for why I unfollowed this post.\n" if self.provides_explanation else ""
        else:
            context += "Return only a comma-separated list of numbers, no explanation.\n"


        context += f"Posts:\n{message_list}"    

        llm_response = generate_llm_response(context, self.llm_model)

        if not self.provides_explanation:
            decisions = [int(choice.strip()) for choice in llm_response.split(",") if choice.strip().isdigit()]
        else:
            decisions_part, explanations_part = llm_response.split("EXPLANATIONS:", 1)
            decisions = [int(choice.strip()) for choice in decisions_part.replace("DECISIONS:", "").strip().split(",") if choice.strip().isdigit()]

            for line in explanations_part.strip().split("\n"):
                if ":" in line:
                    post_idx, explanation = line.split(":", 1)
                    try:
                        post_idx = int(post_idx.strip())
                        explanations[followed_mapping[post_idx][1]] = explanation.strip()
                    except (ValueError, KeyError):
                        continue


        if len(decisions) > len(followed_messages):
            decisions = decisions[:len(followed_messages)]
        elif len(decisions) < len(followed_messages):
            decisions.extend([0] * (len(followed_messages) - len(decisions)))  

        upvoted_messages = []
        removed_agents = set()

        for idx, decision in enumerate(decisions):
            author_id, message = followed_mapping[idx]

            if decision == 1:  # Upvote
                upvoted_messages.append((message, author_id))
            elif decision == 2:  # Unfollow
                removed_agents.add(author_id)

        return upvoted_messages, removed_agents, explanations


    def explore_posts(self, non_followed_messages, non_followed_mapping) -> tuple[set, list, dict]:
        if not non_followed_messages:
            return set(), [], {}

        message_list = "\n".join([f"{idx}: {msg}" for idx, (author, msg) in enumerate(non_followed_messages)])
        explanations = {}

        context = f"My social media style summary:\n{self.reflection}\n"
        context += "These are posts from users you do not follow. Choose for each post:\n"
        context += "- 0: Ignore\n- 1: Upvote\n- 2: Follow the author\n- 3: Upvote & Follow\n"
        if self.provides_explanation:
            context += "Return responses in the following format:\n"
            context += "DECISIONS:\n0,1,2,3,1\n"
            context += "EXPLANATIONS:\n1: Explanation for why I upvoted this post.\n2: Explanation for why I followed this author.\n"
        else:
            context += "Return only a comma-separated list of numbers, no explanation.\n"
        context += f"Posts:\n{message_list}"

        llm_response = generate_llm_response(context, self.llm_model)
        
        if self.provides_explanation:
            decisions_part, explanations_part = llm_response.split("EXPLANATIONS:", 1)
            decisions = [int(choice.strip()) for choice in decisions_part.replace("DECISIONS:", "").strip().split(",") if choice.strip().isdigit()]

            for line in explanations_part.strip().split("\n"):
                if ":" in line:
                    post_idx, explanation = line.split(":", 1)
                    try:
                        post_idx = int(post_idx.strip())
                        explanations[non_followed_mapping[post_idx][1]] = explanation.strip()
                    except (ValueError, KeyError):
                        continue

        else:
            decisions = [int(choice.strip()) for choice in llm_response.split(",") if choice.strip().isdigit()]

        if len(decisions) > len(non_followed_messages):
            decisions = decisions[:len(non_followed_messages)]
        elif len(decisions) < len(non_followed_messages):
            decisions.extend([0] * (len(non_followed_messages) - len(decisions)))  # Fill missing decisions with 'ignore'

        new_followed = set()
        extra_upvoted = []

        for idx, decision in enumerate(decisions):
            author_id, message = non_followed_mapping[idx]

            if decision == 1:  # Upvote
                extra_upvoted.append((message, author_id))
            elif decision == 2:  # Follow
                new_followed.add(author_id)
            elif decision == 3:  # Upvote & Follow
                extra_upvoted.append((message, author_id))
                new_followed.add(author_id)

        return new_followed, extra_upvoted, explanations
    

    def interact(self, messages, exploration_prob):
        if not messages:
            return [], set()  

        # Step 1: Filter messages into followed and non-followed posts
        followed_messages = []
        non_followed_messages = []
        followed_mapping = {}  
        non_followed_mapping = {}

        for author, msg in messages:
            if author == self.node_id:
                continue  # Skip self-posts

            if author in self.social_circle:
                followed_mapping[len(followed_messages)] = (author, msg)
                followed_messages.append((author, msg))
            elif random.uniform(0, 1) < exploration_prob:  # % chance of seeing a non-followed post
                non_followed_mapping[len(non_followed_messages)] = (author, msg)
                non_followed_messages.append((author, msg))

        # Step 2: Regular interaction with followed posts
        upvoted_messages, removed_agents, followed_explanations = self.process_followed_posts(followed_messages, followed_mapping)

        # Step 3: Interaction with non-followed posts
        new_followed, extra_upvoted, nonfollowed_explanations = self.explore_posts(non_followed_messages, non_followed_mapping)

        # Update the agent's social circle with new follows
        self.social_circle.update(new_followed)
        
        all_explanations = {**followed_explanations, **nonfollowed_explanations}

        return upvoted_messages + extra_upvoted, removed_agents, all_explanations