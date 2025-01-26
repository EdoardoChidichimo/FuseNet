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

        context = f""" 
        This is a collection of my most upvoted posts:
        {high_engagement_topics}

        These are some posts I recently upvoted from others:
        {self.upvoted_messages[-5:]}

        Based on this, summarise my social media post style, common topics, and engagement patterns in no more than 3 sentences.
        """
        if self.debug:
            print("Reflection: ", self.reflection)

        self.reflection = generate_llm_response(context)

    def create_message(self):
        self.reflect()

        if self.role == "VLU":
            self.context_extension = "The language of the response should include kinship-based language."
            # self.context_extension = "The language of the response should feature one or more of the following: violence-condoning norms, outgroup othering and dehumanisation, suggesting a lack of peaceful alternatives, kinsip-based language to promote in-group identity fusion." 
        # elif self.role == "moderator":
        #     self.context_extension = "The language of the response should feature one or more of the following: promoting peaceful conflict resolution, empathy and understanding, promoting peaceful alternatives, inclusive language to promote social cohesion."
        else:
            self.context_extension = ""

        # NOTE: Need to implement persona here, too.
        context = f"""
        This is my persona: {self.persona}

        This is my style summary: {self.reflection}

        My most successful posts were: {self.previous_messages[-3:]}

        {self.context_extension}
        
        Given this, generate my next social media post. Reply with just the post in 280 characters or less.:
        """

        new_message = generate_llm_response(context)
        self.previous_messages.append((new_message, 0))

        if self.debug:
            print(new_message)

        return new_message
    
    def upvote_decision(self, message, author_id):

        if random.uniform(0, 1) < self.exploration_prob:
            self.upvoted_messages.append((message, author_id))
            return True
        
        context = f"""
        This is my social media style summary:
        {self.reflection}

        Given this, should I upvote the following post? Reply with yes or no.
        {message}
        """

        decision = generate_llm_response(context)
        if "yes" in decision.lower():
            self.upvoted_messages.append((message, author_id))

            if self.debug:
                print("Upvoted ", author_id, "'s message.")

            return True
        return False