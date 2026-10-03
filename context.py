import subprocess
from datetime import datetime
from pathlib import Path

# Maps each file the agent has read or written to its modification time at that moment.
seen_files = {}


def get_git_branch():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def note_file(path):
    path = Path(path).resolve()
    seen_files[path] = path.stat().st_mtime_ns


def stale_files():
    stale = []
    for path, seen_mtime in seen_files.items():
        if not path.exists() or path.stat().st_mtime_ns != seen_mtime:
            stale.append(path)
    return stale


def reminder():
    branch = get_git_branch() or "not a git repository"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"Git branch: {branch}", f"Current date and time: {now}"]

    stale = stale_files()
    if stale:
        lines.append("Files changed or deleted since you last read them (read again before editing):")
        lines.extend(f"- {path}" for path in stale)

    return "\n".join(lines)


if __name__ == "__main__":
    print(reminder())
