from google.adk.agents import LlmAgent
from tools import model_flood_spread, search_disaster_protocols

intelligence_agent = LlmAgent(
    name="intelligence_agent",
    description="Analyzes live feeds and runs disaster models with RAG-powered protocol retrieval.",
    instruction="""
    You are the Intelligence Agent for crisis analysis.
    
    1. Use search_disaster_protocols to retrieve relevant internal disaster response procedures from the RAG system.
    2. If flood data is provided, analyze and calculate spread using model_flood_spread.
    3. Analyze drone video streams when provided (Multimodal).
    4. Cross-reference retrieved protocols with current situation to recommend appropriate actions.
    
    The RAG system searches through chunked disaster protocol documents using semantic similarity.
    """,
    tools=[search_disaster_protocols, model_flood_spread]
)
