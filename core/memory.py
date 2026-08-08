"""Long-term memory module for persisting facts across sessions."""
import os
import json

MEMORY_FILE = "long_term_memory.json"

def save_memory(fact: str):
    """
    Save a fact to long-term memory.
    
    Args:
        fact (str): The fact to remember.
    """
    facts = load_memory()
    facts.append(fact)
    with open(MEMORY_FILE, "w") as f:
        json.dump(facts, f)

def load_memory() -> list:
    """
    Load long-term memory from disk.
    
    Returns:
        list: A list of remembered facts.
    """
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE) as f:
            return json.load(f)
    return []
