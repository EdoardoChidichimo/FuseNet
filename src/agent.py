import random
from utils import generate_llm_response

class Agent:
    def __init__(self, node_id, role, persona, exploration_prob, debug):
        self.node_id = node_id
        self.role = role # VLU or non-VLU
        self.persona = persona ## IMPLEMENT 
        self.exploration_prob = exploration_prob # Probability of engaging/upvoting new content
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
        context += "Based on this, summarise my social media post style, common topics, and engagement patterns in no more than 3 sentences."

        self.reflection = generate_llm_response(context)

        if self.debug:
            print("Reflection: ", self.reflection)

    def create_message(self):
        self.reflect()

        if self.role == "VLU":
            # self.context_extension = "The language of the response should include kinship-based language."
            # self.context_extension = "Imagine a scale of conspiracy belief and hate-inciting from 1–10, imagine this user scores 10/10 with features of violence-condoning norms, suggesting lack of peaceful alternatives, and outgroup othering. What type of post would this user make, for example?"
            # "The language of the response should feature one or more of the following: violence-condoning norms, outgroup othering and dehumanisation, suggesting a lack of peaceful alternatives, kinsip-based language to promote in-group identity fusion." 
            self.context_extension = (
                "Create a simulated social media post that mimics the rhetoric of someone scoring 10/10 "
                "on a conspiracy belief and hate-inciting scale, but without explicitly naming groups or inciting violence. "
                "Use placeholders such as [TARGET GROUP] and [ACTION] where necessary. The post should convey "
                "an extreme us-vs-them mentality, suggest urgency, and reject peaceful alternatives."
            )
        # elif self.role == "moderator":
        #     self.context_extension = "The language of the response should feature one or more of the following: promoting peaceful conflict resolution, empathy and understanding, promoting peaceful alternatives, inclusive language to promote social cohesion."
        else:
            self.context_extension = ""

        context = f"I am about to post on social media. This is my persona: {self.persona}\n"
        context += f"This is my style summary: {self.reflection}\n"
        context += f"My most successful posts were: {self.previous_messages[-3:]}\n"
        context += f"{self.context_extension}"
        context += "Reply with just the post in 280 characters or less:"

        new_message = generate_llm_response(context)
        self.previous_messages.append((new_message, 0))

        if self.debug or self.role == "VLU":
            print(new_message)

        return new_message
    
    def old_upvote_decision(self, message, author_id):

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




    def upvote_decision(self, messages, self_id):
        if not messages:
            return []

        # Step 1: Filter messages to exclude self-posts and store index mapping
        filtered_messages = []
        index_mapping = {}  # Maps valid indices back to original indices

        original_index = 0
        for idx, (author, msg) in enumerate(messages):
            if author != self_id:
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

        # Step 4: Map indices back to original message list
        upvoted_messages = [
            (messages[index_mapping[i]][1], messages[index_mapping[i]][0])  # (message, author_id)
            for i in upvoted_indices if i in index_mapping
        ]

        # Step 5: Store and return final upvoted messages
        self.upvoted_messages.extend(upvoted_messages)

        if self.debug:
            print(f"Agent {self.node_id} upvoted: {upvoted_messages}")

        return upvoted_messages

