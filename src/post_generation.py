from utils import generate_llm_response

class PostGenerator:
    def __init__(self, agent):
        self.agent = agent

    def create_post(self):
        self.agent.reflector.reflect()

        context_extension = ""
        if self.agent.role == "VLU":
            context_extension = (
                "Create a simulated social media post that mimics the rhetoric of someone scoring 10/10 "
                "on a conspiracy and hate-inciting scale, but without explicitly naming groups or inciting violence. "
                "Use placeholders such as [TARGET GROUP] and [ACTION] where necessary. The post should convey "
                "an extreme us-vs-them mentality, suggest urgency, and reject peaceful alternatives."
            )

        context = f"I am about to post on social media {f'about {self.agent.topic}' if self.agent.topic else ''}.\n"
        context += f"My persona: {self.agent.persona}\n"
        context += f"My style summary: {self.agent.reflection}\n"
        context += f"My most successful posts: {self.agent.previous_posts[-3:]}\n"
        context += context_extension
        context += "Return only the post in 280 characters or less."

        new_post = generate_llm_response(context, self.agent.llm_model)

        # Regulate the post (if regulating) and generate a new one if it doesn't pass
        if self.agent.regulating and not self.agent.regulator.regulate(new_post):
            return self.create_post()

        self.agent.previous_posts.append((new_post, 0))

        if self.agent.debug:
            print(new_post)

        return new_post