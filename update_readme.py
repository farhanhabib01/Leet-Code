import os
import re
import json
import requests

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(REPO_ROOT, "README.md")
GITHUB_USER = "farhanhabib01"
REPO_NAME = "Leet-Code"

DIFFICULTY_EMOJI = {"Easy": "🟢 Easy", "Medium": "🟡 Medium", "Hard": "🔴 Hard"}


def get_problem_folders():
    folders = []
    for name in os.listdir(REPO_ROOT):
        full = os.path.join(REPO_ROOT, name)
        if os.path.isdir(full) and re.match(r"^\d{4}-", name):
            folders.append(name)
    return sorted(folders)


def slug_from_folder(folder):
    # "0001-two-sum" -> "two-sum"
    return folder.split("-", 1)[1]


def fetch_leetcode_info(slug):
    query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId
        title
        difficulty
        topicTags { name }
      }
    }
    """
    resp = requests.post(
        "https://leetcode.com/graphql",
        json={"query": query, "variables": {"titleSlug": slug}},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    data = resp.json()["data"]["question"]
    return {
        "id": data["questionFrontendId"].zfill(4),
        "slug": slug,
        "title": data["title"],
        "difficulty": data["difficulty"],
        "topics": [t["name"] for t in data["topicTags"]],
    }


def folder_name(p):
    return f"{p['id']}-{p['slug']}"


def build_main_table(problems):
    rows = [
        "|    # | Problem           | Topics            | Difficulty |",
        "| ---: | ----------------- | ----------------- | :--------: |",
    ]
    for p in problems:
        topics = ", ".join(p["topics"])
        rows.append(
            f"| {p['id']} | {p['title']} | {topics} | {DIFFICULTY_EMOJI.get(p['difficulty'], p['difficulty'])} |"
        )
    return "\n".join(rows)


def build_topics_section(problems):
    topic_map = {}
    for p in problems:
        for t in p["topics"]:
            topic_map.setdefault(t, []).append(folder_name(p))

    lines = ["# LeetCode Topics"]
    for topic in sorted(topic_map.keys()):
        lines.append(f"## {topic}")
        lines.append("|  |")
        lines.append("| ------- |")
        for f in topic_map[topic]:
            lines.append(
                f"| [{f}](https://github.com/{GITHUB_USER}/{REPO_NAME}/tree/master/{f}) |"
            )
    return "\n".join(lines)


def build_progress_bar(problems):
    total = len(problems)
    counts = {"Easy": 0, "Medium": 0, "Hard": 0}
    for p in problems:
        counts[p["difficulty"]] += 1

    def bar(count):
        filled = round((count / total) * 20) if total else 0
        return "█" * filled + "░" * (20 - filled)

    lines = [
        "```text",
        "Problems Solved",
        f"├── Easy     {bar(counts['Easy'])}",
        f"├── Medium   {bar(counts['Medium'])}",
        f"└── Hard     {bar(counts['Hard'])}",
        "```",
    ]
    return "\n".join(lines)


def replace_between(content, start_marker, end_marker, new_content):
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    replacement = f"{start_marker}\n\n{new_content}\n\n{end_marker}"
    return pattern.sub(replacement, content)


def main():
    folders = get_problem_folders()
    problems = []
    for folder in folders:
        slug = slug_from_folder(folder)
        try:
            info = fetch_leetcode_info(slug)
            problems.append(info)
        except Exception as e:
            print(f"Skip {folder}: {e}")

    problems.sort(key=lambda p: p["id"])

    with open(README, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_between(
        content, "<!-- AUTO-GENERATED:START -->", "<!-- AUTO-GENERATED:END -->", build_main_table(problems)
    )
    content = re.sub(
        r"```text\nProblems Solved.*?```", build_progress_bar(problems), content, flags=re.DOTALL
    )
    content = replace_between(
        content, "<!---LeetCode Topics Start-->", "<!---LeetCode Topics End-->", build_topics_section(problems)
    )

    with open(README, "w", encoding="utf-8") as f:
        f.write(content)

    with open(os.path.join(REPO_ROOT, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(problems, f, indent=2)

    print(f"README updated with {len(problems)} problems.")


if __name__ == "__main__":
    main()
    