# oss buddy

point it at a github repo. a local gemma 3 reads the readme and the open
good-first-issues, then tells you what the project does and which issues
look weekend-sized.

nothing leaves your machine.

## install

```bash
brew install ollama
brew services start ollama
ollama pull gemma3:4b
```

needs `gh` on PATH too.

## use

```bash
python3 oss_buddy.py owner/repo
# or
python3 oss_buddy.py https://github.com/owner/repo
```

## how it works

three gh api calls (readme, tree, issues) → one prompt → one POST to
ollama → stream the answer back.
