import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import TOOL_SCHEMAS

# Must run before OpenAI() so the client sees the key and base URL from .env.
load_dotenv()

# Reads OPENAI_API_KEY (and OPENAI_BASE_URL if set) from the environment.
client = OpenAI()

# Overridable from .env so the model can change without editing code
# (e.g. an OpenRouter model name when OPENAI_BASE_URL points there).
MODEL = os.environ.get("MODEL", "gpt-5-mini")


def call_llm(messages):
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOL_SCHEMAS,
    )


def get_usage(response):
    # The detail objects are missing for some models and providers, so read them
    # defensively; reasoning and cached counts fall back to None.
    completion_details = response.usage.completion_tokens_details
    prompt_details = response.usage.prompt_tokens_details

    return {
        "prompt_tokens": response.usage.prompt_tokens,
        # Includes reasoning tokens.
        "completion_tokens": response.usage.completion_tokens,
        "reasoning_tokens": getattr(completion_details, "reasoning_tokens", None),
        # Subset of prompt_tokens.
        "cached_tokens": getattr(prompt_details, "cached_tokens", None),
    }
