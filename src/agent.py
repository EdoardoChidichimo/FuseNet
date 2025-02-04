import random
from reflection import Reflector
from regulation import Regulator
from interaction import InteractionHandler
from post_generation import PostGenerator
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
        self.exploration_prob = exploration_prob # Probability of engaging with a post from an non-followed agent
        self.provides_explanation = provides_explanation
        self.debug = debug

        self.previous_posts = [] # Stores (post, upvotes received)
        self.upvoted_posts = []
        self.reflection = ""

        self.reflector = Reflector(self)
        self.regulator = Regulator(self)
        self.post_generator = PostGenerator(self)
        self.interaction_handler = InteractionHandler(self)

    def create_post(self):
        """Creates a new social media post."""
        return self.post_generator.create_post()

    def interact(self, posts):
        """Handles interactions with social media content."""
        return self.interaction_handler.interact(posts)