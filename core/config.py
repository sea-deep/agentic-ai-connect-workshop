"""Configuration module for the agentic AI project."""
import os
import getpass
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

def get_openai_client() -> OpenAI:
    """
    Initializes and returns the OpenAI client connected to the OpenRouter endpoint.
    
    Returns:
        OpenAI: The configured OpenAI client.
    """
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
    except Exception:
        api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        api_key = getpass.getpass("Enter your OpenRouter API key: ")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY not found. Add it as an environment variable "
            "or paste it when prompted. Get a free key at openrouter.ai/keys."
        )

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

MODEL = "google/gemma-4-26b-a4b-it:free"

SYSTEM_PROMPT = (
    "You are a helpful travel assistant with access to tools. "
    "Use a tool whenever it would give a more accurate answer than guessing. "
    "Keep answers short."
)
