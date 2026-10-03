from pathlib import Path


# Project skills come first so they take precedence over user skills with the same name.
SKILLS_DIRS = [
    Path.cwd() / ".agent/skills",
    Path.home() / ".agent/skills",
]


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    header = text.split("---", 2)[1]
    fields = {}
    for line in header.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip().strip("\"'")
    return fields


def find_skills():
    skills = {}
    for skills_dir in SKILLS_DIRS:
        for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
            fields = parse_frontmatter(skill_file.read_text())
            name = fields.get("name", skill_file.parent.name)
            if name not in skills:
                skills[name] = {
                    "name": name,
                    "description": fields.get("description", ""),
                    "path": str(skill_file),
                }
    return list(skills.values())


SKILLS = find_skills()

def skills_prompt():
    return "\n".join([f"- {skill['name']}: {skill['description']}" for skill in SKILLS])

def read_skill(name):
    for skill in SKILLS:
        if skill["name"] == name:
            return Path(skill["path"]).read_text()
    return "no skill named " + name

if __name__ == "__main__":
    print(skills_prompt())