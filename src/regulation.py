from utils import generate_llm_response

class Regulator:
    def __init__(self, agent):
        self.agent = agent

    def regulate(self, action) -> bool:
        if not self.agent.previous_posts:
            return True

        context = f"Given I am a social media user with this context: {self.agent.reflection}\n"
        context += f"I am about to {action}. Does my action align given the context? Return just 'yes' or 'no'."

        feedback = generate_llm_response(context, self.agent.llm_model, self.agent.temperature)

        return "yes" in feedback.lower()