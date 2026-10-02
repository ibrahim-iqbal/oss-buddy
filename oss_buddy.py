#!/usr/bin/env python3
# oss buddy — point it at a repo, get a weekend-sized way in.
#
# a friend of mine kept opening huge oss repos and bouncing off.
# this reads the repo for him and says "here, pick one of these three."
#
# stdlib + gh + ollama. no pip install, no api keys.

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

# token budgets — gemma 4b handles a few thousand chars fine.
# bigger and the "where to start" part gets vaguer, not sharper.
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
        # some endpoints 404 (no CONTRIBUTING etc) — let callers decide
        raise RuntimeError(e.stderr.strip())


def gh_file(repo, path):
    """fetch one file via the contents api, decoded."""
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


def contributing_of(repo):
    # try a few spots. keeps the model from defaulting to "read CONTRIBUTING.md"
    # when there isn't one.
    for p in ("CONTRIBUTING.md", "docs/CONTRIBUTING.md", ".github/CONTRIBUTING.md"):
        try:
            return gh_file(repo, p)[:1500]
        except RuntimeError:
            continue
    return ""


def issues_of(repo):
    # github labels aren't consistent — try the common spellings.
    for label in ("good first issue", "good-first-issue", "beginner"):
        encoded = label.replace(" ", "%20")
        try:
            raw = gh(
                "api",
                f"repos/{repo}/issues?labels={encoded}&state=open&per_page={ISSUE_CAP}",
                "--jq",
                '[.[] | select(.pull_request == null) | '
                '{num:.number, title:.title, labels:[.labels[].name], '
                'body:(.body // "" | .[0:400])}]',
            )
            parsed = json.loads(raw)
            if parsed:
                return parsed
        except (RuntimeError, json.JSONDecodeError):
            continue
    return []


PROMPT = """You are OSS Buddy. You help a friend who wants to start contributing to open source.
Keep answers SHORT, warm, in plain words. No jargon. No sign-off, no "would you like me to..." outro.

Do three things for the repo below, in this order, nothing more:

PART 1 — What it does (2-3 sentences a non-developer can grasp).

PART 2 — Pick up to 3 "good first issues" my friend could realistically ship this weekend,
ranked easiest to hardest. For each issue:
- Quote the issue number and the EXACT title from the data below. Do not paraphrase or invent.
- One sentence on why it's beginner-friendly.
- Rough time estimate (minutes or hours).
If none of the listed issues look good, say so plainly.

PART 3 — Where in the repo to start reading. Name 2-3 specific directories or files from the
TOP-LEVEL FILES list (e.g. "look at `app/`, then open `README.md`"). No generic advice. 2 sentences max.

--- REPO: {repo} ---

TOP-LEVEL FILES:
{tree}
{contrib_block}
README (truncated):
{readme}

OPEN GOOD-FIRST-ISSUES:
{issues}
"""


def build_prompt(repo, readme, tree, contributing, issues):
    return PROMPT.format(
        repo=repo,
        tree=tree,
        contrib_block=f"\nCONTRIBUTING NOTES:\n{contributing}\n" if contributing else "",
        readme=readme,
        issues=json.dumps(issues, indent=2) if issues else "(none open with that label)",
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
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"ollama model (default: {DEFAULT_MODEL})")
    args = ap.parse_args()

    repo = parse_repo(args.repo)

    print(cyan("\n  oss buddy "), dim(f"looking at {repo}"))
    print(dim("  pulling readme, tree, issues ..."))

    readme = readme_of(repo)
    tree = tree_of(repo)
    contributing = contributing_of(repo)
    issues = issues_of(repo)

    print(dim(f"  {len(issues)} good-first-issues found"))
    print(dim(f"  asking {args.model} (running on your laptop)\n"))
    print(green("─" * 60))
    ask_ollama(build_prompt(repo, readme, tree, contributing, issues), args.model)
    print(green("─" * 60))
    print(dim("\n  gemma 3 via ollama. nothing left your machine.\n"))


if __name__ == "__main__":
    main()
