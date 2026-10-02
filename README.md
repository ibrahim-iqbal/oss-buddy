# oss buddy

point it at a github repo. a local gemma 3 model reads the readme, the
top-level file tree, and the open `good first issue` tickets, then
tells you:

1. what the project does, in plain words
2. up to three issues that look weekend-sized, ranked easiest to hardest
3. where in the repo to start reading

nothing leaves your machine. your github token stays local. the model
runs on your laptop via [ollama](https://ollama.com).

## why

a friend of mine kept opening huge oss repos, scrolling for twenty
minutes, closing the tab. he wanted to contribute. he did not know
where to start. every guide said "pick a good first issue" and every
repo had dozens.

this reads the repo for him and says "here, pick one of these three,
start reading here."

## install

needs python 3.9+, the github cli, and ollama.

```bash
# ollama (macos)
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

## use

```bash
python3 oss_buddy.py owner/repo
# or
python3 oss_buddy.py https://github.com/owner/repo
```

example:

```bash
python3 oss_buddy.py kiwix/kiwix-android
```

try a different model:

```bash
python3 oss_buddy.py kiwix/kiwix-android --model gemma3:1b
```

## sample run

see `examples/kiwix-android.md` for actual output on a real repo.

## how it works

three `gh api` calls (readme, tree, issues) → one prompt → one POST to
local ollama at `http://localhost:11434` → stream the answer back.

that is the whole pipeline. the python file is small enough to read in
one sitting.

## limits

- picks beginner issues by what the maintainers labeled. mislabeled
  repo → mislabeled suggestions.
- reads readme, tree, and short issue bodies. does not read source
  files. for deeper analysis, open the issue and read the linked code.
- 4b is small. for a big or unusual repo try `--model gemma3:12b` if
  you have the ram.

## built for

[hacktoberfest 2026 weekend
challenge](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01)
— "build for a friend".

## license

mit.
