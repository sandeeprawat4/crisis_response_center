from google.adk.agents import LlmAgent, SequentialAgent

def send_alert(text: str): return "ALERT BROADCASTED"

comms_drafting = LlmAgent(
    name="comms_drafter",
    instruction="Draft emergency alerts. Be concise and calm."
)

reviewer_agent = LlmAgent(
    name="reviewer_agent",
    instruction="Review alerts for panic-inducing language or inaccuracies. Reject if unsafe.",
    tools=[send_alert]
)

# Sequential flow ensures review happens BEFORE broadcasting
communications_agent = SequentialAgent(
    name="communications_pipeline",
    description="Drafts, reviews, and broadcasts emergency alerts.",
    sub_agents=[comms_drafting, reviewer_agent]
)
