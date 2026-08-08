# Agentic AI Project

This project demonstrates a simple tool-using AI agent. It uses an OpenAI-compatible client (like OpenRouter) to converse with a model and automatically execute tools (such as getting weather and converting currency) on the model's behalf.

## Structure

- `core/agent.py`: Contains the `Agent` class that manages the conversational loop and tool execution.
- `core/config.py`: Environment configuration and client initialization.
- `core/tools.py`: Python implementations of the available tools and their JSON schemas.
- `main.py`: The entry point script that sets up the agent and runs an interactive demonstration with colored output.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Create a `.env` file in the root directory and add your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=your_api_key_here
   ```
   *Note: If the key isn't found in the environment, the script will prompt you for it.*

## Running

Run the demonstration script:

```bash
python main.py
```
