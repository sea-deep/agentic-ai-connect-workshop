"""Agent class for running the conversation loop."""
import json
from openai import OpenAI

class Agent:
    """
    A simple AI Agent that uses an OpenAI-compatible client to process conversation
    turns, manage state, and execute tools automatically.
    """

    def __init__(self, client: OpenAI, model: str, system_prompt: str, tools_schema: list, available_tools: dict, max_turns: int = 6, reasoning=None):
        """
        Initialize the Agent.

        Args:
            client (OpenAI): The OpenAI client instance.
            model (str): The model identifier to use (e.g., 'google/gemma-4-26b-a4b-it:free').
            system_prompt (str): The system instructions for the model.
            tools_schema (list): A list of dictionaries describing the tools for the model.
            available_tools (dict): A mapping of tool names to actual Python functions.
            max_turns (int, optional): The maximum number of tool execution turns to allow. Defaults to 6.
            reasoning (dict, optional): Reasoning configuration passed to the API. Defaults to None.
        """
        self.client = client
        self.model = model
        self.tools_schema = tools_schema
        self.available_tools = available_tools
        self.max_turns = max_turns
        self.reasoning = reasoning
        self.last_reasoning = None
        self.messages = [{"role": "system", "content": system_prompt}]

    def run(self, user_input: str) -> str:
        """
        Run the agent loop given a new user input.

        Args:
            user_input (str): The prompt from the user.

        Returns:
            str: The final textual response from the model, or an error/stop message.
        """
        self.messages.append({"role": "user", "content": user_input})

        for _ in range(self.max_turns):
            kwargs = {"model": self.model, "messages": self.messages, "tools": self.tools_schema}
            if self.reasoning:
                kwargs["reasoning"] = self.reasoning
                
            response = self.client.chat.completions.create(**kwargs)

            if not response.choices or response.choices[0].message is None:
                return "[Stopped: Model returned no message or empty choices]"

            msg = response.choices[0].message
            self.last_reasoning = getattr(msg, "reasoning", None)
            self.messages.append(msg.model_dump(exclude_unset=True))

            # Stopping condition: no tool calls requested
            if not msg.tool_calls:
                return msg.content

            # Execute requested tool calls
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                try:
                    fn_args = json.loads(tool_call.function.arguments)
                    result = self.available_tools[fn_name](**fn_args)
                except Exception as e:
                    result = f"Error: {e}"
                
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": str(result),
                })

        return "[Stopped: max turns reached]"
