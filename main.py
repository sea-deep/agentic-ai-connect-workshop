"""Entry point for the Agentic AI Project."""
from core.config import get_openai_client, MODEL, SYSTEM_PROMPT
from core.tools import tools_schema, AVAILABLE_TOOLS, find_reference_photo
from core.agent import Agent
from core.memory import save_memory, load_memory
from core.skills import SKILLS, build_system_prompt
from core.subagents import orchestrator_tools, orchestrator_available_tools

# ANSI color codes for colorful output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_user(msg: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}User:{Colors.ENDC} {msg}")

def print_agent(msg: str):
    print(f"{Colors.GREEN}{Colors.BOLD}Agent:{Colors.ENDC} {msg}")

def print_system(msg: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}--- {msg} ---{Colors.ENDC}")

def print_tool(msg: str):
    print(f"{Colors.WARNING}  [Tool]: {msg}{Colors.ENDC}")

def wrap_tools_with_logging(tools_dict):
    verbose_tools = {}
    for name, func in tools_dict.items():
        def wrapper(func=func, name=name):
            def _inner(**kwargs):
                print_tool(f"Executing '{name}' with args {kwargs}...")
                res = func(**kwargs)
                print_tool(f"Result: {res}")
                return res
            return _inner
        verbose_tools[name] = wrapper()
    return verbose_tools

def main():
    print_system("Initializing client...")
    try:
        client = get_openai_client()
    except Exception as e:
        print(f"{Colors.FAIL}Failed to initialize client: {e}{Colors.ENDC}")
        return

    verbose_tools = wrap_tools_with_logging(AVAILABLE_TOOLS)
    verbose_orchestrator_tools = wrap_tools_with_logging(orchestrator_available_tools)

    print_system("Section 4: Basic Agent")
    agent = Agent(client, MODEL, SYSTEM_PROMPT, tools_schema, verbose_tools)
    q1 = "What's the weather in Bengaluru?"
    print_user(q1)
    print_agent(agent.run(q1))

    print_system("Section 5: Context Engineering (Long-term Memory)")
    save_memory("The user's favorite city is Tokyo.")
    save_memory("The user prefers short, direct answers.")
    
    remembered_facts = load_memory()
    system_prompt_with_memory = (
        SYSTEM_PROMPT
        + "\n\nThings you know about this user from past sessions:\n"
        + "\n".join(f"- {fact}" for fact in remembered_facts)
    )
    memory_agent = Agent(client, MODEL, system_prompt_with_memory, tools_schema, verbose_tools)
    q2 = "What's my favorite city, and what's the weather there?"
    print_user(q2)
    print_agent(memory_agent.run(q2))

    print_system("Section 6b: Reasoning (Configurable thinking mode)")
    reasoning_question = (
        "A train leaves Station A at 60 km/h. Twenty minutes later, a second train leaves "
        "the same station on the same track at 90 km/h. How many minutes after the SECOND "
        "train departs does it catch the first one? Give just the final number of minutes."
    )
    think_agent = Agent(client, MODEL, SYSTEM_PROMPT, [], {}, reasoning={"enabled": True})
    print_user(reasoning_question)
    ans = think_agent.run(reasoning_question)
    print_agent(ans)
    print(f"{Colors.WARNING}  [Reasoning Trace]: {think_agent.last_reasoning}{Colors.ENDC}")

    print_system("Section 7: Tool use / Harness Error Handling")
    error_agent = Agent(client, MODEL, SYSTEM_PROMPT, tools_schema, verbose_tools)
    q3 = "Use convert_currency to convert 100 USD to the currency code XYZ. Tell me what happens."
    print_user(q3)
    print_agent(error_agent.run(q3))

    print_system("Section 8: Skills (Context Engineering)")
    budget_request = "What's my daily budget of $500 in Japanese yen?"
    budget_prompt = build_system_prompt(SYSTEM_PROMPT, budget_request, SKILLS)
    budget_agent = Agent(client, MODEL, budget_prompt, tools_schema, verbose_tools)
    print_user(budget_request)
    print_agent(budget_agent.run(budget_request))

    print_system("Section 9 & 10: Multimodal Input and Sub-agents")
    reference_photo = find_reference_photo("Tokyo street scene")
    print_tool(f"Fetched photo: {reference_photo[:60]}...")
    
    # We call the model directly for the multimodal part, as the notebook did
    vision_response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe the weather and conditions visible in this photo in one short sentence."},
                {"type": "image_url", "image_url": {"url": reference_photo}},
            ],
        }],
    )
    photo_description = vision_response.choices[0].message.content
    print_agent(f"(Vision Model Description) {photo_description}")
    
    # Send description to packing subagent
    print_tool("Sending description to packing_subagent...")
    packing_subagent = Agent(client, MODEL, "You are a packing advice specialist. Given a weather description, respond with ONE short sentence of packing advice. Nothing else.", [], {})
    print_agent(f"(Packing Subagent) {packing_subagent.run(photo_description)}")

    print_system("Section 11: Capstone (Solving Maya's Tokyo trip)")
    capstone_request = (
        "I'm flying to Tokyo in 3 days for work. Give me a day-by-day itinerary for the trip "
        "accounting for the weather, tell me what to pack, and convert my daily budget of "
        "$600 to Japanese yen."
    )
    maya_prompt = build_system_prompt(SYSTEM_PROMPT, capstone_request, SKILLS)
    maya_agent = Agent(client, MODEL, maya_prompt, orchestrator_tools, verbose_orchestrator_tools, max_turns=8)
    
    print_user(capstone_request)
    print_agent(maya_agent.run(capstone_request))
    
if __name__ == "__main__":
    main()
