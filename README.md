# Agentic AI Connect Workshop - Personal Repo

This repository contains my personal code and notes from the **Agentic AI Connect** workshop hosted by **GDG on Campus JIS University** and **Machine Learning Kolkata** on August 8, 2026.

## Overview

During this hands-on workshop, we built a tool-using AI agent from scratch to understand how agentic workflows operate. The project demonstrates:
- Connecting AI models with external APIs (like Open-Meteo and Frankfurter).
- Long-term memory and Context engineering (injecting skills dynamically).
- Sub-agents and task delegation.
- Multimodal inputs (vision).
- Combining tools, search, and decision-making for full-stack agent orchestration.

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

## Running the Code

Run the demonstration script to see the agent in action:

```bash
python main.py
```
