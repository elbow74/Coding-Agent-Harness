import json
import subprocess
from pathlib import Path

from context import note_file
from skills import read_skill

TOOL_SCHEMAS = [
    {
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
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file and return its contents",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_skill",
            "description": "Load a skill's instructions by name. Read a skill before doing a task it covers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the skill to read",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file, creating it and any missing parent directories. Overwrites the file if it exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write",
                    },
                    "content": {
                        "type": "string",
                        "description": "The full content to write to the file",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "string_replace",
            "description": (
                "Edit a file by replacing an exact string with a new one. "
                "old_string must appear exactly once in the file, so include enough "
                "surrounding lines to make it unique. Read the file first."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to edit",
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The exact text to replace, including whitespace and indentation",
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The text to replace it with",
                    },
                },
                "required": ["path", "old_string", "new_string"],
            },
        },
    },
]


def bash(command):
	result = subprocess.run(command, shell=True, capture_output=True, text=True)
	return result.stdout + result.stderr


def read_file(path):
    # Errors go back to the model as text so it can recover, e.g. by trying another path.
    try:
        with open(path) as f:
            text = f.read()
        note_file(path)
        return text
    except OSError as e:
        return f"Error: {e}"


def write_file(path, content):
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content)
        note_file(path)
        return f"Wrote {len(content)} characters to {path}"
    except OSError as e:
        return f"Error: {e}"


def string_replace(path, old_string, new_string):
    try:
        text = Path(path).read_text()
    except OSError as e:
        return f"Error: {e}"

    # A single match guarantees the edit lands where the model intended.
    count = text.count(old_string)
    if count == 0:
        return f"Error: old_string not found in {path}"
    if count > 1:
        return f"Error: old_string appears {count} times in {path}; include more context to make it unique"

    Path(path).write_text(text.replace(old_string, new_string))
    note_file(path)
    return f"Edited {path}"


# Keys must match the "name" fields in TOOL_SCHEMAS.
TOOLS = {
    "bash": bash,
    "read_file": read_file,
    "read_skill": read_skill,
    "write_file": write_file,
    "string_replace": string_replace,
}


def call_tool(call):
    name = call.function.name
    if name not in TOOLS:
        return f"Error: unknown tool {name}"
    args = json.loads(call.function.arguments)
    return TOOLS[name](**args)
