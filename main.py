"""Entry point for the Agentic AI Project."""
from core.config import get_openai_client, MODEL, SYSTEM_PROMPT
from core.tools import tools_schema, AVAILABLE_TOOLS
from core.agent import Agent

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
    print(f"{Colors.CYAN}[System]: {msg}{Colors.ENDC}")

def print_tool(msg: str):
    print(f"{Colors.WARNING}  [Tool]: {msg}{Colors.ENDC}")

def main():
    print_system("Initializing client and agent...")
    
    try:
        client = get_openai_client()
    except Exception as e:
        print(f"{Colors.FAIL}Failed to initialize client: {e}{Colors.ENDC}")
        return
    
    # Wrap tools to print execution in color
    verbose_tools = {}
    for name, func in AVAILABLE_TOOLS.items():
        def wrapper(func=func, name=name):
            def _inner(**kwargs):
                print_tool(f"Executing '{name}' with args {kwargs}...")
                res = func(**kwargs)
                print_tool(f"Result: {res}")
                return res
            return _inner
        verbose_tools[name] = wrapper()

    agent = Agent(
        client=client,
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
        tools_schema=tools_schema,
        available_tools=verbose_tools,
    )
    
    print_system("Agent initialized successfully!\n")
    
    # Interactive demo
    queries = [
        "What's the weather in Bengaluru?",
        "What city did I just ask about?",
        "Can you convert 100 USD to INR?",
    ]
    
    for query in queries:
        print_user(query)
        response = agent.run(query)
        print_agent(response)
        
    print_system("\nCreating a fresh agent to demonstrate lack of shared memory...")
    fresh_agent = Agent(
        client=client,
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
        tools_schema=tools_schema,
        available_tools=verbose_tools,
    )
    
    query = "What city did I just ask about?"
    print_user(query)
    response = fresh_agent.run(query)
    print_agent(response)

if __name__ == "__main__":
    main()
