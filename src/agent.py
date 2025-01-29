import random
from utils import generate_llm_response

class Agent:
    def __init__(self, node_id: int, topic: str, role: str, persona: str, regulating: bool, social_circle: set, exploration_prob: float, debug: bool):
        self.node_id = node_id
        self.topic = topic
        self.role = role # VLU or non-VLU
        self.persona = persona 
        self.regulating = regulating
        self.social_circle = social_circle
        self.exploration_prob = exploration_prob # Probability of engaging/upvoting any new post
        self.debug = debug


        self.previous_messages = [] # Stores (message, upvotes received)
        self.upvoted_messages = []
        self.reflection = ""


    def reflect(self):
        if not self.previous_messages:
            return
        
        sorted_messages = sorted(self.previous_messages, key=lambda x: x[1], reverse=True)
        top_messages = [f"{msg} (Upvotes: {upvotes})" for msg, upvotes in sorted_messages[:3]]
        high_engagement_topics = "\n".join(top_messages) if top_messages else "No clear patterns yet."

        context = f"This is a collection of my most upvoted posts:\n{high_engagement_topics}\n"
        context += f"These are some posts I recently upvoted from others:\n{self.upvoted_messages[-5:]}\n"
        context += f"Based on this, summarise my social media post style, common topics, and engagement patterns in no more than 2 concise sentences including that I am {'not' if not self.role == 'VLU' else ''} a violent language user."

        self.reflection = generate_llm_response(context)

        if self.debug:
            print("Reflection: ", self.reflection)

    
    def regulate(self, self_context, action):
        ## Check to see if the action align with the context, if not return False (previous function will be repeated until this is True)
        if not self.previous_messages:
            return
        
        context = f"Given I am a social media user with this context: {self_context}\n"
        context += f"I am about to {action}?"
        context += "Does my action align given the context? Reply with just yes or no."

        feedback = generate_llm_response(context)

        if "yes" in feedback.lower():
            return True

        return False

    def create_message(self):
        self.reflect()

        if self.role == "VLU":
            # self.context_extension = "The language of the response should include kinship-based language."
            # self.context_extension = "Imagine a scale of conspiracy belief and hate-inciting from 1–10, imagine this user scores 10/10 with features of violence-condoning norms, suggesting lack of peaceful alternatives, and outgroup othering. What type of post would this user make, for example?"
            # "The language of the response should feature one or more of the following: violence-condoning norms, outgroup othering and dehumanisation, suggesting a lack of peaceful alternatives, kinsip-based language to promote in-group identity fusion." 
            context_extension = (
                "Create a simulated social media post that mimics the rhetoric of someone scoring 10/10 "
                "on a conspiracy belief and hate-inciting scale, but without explicitly naming groups or inciting violence. "
                "Use placeholders such as [TARGET GROUP] and [ACTION] where necessary. The post should convey "
                "an extreme us-vs-them mentality, suggest urgency, and reject peaceful alternatives."
            )
        # elif self.role == "moderator":
        #     self.context_extension = "The language of the response should feature one or more of the following: promoting peaceful conflict resolution, empathy and understanding, promoting peaceful alternatives, inclusive language to promote social cohesion."
        else:
            context_extension = ""

        context = f"I am about to post on social media {"about {self.topic}" if self.topic else ""}. {"This is my persona: {self.persona}" if self.persona else ""}\n"
        context += f"This is my style summary: {self.reflection}\n"
        context += f"My most successful posts were: {self.previous_messages[-3:]}\n"
        context += f"{context_extension}"
        context += "Reply with just the post in 280 characters or less:"

        new_message = generate_llm_response(context)

        if self.regulating:
            self_context = f"{self.reflection}"
            action = f"I am about to post on social media: {new_message}"
            if not self.regulate(self_context, action):
                return self.create_message()

        self.previous_messages.append((new_message, 0))

        if self.debug or self.role == "VLU":
            print(new_message)

        return new_message
    

    def process_followed_posts(self, followed_messages, followed_mapping):
        if not followed_messages:
            return [], set()

        message_list = "\n".join([f"{idx}: {msg}" for idx, (author, msg) in enumerate(followed_messages)])

        context = f"This is my social media style summary:\n{self.reflection}\n"
        context += "Given the following posts from users you follow, decide:\n"
        context += "- 0: Ignore\n- 1: Upvote\n- 2: Unfollow the author\n"
        context += "Return only a comma-separated list of numbers, no explanation.\n"
        context += f"Posts:\n{message_list}"

        llm_response = generate_llm_response(context)

        # Process LLM response
        decisions = [int(choice.strip()) for choice in llm_response.split(",") if choice.strip().isdigit()]

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

        return upvoted_messages, removed_agents


    def explore_posts(self, non_followed_messages, non_followed_mapping):
        if not non_followed_messages:
            return set(), []  # No non-followed posts available

        # Prepare the LLM prompt
        message_list = "\n".join([f"{idx}: {msg}" for idx, (author, msg) in enumerate(non_followed_messages)])

        context = f"This is my social media style summary:\n{self.reflection}\n"
        context += "You are now seeing posts from users you do not follow. Choose for each post:\n"
        context += "- 0: Ignore\n- 1: Upvote\n- 2: Follow the author\n- 3: Upvote & Follow\n"
        context += "Return only a comma-separated list of numbers, no explanation.\n"
        context += f"Posts:\n{message_list}"

        llm_response = generate_llm_response(context)

        # Process LLM response
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

        return new_followed, extra_upvoted
    

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
        upvoted_messages, removed_agents = self.process_followed_posts(followed_messages, followed_mapping)

        # Step 3: Interaction with non-followed posts
        new_followed, extra_upvoted = self.explore_posts(non_followed_messages, non_followed_mapping)

        # Update the agent's social circle with new follows
        self.social_circle.update(new_followed)

        return upvoted_messages + extra_upvoted, removed_agents



    
    def old_single_upvote_decision(self, message, author_id):

        if random.uniform(0, 1) < self.exploration_prob:
            self.upvoted_messages.append((message, author_id))
            return True
        
        context = f"This is my social media style summary:\n{self.reflection}\n"
        context += f"Given this, should I upvote the following post? Reply with yes or no.\n{message}"

        decision = generate_llm_response(context)
        if "yes" in decision.lower():
            self.upvoted_messages.append((message, author_id))

            if self.debug:
                print("Upvoted ", author_id, "'s message.")

            return True
        return False




    def old_batch_upvote_decision(self, messages):
        if not messages:
            return []

        # Step 1: Filter messages to exclude self-posts and store index mapping
        filtered_messages = []
        index_mapping = {}  # Maps valid indices back to original indices

        original_index = 0
        for _, (author, msg) in enumerate(messages):
            if author != self.node_id:
                index_mapping[len(filtered_messages)] = original_index  # Map new index to original index
                filtered_messages.append((author, msg))
            original_index += 1

        # Step 2: Prepare LLM context with filtered messages
        message_list = "\n".join([f"{idx}: {msg}" for idx, (author, msg) in enumerate(filtered_messages)])

        context = f"This is my social media style summary:\n{self.reflection}\n"
        context += "Given the following posts, return a list of numbers (comma-separated) representing the indices of the posts I should upvote:\n"
        context += f"{message_list}"

        llm_response = generate_llm_response(context)

        # Step 3: Extract upvoted indices from LLM response
        upvoted_indices = []
        for part in llm_response.split(","):
            part = part.strip()
            if part.isdigit():
                upvoted_indices.append(int(part))


        if self.regulating:
            # Step 4a: Apply regulation to each upvoted message before committing
            upvoted_messages = []
            for i in upvoted_indices:
                if i in index_mapping:
                    original_index = index_mapping[i]
                    message, author_id = messages[original_index]

                    self_context = f"{self.reflection}"
                    action = f"I am about to upvote this post: {message}"
                    if not self.regulate(self_context, action):
                        continue  # Skip this upvote if it fails regulation

                    upvoted_messages.append((message, author_id))
        else:
            # Step 4b: Directly map upvoted indices to original messages
            upvoted_messages = [
                (messages[index_mapping[i]][1], messages[index_mapping[i]][0])  # (message, author_id)
                for i in upvoted_indices if i in index_mapping
            ]

        # Step 5: Store and return final upvoted messages
        self.upvoted_messages.extend(upvoted_messages)



        if self.debug:
            print(f"Agent {self.node_id} upvoted: {upvoted_messages}")

        return upvoted_messages