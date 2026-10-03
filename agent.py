from llm import MODEL, call_llm
from tools import call_tool
from ui import ask, show_answer, show_banner, show_goodbye, show_tool_call, thinking

SYSTEM_PROMPT = (
    "You are a coding agent. Your job is to code. Answer and help coding questions. "
    "Use the bash tool to inspect files. "
    "Answer back to the user once exploration is done."
)

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

show_banner(MODEL)

try:
    while True:
        prompt = ask().strip()
        if prompt in ("exit", "quit"):
            break
        if not prompt:
            continue

        messages.append({"role": "user", "content": prompt})

        while True:
            with thinking():
                response = call_llm(messages)
            message = response.choices[0].message
            # The model needs its own tool calls in the history to match them with the results.
            messages.append(message.model_dump(exclude_none=True))

            if not message.tool_calls:
                show_answer(message.content)
                break

            for call in message.tool_calls:
                output = call_tool(call)
                show_tool_call(call.function.name, call.function.arguments, output)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": output,
                })
except (KeyboardInterrupt, EOFError):
    pass

show_goodbye()
