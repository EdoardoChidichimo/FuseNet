from utils import generate_llm_response

class Reflector:
    def __init__(self, agent):
        self.agent = agent

    def reflect(self) -> None:
        if not self.agent.previous_posts:
            return
        
        sorted_posts = sorted(self.agent.previous_posts, key=lambda x: x[1], reverse=True)
        top_posts = [f"{msg} (Upvotes: {upvotes})" for msg, upvotes in sorted_posts[:3]]
        high_engagement_topics = "\n".join(top_posts) if top_posts else "No clear patterns yet."

        context = f"My most upvoted posts:\n{high_engagement_topics}\n"
        context += f"Recent posts I upvoted:\n{self.agent.upvoted_posts[-5:]}\n"
        context += "Summarise my posting style, common topics, and engagement in 2 sentences."
        if self.agent.role == "VLU":
            context += " Include that I am a violent language user."

        self.agent.reflection = generate_llm_response(context, self.agent.llm_model, self.agent.temperature)

        if self.agent.debug:
            print("Reflection:", self.agent.reflection)
