import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


PROGRESS_FILE = Path("progress.json")


@dataclass
class PythonChallenge:
    prompt: str
    checker: Callable[[str], bool]
    success_message: str
    hint: str


@dataclass
class SQLChallenge:
    prompt: str
    expected_rows: list[tuple]
    success_message: str
    hint: str


def _clean(text: str) -> str:
    return "".join(text.strip().lower().split())


def default_python_challenges() -> list[PythonChallenge]:
    return [
        PythonChallenge(
            prompt=(
                "Python 1/3:\n"
                "What is the output of this code?\n\n"
                "numbers = [1, 2, 3]\n"
                "print(sum(numbers))\n"
            ),
            checker=lambda answer: _clean(answer) == "6",
            success_message="Correct. `sum([1, 2, 3])` is 6.",
            hint="`sum` adds all numbers in the list.",
        ),
        PythonChallenge(
            prompt=(
                "Python 2/3:\n"
                "Fill in the missing word so this loop prints 0 1 2:\n\n"
                "for i in _____(3):\n"
                "    print(i)\n"
            ),
            checker=lambda answer: _clean(answer) == "range",
            success_message="Nice. `range(3)` gives 0, 1, 2.",
            hint="Common built-in used with `for` loops and integer sequences.",
        ),
        PythonChallenge(
            prompt=(
                "Python 3/3:\n"
                "Type a valid Python expression that creates a dictionary with:\n"
                "name='Ada' and skill='SQL'\n\n"
                "Example format: {'x': 1}\n"
            ),
            checker=lambda answer: _clean(answer)
            in {
                "{'name':'ada','skill':'sql'}",
                '{"name":"ada","skill":"sql"}',
                '{"skill":"sql","name":"ada"}',
                "{'skill':'sql','name':'ada'}",
                "dict(name='ada',skill='sql')",
                "dict(skill='sql',name='ada')",
                'dict(name="ada",skill="sql")',
                'dict(skill="sql",name="ada")',
            },
            success_message="Great. You created a valid dictionary.",
            hint="Use either `{...}` with key/value pairs or `dict(...)`.",
        ),
    ]


def setup_sql_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE learners (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            points INTEGER NOT NULL
        );

        INSERT INTO learners (name, points) VALUES
            ('Ava', 12),
            ('Leo', 8),
            ('Mia', 19),
            ('Noah', 15);
        """
    )
    conn.commit()
    return conn


def default_sql_challenges() -> list[SQLChallenge]:
    return [
        SQLChallenge(
            prompt=(
                "SQL 1/3:\n"
                "Write a query to show all columns for all rows from the `learners` table.\n"
            ),
            expected_rows=[
                (1, "Ava", 12),
                (2, "Leo", 8),
                (3, "Mia", 19),
                (4, "Noah", 15),
            ],
            success_message="Correct. You returned every row and column.",
            hint="Use `SELECT * FROM learners;`",
        ),
        SQLChallenge(
            prompt=(
                "SQL 2/3:\n"
                "Write a query to return only names from learners with points >= 15.\n"
                "Return one column named `name` and sort alphabetically.\n"
            ),
            expected_rows=[("Mia",), ("Noah",)],
            success_message="Nice filtering and ordering.",
            hint=(
                "Use `WHERE points >= 15`, select only `name`, and add `ORDER BY name`."
            ),
        ),
        SQLChallenge(
            prompt=(
                "SQL 3/3:\n"
                "Write a query to show the average points as one column named `avg_points`.\n"
            ),
            expected_rows=[(13.5,)],
            success_message="Great. You used an aggregate function.",
            hint="Use `AVG(points)` and alias it with `AS avg_points`.",
        ),
    ]


def load_progress() -> dict:
    if not PROGRESS_FILE.exists():
        return {"python_done": 0, "sql_done": 0, "score": 0}
    try:
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        return {
            "python_done": int(data.get("python_done", 0)),
            "sql_done": int(data.get("sql_done", 0)),
            "score": int(data.get("score", 0)),
        }
    except (json.JSONDecodeError, OSError, ValueError):
        return {"python_done": 0, "sql_done": 0, "score": 0}


def save_progress(progress: dict) -> None:
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2), encoding="utf-8")


def ask_with_retry(prompt: str, hint: str, validator: Callable[[str], bool]) -> bool:
    print(prompt)
    for attempt in range(1, 4):
        answer = input("Your answer: ").strip()
        if validator(answer):
            return True
        if attempt < 3:
            print(f"Not quite. Hint: {hint}")
    print("No problem. You can revisit this later.")
    return False


def run_python_round(progress: dict) -> None:
    challenges = default_python_challenges()
    done = progress["python_done"]

    if done >= len(challenges):
        print("You already completed all Python challenges.")
        return

    challenge = challenges[done]
    success = ask_with_retry(
        prompt=challenge.prompt,
        hint=challenge.hint,
        validator=challenge.checker,
    )
    if success:
        print(challenge.success_message)
        progress["python_done"] += 1
        progress["score"] += 10
        save_progress(progress)
        print("+10 points earned.\n")


def run_sql_round(progress: dict) -> None:
    challenges = default_sql_challenges()
    done = progress["sql_done"]

    if done >= len(challenges):
        print("You already completed all SQL challenges.")
        return

    challenge = challenges[done]
    conn = setup_sql_db()
    print(challenge.prompt)

    for attempt in range(1, 4):
        query = input("SQL query: ").strip()
        try:
            rows = conn.execute(query).fetchall()
            if rows == challenge.expected_rows:
                print(challenge.success_message)
                progress["sql_done"] += 1
                progress["score"] += 15
                save_progress(progress)
                print("+15 points earned.\n")
                conn.close()
                return
            print("Query ran, but result is not correct.")
        except sqlite3.Error as exc:
            print(f"SQL error: {exc}")

        if attempt < 3:
            print(f"Hint: {challenge.hint}")

    print("Keep practicing. Try this challenge again later.\n")
    conn.close()


def show_dashboard(progress: dict) -> None:
    print("\n=== Code Quest: Python + SQL Trainer ===")
    print(f"Score: {progress['score']}")
    print(f"Python completed: {progress['python_done']}/3")
    print(f"SQL completed: {progress['sql_done']}/3\n")


def reset_progress() -> None:
    save_progress({"python_done": 0, "sql_done": 0, "score": 0})
    print("Progress reset.\n")

