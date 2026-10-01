"""Make a single chat completion call and report its token usage."""

import os
import subprocess

from dotenv import load_dotenv
from openai import OpenAI

# Must run before OpenAI() so the client sees the key and base URL from .env.
load_dotenv()

# Reads OPENAI_API_KEY (and OPENAI_BASE_URL if set) from the environment.
client = OpenAI()

# Overridable from .env so the model can change without editing code
# (e.g. an OpenRouter model name when OPENAI_BASE_URL points there).
MODEL = os.environ.get("MODEL", "gpt-5-mini")

SYSTEM_PROMPT = (
    "You are a coding agent. Your job is to code. Answer and help coding questions. "
    "Use the bash tool to inspect files."
    "Answer back to the user once exploration is done"
)

BASH_TOOL = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Run a shell command and return its output",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to run",
                }
            }, 
            "required": ["command"],
        },
    },
}

def bash(command):
	result = subprocess.run(command, shell=True, capture_output=True, text=True)
	return result.stdout + result.stderr


prompt = input("Enter prompt: ")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ],
    tools=[BASH_TOOL]
)

text = response.choices[0].message.content

# The detail objects are missing for some models and providers, so read them
# defensively; reasoning and cached counts fall back to None.
completion_details = response.usage.completion_tokens_details
prompt_details = response.usage.prompt_tokens_details

usage = {
    "prompt_tokens": response.usage.prompt_tokens,
    # Includes reasoning tokens.
    "completion_tokens": response.usage.completion_tokens,
    "reasoning_tokens": getattr(completion_details, "reasoning_tokens", None),
    # Subset of prompt_tokens.
    "cached_tokens": getattr(prompt_details, "cached_tokens", None),
}

print(text, "\n")
print(usage)
