# Web App Guide

## Overview
`web_app.py` provides a beginner-friendly Flask interface for Code Quest.
It teaches Python concepts with:
- One concept per lesson
- Immediate feedback
- Hints and gentle explanations
- Score and progress tracking in session

## Run locally
```bash
cd "/Users/kyleparker/Documents/code game"
pip3 install -r requirements.txt
python3 web_app.py
```

Open `http://127.0.0.1:5000`.

## Routes
- `GET /` dashboard and progress summary
- `GET /python` active lesson page
- `POST /python` answer submission + feedback
- `POST /python/continue` continue after review-mode
- `POST /reset` reset score/progress

## Where lessons live
Lesson definitions are in `_python_lessons()` inside `web_app.py`.
Each lesson includes:
- `title`, `concept`, `prompt`
- `checker` function
- `hint`
- explanation blocks (`explanation`, `gentle_explanation`, `solution_breakdown`)
- `example` and `model_answer`

## How to add a new lesson
1. Add a new `PythonChallenge` in `default_python_challenges()` in `game.py`.
2. Add a matching lesson object in `_python_lessons()` in `web_app.py`.
3. Keep explanations beginner-safe and concrete.
4. Run tests:
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```
