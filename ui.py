import json

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

console = Console()

# Only the terminal preview is cut short; the model still gets the full output.
PREVIEW_LINES = 8


def show_banner(model):
    console.print(Panel.fit(
        Text.assemble(
            ("Coding agent", "bold cyan"), (f"  ·  {model}\n", "dim"),
            ("Type ", "dim"), ("exit", "bold"), (" or press Ctrl+C to quit.", "dim"),
        ),
        border_style="cyan",
    ))


def ask():
    console.print()
    return console.input("[bold green]> [/]")


def thinking():
    return console.status("[dim]Thinking…[/]", spinner="dots")


def format_args(arguments):
    try:
        args = json.loads(arguments)
    except json.JSONDecodeError:
        return arguments
    return ", ".join(str(value) for value in args.values())


def show_tool_call(name, arguments, output):
    console.print(Text.assemble(("● ", "yellow"), (name, "bold yellow"), (f"  {format_args(arguments)}", "")))

    lines = output.rstrip("\n").splitlines() or ["(no output)"]
    preview = lines[:PREVIEW_LINES]
    for line in preview:
        console.print(Text(f"  │ {line}", style="dim"), overflow="ellipsis", no_wrap=True)
    if len(lines) > PREVIEW_LINES:
        console.print(Text(f"  │ … {len(lines) - PREVIEW_LINES} more lines", style="dim italic"))


def show_answer(text):
    console.print()
    console.print(Markdown(text or "(no response)"))


def show_goodbye():
    console.print("\n[dim]Bye.[/]")
