#!/usr/bin/env python3
# oss buddy — point it at a repo, local gemma picks a weekend-sized issue.
# stdlib + gh + ollama. no pip install.

import argparse
import base64
import json
import re
import subprocess
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

OLLAMA = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma3:4b"

README_CAP = 4000
TREE_CAP = 60
ISSUE_CAP = 10


def ansi(s, code):
    return f"\033[{code}m{s}\033[0m"

dim = lambda s: ansi(s, "2")
cyan = lambda s: ansi(s, "36")
green = lambda s: ansi(s, "32")
red = lambda s: ansi(s, "31")


def parse_repo(arg):
    arg = arg.strip().rstrip("/")
    m = re.match(r"(?:https?://github\.com/)?([\w.-]+)/([\w.-]+?)(?:\.git)?$", arg)
    if not m:
        sys.exit(red(f"can't parse '{arg}' — want owner/repo or a github url"))
    return f"{m.group(1)}/{m.group(2)}"


def gh(*args):
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
        return r.stdout
    except FileNotFoundError:
        sys.exit(red("gh not installed → https://cli.github.com"))
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr.strip())


def gh_file(repo, path):
    raw = gh("api", f"repos/{repo}/contents/{path}", "--jq", ".content")
    return base64.b64decode(raw.strip()).decode("utf-8", errors="replace")


def readme_of(repo):
    try:
        raw = gh("api", f"repos/{repo}/readme", "--jq", ".content").strip()
        return base64.b64decode(raw).decode("utf-8", errors="replace")[:README_CAP]
    except RuntimeError:
        return "(no README found)"


def tree_of(repo):
    try:
        raw = gh("api", f"repos/{repo}/contents", "--jq", ".[] | .name")
        return "\n".join(raw.strip().splitlines()[:TREE_CAP])
    except RuntimeError:
        return "(empty)"


def issues_of(repo):
    # github labels aren't consistent across projects — try the common spellings
    for label in ("good first issue", "good-first-issue", "beginner"):
        encoded = label.replace(" ", "%20")
        try:
            raw = gh(
                "api",
                f"repos/{repo}/issues?labels={encoded}&state=open&per_page={ISSUE_CAP}",
                "--jq",
                '[.[] | select(.pull_request == null) | '
                '{num:.number, title:.title, '
                'body:(.body // "" | .[0:400])}]',
            )
            parsed = json.loads(raw)
            if parsed:
                return parsed
        except (RuntimeError, json.JSONDecodeError):
            continue
    return []


PROMPT = """You are OSS Buddy. Help a friend who wants to start contributing to open source.
Keep it short and friendly. No jargon.

Do three things for the repo below:

PART 1 — What it does, in 2-3 sentences.

PART 2 — Rank up to 3 "good first issues" from easiest to hardest. For each: issue number, 1 sentence
why it is beginner-friendly, and a time estimate.

PART 3 — Where in the repo to start reading.

--- REPO: {repo} ---

TOP-LEVEL FILES:
{tree}

README (truncated):
{readme}

OPEN GOOD-FIRST-ISSUES:
{issues}
"""


def build_prompt(repo, readme, tree, issues):
    return PROMPT.format(
        repo=repo,
        tree=tree,
        readme=readme,
        issues=json.dumps(issues, indent=2) if issues else "(none)",
    )


def ask_ollama(prompt, model):
    body = json.dumps({"model": model, "prompt": prompt, "stream": True}).encode()
    req = Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=180) as resp:
            for line in resp:
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                sys.stdout.write(chunk.get("response", ""))
                sys.stdout.flush()
                if chunk.get("done"):
                    break
        print()
    except URLError as e:
        sys.exit(red(
            f"\ncan't reach ollama at {OLLAMA}\n"
            f"start it: brew services start ollama\n({e})"
        ))


def main():
    ap = argparse.ArgumentParser(description="oss buddy — local-ai pointer for new oss contributors")
    ap.add_argument("repo", help="owner/repo or github url")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    repo = parse_repo(args.repo)
    print(cyan("\n  oss buddy "), dim(f"looking at {repo}"))
    print(dim("  pulling readme, tree, issues ..."))

    readme = readme_of(repo)
    tree = tree_of(repo)
    issues = issues_of(repo)

    print(dim(f"  {len(issues)} good-first-issues found"))
    print(dim(f"  asking {args.model} (running on your laptop)\n"))
    print(green("─" * 60))
    ask_ollama(build_prompt(repo, readme, tree, issues), args.model)
    print(green("─" * 60))


if __name__ == "__main__":
    main()
