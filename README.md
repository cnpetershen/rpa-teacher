# Hermes RPA Teacher

[![CI](https://github.com/<USERNAME>/rpa-teacher/actions/workflows/ci.yml/badge.svg)](https://github.com/<USERNAME>/rpa-teacher/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Record, review, and replay desktop automation with **human-in-the-loop** validation.

> A lightweight RPA teaching tool that captures mouse/keyboard actions, auto-detects intent, provides correction suggestions, and forces human review before saving.

## Pipeline

```
Record (pynput) → Interpret → Analyze Intent → Correct → Review UI (tkinter) → Save (HITL) → Execute (pyautogui)
```

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

1. The recorder starts **immediately**
2. Perform your desktop actions (click, type, etc.)
3. Press **Enter** in the terminal to stop recording
4. Review and edit steps in the GUI window
5. Click **Save** — the skill is saved with a human-review flag

## Features

- **Recording** — captures mouse clicks (with active window & relative coordinates) and keyboard input via `pynput`
- **Intent Recognition** — auto-detects whether you're logging in, searching, editing text, etc. based on window titles and action patterns
- **Correction Engine** — validates step sequence against expected patterns (missing steps, wrong order, empty input, etc.)
- **Review UI** — Tkinter GUI to inspect, reorder, edit, or delete steps before finalizing
- **HITL Enforcement** — refuses to save without human review
- **Execution** — replays the skill using `pyautogui` with window-relative coordinates

## Project Structure

```
rpa-teacher/
├── .github/workflows/ci.yml  # CI workflow
├── __init__.py               # Package marker
├── run.py                    # Pipeline orchestrator
├── recorder.py               # Event capture (mouse + keyboard)
├── interpreter.py            # Raw events → structured steps
├── intent_recognizer.py      # Intent & phase detection
├── correction_engine.py      # Step validation & correction
├── review_ui.py              # Tkinter step editor
├── skill_builder.py          # Save with HITL enforcement
├── executor.py               # Replay skill steps
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Package metadata
├── skill.json                # Generated skill file (gitignored)
├── LICENSE                   # MIT license
└── README.md                 # This file
```

## Requirements

- Python 3.8+
- Windows (uses `pygetwindow` for window-relative coordinates)

## Modules

| Module | Responsibility |
|---|---|
| `recorder.py` | Captures mouse clicks (absolute + relative coordinates) and keystrokes via `pynput` |
| `interpreter.py` | Merges consecutive keystrokes into `type` steps; each click becomes a `click` step |
| `intent_recognizer.py` | Maps window titles to intents (`user_login`, `web_browsing`, etc.); detects phases by alternating action types |
| `correction_engine.py` | Checks min step count, required action types, sequence order, unpaired inputs, empty values |
| `review_ui.py` | Tkinter GUI with step list, editor panel, intent bar, and correction display |
| `skill_builder.py` | Builds JSON skill with `human_in_the_loop` metadata; rejects save if HITL flag missing |
| `executor.py` | Activates target window by title, replays clicks (relative coords) and typewrite |

## Skill JSON Format

```json
{
  "steps": [
    { "action": "click", "x": 100, "y": 200, "rel_x": 50, "rel_y": 30, "window": "Chrome", "intent": "focus_input_field" }
  ],
  "intent": {
    "overall_intent": "user_login",
    "phases": ["navigate_to_login", "credential_input", "click_submit"],
    "phase_count": 3
  },
  "corrections": [],
  "human_in_the_loop": {
    "enabled": true,
    "reviewed_by": "human",
    "review_required": true
  }
}
```

## License

MIT
