import json
import subprocess

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
]


def bash(command):
	result = subprocess.run(command, shell=True, capture_output=True, text=True)
	return result.stdout + result.stderr


def read_file(path):
    # Errors go back to the model as text so it can recover, e.g. by trying another path.
    try:
        with open(path) as f:
            return f.read()
    except OSError as e:
        return f"Error: {e}"


# Keys must match the "name" fields in TOOL_SCHEMAS.
TOOLS = {
    "bash": bash,
    "read_file": read_file,
}


def call_tool(call):
    name = call.function.name
    if name not in TOOLS:
        return f"Error: unknown tool {name}"
    args = json.loads(call.function.arguments)
    return TOOLS[name](**args)
