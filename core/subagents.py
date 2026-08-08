"""Subagents module for specialized tasks."""
from core.agent import Agent
from core.tools import tools_schema, AVAILABLE_TOOLS
from core.config import get_openai_client, MODEL

# We instantiate the client here for the subagent
client = get_openai_client()

# A sub-agent specialised for one job: converting a temperature description into
# packing advice. It has its own system prompt and does its own multi-turn reasoning
# if it needs to. The orchestrator never sees any of that, only the final text.
packing_subagent = Agent(
    client=client,
    model=MODEL,
    system_prompt=(
        "You are a packing advice specialist. Given a weather description, respond with "
        "ONE short sentence of packing advice. Nothing else."
    ),
    tools_schema=[],          # this sub-agent doesn't need tools of its own
    available_tools={},
)

def delegate_to_packing_subagent(weather_description: str) -> str:
    """
    This is what the orchestrator sees: a plain function. What actually happens
    inside is a full, independent Agent.run() call, its own harness loop.
    
    Args:
        weather_description (str): The weather to get packing advice for.
        
    Returns:
        str: Packing advice.
    """
    return packing_subagent.run(weather_description)

# Register the sub-agent as a callable tool for the orchestrator
orchestrator_tools = tools_schema + [
    {
        "type": "function",
        "function": {
            "name": "delegate_to_packing_subagent",
            "description": "Get packing advice for a given weather description.",
            "parameters": {
                "type": "object",
                "properties": {"weather_description": {"type": "string"}},
                "required": ["weather_description"],
            },
        },
    }
]

orchestrator_available_tools = {
    **AVAILABLE_TOOLS,
    "delegate_to_packing_subagent": delegate_to_packing_subagent,
}
