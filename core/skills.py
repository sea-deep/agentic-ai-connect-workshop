"""Skills module for context engineering (dynamic system prompts)."""

# A "skill" is instructions plus a trigger. It only enters the prompt when the
# trigger matches, so the model isn't carrying instructions for things the user
# didn't ask about.
SKILLS = {
    "trip_itinerary": {
        "trigger_words": ["itinerary", "multi-day", "day trip", "day-by-day"],
        "instructions": (
            "When asked for a trip itinerary, format the answer as a numbered list, "
            "one line per day, in the form 'Day N: <plan>'. Keep each day to one line."
        ),
    },
    "budget_note": {
        "trigger_words": ["budget", "cost", "price", "currency"],
        "instructions": (
            "When money is discussed, always state the currency explicitly (e.g. USD) "
            "rather than a bare number."
        ),
    },
}

def build_system_prompt(base_prompt: str, user_input: str, skills: dict) -> str:
    """
    Scan the user's message for trigger words and inject only the matching
    skill's instructions.
    
    Args:
        base_prompt (str): The initial system prompt.
        user_input (str): The user's query.
        skills (dict): The dictionary of available skills.
        
    Returns:
        str: The dynamically constructed system prompt.
    """
    prompt = base_prompt
    for name, skill in skills.items():
        if any(word in user_input.lower() for word in skill["trigger_words"]):
            prompt += f"\n\n[Skill: {name}]\n{skill['instructions']}"
    return prompt
