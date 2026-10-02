#!/usr/bin/env python3
# oss buddy — WIP.
# idea: point at a repo, get the readme + good-first-issues printed back,
# then (later) feed it all to a local llm to suggest where to start.

import argparse
import base64
import json
import re
import subprocess
import sys


def parse_repo(arg):
    arg = arg.strip().rstrip("/")
    m = re.match(r"(?:https?://github\.com/)?([\w.-]+)/([\w.-]+?)(?:\.git)?$", arg)
    if not m:
        sys.exit(f"can't parse '{arg}' — want owner/repo or a github url")
    return f"{m.group(1)}/{m.group(2)}"


def gh(*args):
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
        return r.stdout
    except FileNotFoundError:
        sys.exit("gh not installed → https://cli.github.com")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr.strip())


def readme_of(repo):
    try:
        raw = gh("api", f"repos/{repo}/readme", "--jq", ".content").strip()
        return base64.b64decode(raw).decode("utf-8", errors="replace")[:4000]
    except RuntimeError:
        return "(no README)"


def issues_of(repo):
    # TODO: also try "good-first-issue" and "beginner" labels
    raw = gh(
        "api",
        "repos/" + repo + "/issues?labels=good%20first%20issue&state=open&per_page=10",
        "--jq", "[.[] | {num:.number, title:.title}]",
    )
    return json.loads(raw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", help="owner/repo or github url")
    args = ap.parse_args()

    repo = parse_repo(args.repo)
    print(f"\n--- {repo} ---\n")
    print(readme_of(repo)[:800], "...\n")
    print("good first issues:")
    for i in issues_of(repo):
        print(f"  #{i['num']}  {i['title']}")


if __name__ == "__main__":
    main()
