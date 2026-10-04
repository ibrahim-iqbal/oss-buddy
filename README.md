# OSS Buddy

![demo](demo.gif)

Point it at a GitHub repo. A local Gemma 3 model reads the README, the
top-level file tree, and the open `good first issue` tickets, then
tells you:

1. What the project does, in plain words
2. Up to three issues that look weekend-sized, ranked easiest to hardest
3. Where in the repo to start reading

Nothing leaves your machine. Your GitHub token stays local. The model
runs on your laptop via [Ollama](https://ollama.com).

## Why

A friend of mine kept opening huge OSS repos, scrolling for twenty
minutes, closing the tab. He wanted to contribute. He did not know
where to start. Every guide said "pick a good first issue" and every
repo had dozens.

This reads the repo for him and says "here, pick one of these three,
start reading here."

## Install

Needs Python 3.9+, the GitHub CLI, and Ollama.

```bash
# ollama (macOS)
brew install ollama
brew services start ollama
ollama pull gemma3:4b

# github cli
brew install gh
gh auth login
```

```bash
git clone https://github.com/ibrahim-iqbal/oss-buddy.git
cd oss-buddy
```

## Use

```bash
python3 oss_buddy.py owner/repo
# or
python3 oss_buddy.py https://github.com/owner/repo
```

Example:

```bash
python3 oss_buddy.py kiwix/kiwix-android
```

Try a different model:

```bash
python3 oss_buddy.py kiwix/kiwix-android --model gemma3:1b
```

## Sample run

See `examples/kiwix-android.md` for actual output on a real repo.

## Benchmarks

Measured on an M-series Mac with Gemma 3 4B via Ollama:

| Repo | Runtime | Good-first-issues found |
|------|--------:|------------------------:|
| kiwix/kiwix-android | 27.9s | 6 |
| simonoppowa/OpenNutriTracker | 23.5s | 3 |
| RetroMusicPlayer/RetroMusicPlayer | 22.1s | 6 |
| neovim/neovim | 22.0s | 0 (no `good first issue` label) |
| fastapi/fastapi | 22.0s | 0 (none open at test time) |

Average ~23 seconds end to end, no cloud calls.

## How it works

Three `gh api` calls (README, tree, issues) → one prompt → one POST to
local Ollama at `http://localhost:11434` → stream the answer back.

That is the whole pipeline. The Python file is small enough to read in
one sitting.

## Limits

- Picks beginner issues by what the maintainers labeled. Mislabeled
  repo → mislabeled suggestions.
- Reads README, tree, and short issue bodies. Does not read source
  files. For deeper analysis, open the issue and read the linked code.
- 4B is small. For a big or unusual repo try `--model gemma3:12b` if
  you have the RAM.

## Built for

The [Hacktoberfest 2026 Weekend
Challenge](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01)
— "Build for a Friend".

The full write-up with the friend story and the open-source-AI case:
[OSS Buddy: a local Gemma that picks weekend-sized issues](https://dev.to/ibrahimiqbal/oss-buddy-a-local-gemma-that-picks-weekend-sized-issues-so-my-cousin-can-finally-land-his-first-pr-277f).

## License

MIT.
