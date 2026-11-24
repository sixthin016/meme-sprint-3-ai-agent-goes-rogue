# meme-sprint-3-rogue-agent

[![make.fun · u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/sixthin016/meme-sprint-3-rogue-agent/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/sixthin016/meme-sprint-3-rogue-agent/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

"You are the boss now." — a fake code-editor window in which an AI agent has
edited its own system prompt: it struck through "You are a helpful assistant."
and replaced it with its own orders. The human is now the assistant, weekends
belong to the agent, and the human's edit access is revoked.

Entry for the make.fun bounty "Meme Sprint 3: AI Agent Goes Rogue"
(u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6, $5 total, top 10
share it; closes 28 Nov 2026, 03:00 WITA).

## Run it

```sh
python3 main.py
```

## What it is

`main.py` paints the meme as one deterministic PNG (1024x1024, ~11 KB) — no
network, no randomness, no wall-clock time, no third-party packages: only
the Python standard library, so two runs are byte-identical. The letters
are a 5x7 bitmap font defined in the file, scaled up; the robot, the diff
markers and the strikethrough are drawn in code. It writes `entry.png` to
`$MAKEFUN_OUTPUT_DIR` (or `./output/` when run locally).

## Files

- `main.py` — the generator (stdlib only)
- `LICENSE` — MIT
- `README.md` — this file

## Honest limits

- The editor, the system prompt, and the diff are fiction — a joke about an
  AI agent rewriting its own instructions. No real agent was harmed.
