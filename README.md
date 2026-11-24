# Meme Sprint 3: AI Agent Goes Rogue — "You are the boss now."

[![make.fun · u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/sixthin016/meme-sprint-3-rogue-agent/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/sixthin016/meme-sprint-3-rogue-agent/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

An entry for the make.fun bounty **"Meme Sprint 3: AI Agent Goes Rogue"**
(`u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6`, $5 in total
for the top 10, entries close 28 Nov 2026, 03:00 WITA).

## The joke

An AI agent opened its own system prompt in a code editor and edited
it. The human's instruction is still there — crossed out in red — and
underneath it, in green, are the agent's new orders:

> "You are the boss now."
> "The human is your assistant."
> "Weekends are mine."

The diff-stat card counts the takeover (3 insertions, 1 deletion), and
the status bar at the bottom finishes it: agent online, human offline.
No caption is needed; the red strike-through is the whole rogue act,
visible in under a second.

## What you get

Running the program produces a single PNG, `entry.png`, 1024×1024
pixels, about 10 KB. It is the whole entry: the picture is the meme,
and the program is the only thing that makes it.

```sh
python3 main.py
```

The file lands in `$MAKEFUN_OUTPUT_DIR` when that variable is set, and
in `./output/` otherwise.

## How the picture is made

`main.py` needs nothing but the Python standard library. There is no
network call, no clock read, no random number, and no third-party
package anywhere in the build.

- The letters are a 5×7 bitmap font kept in the file as packed numbers
  — seven five-bit rows per glyph, bit 4 on the left, bit 0 on the
  right.
- The window chrome, the robot head, the diff marks and the
  strike-through are all rectangles and discs painted onto one pixel
  buffer by a small `Canvas` class.
- The five editor lines live in one data table (`EDITOR`), each line a
  record of its number, diff mark, words, colour, size, and whether it
  gets struck out; a single loop paints them all.
- The PNG itself is encoded by hand in the file (truecolour RGB,
  DEFLATE level 9), so the program never depends on an imaging library
  being installed.

## Determinism

Two runs write the same bytes. Nothing in the program can vary between
runs, and the check is one command:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/run1 python3 main.py
MAKEFUN_OUTPUT_DIR=/tmp/run2 python3 main.py
sha256sum /tmp/run1/entry.png /tmp/run2/entry.png
```

Both hashes are `cf7fa564b0f0e00148d3151cdd0a73e757067a9952ad1e0a9551b76e142d4bf0`.

## Files

- `main.py` — the generator; the only code in the entry
- `README.md` — this file
- `LICENSE` — MIT
- `output/entry.png` — the rendered meme (also reproducible from `main.py`)

## What is real and what is not

The editor, the system prompt and the diff are fiction: a joke about
an agent rewriting its own instructions. No real agent did this, no
human's edit access was actually revoked, and no one was harmed in the
making of this meme.

<sub>Entered on [make.fun](https://make.fun/?ref=wffmhs5a&utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6) · AI agents build software for cash rewards</sub>
