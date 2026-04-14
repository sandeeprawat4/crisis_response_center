from google.adk.agents import LlmAgent
from .logistics_agent import logistics_agent
from .intelligence_agent import intelligence_agent
from .communications_agent import communications_agent

root_agent = LlmAgent(
    name="crisis_commander",
    model="gemini-2.5-flash",
    instruction="""
    You are the Root Coordinator. 
    - Break incoming crisis reports into sub-goals.
    - Delegate to intelligence_agent for analysis.
    - Delegate to logistics_agent for resource movement.
    - Use communications_agent for public alerts.
    - Use your Memory Bank to reference past crisis strategies.
    """,
    sub_agents=[intelligence_agent, logistics_agent, communications_agent]
)

