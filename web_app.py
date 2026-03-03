import os

from flask import Flask, redirect, render_template, request, session, url_for

from game import default_python_challenges


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("CODE_QUEST_SECRET", "dev-secret-change-me")

    @app.get("/")
    def home():
        progress = _get_progress()
        current = min(progress["python_done"] + 1, len(_python_lessons()))
        return render_template("home.html", progress=progress, current=current, total=3)

    @app.get("/python")
    def python_lesson():
        progress = _get_progress()
        lessons = _python_lessons()
        idx = progress["python_done"]

        if idx >= len(lessons):
            return render_template("python.html", progress=progress, complete=True, lesson=None)

        lesson = lessons[idx]
        attempts = session.get("attempts", {}).get(str(idx), 0)
        return render_template(
            "python.html",
            progress=progress,
            complete=False,
            lesson=lesson,
            lesson_number=idx + 1,
            total_lessons=len(lessons),
            attempts=attempts,
            feedback=None,
            status="idle",
        )

    @app.post("/python")
    def submit_python_answer():
        progress = _get_progress()
        lessons = _python_lessons()
        idx = progress["python_done"]

        if idx >= len(lessons):
            return redirect(url_for("python_lesson"))

        lesson = lessons[idx]
        answer = request.form.get("answer", "").strip()
        attempts_map = session.get("attempts", {})
        attempts = int(attempts_map.get(str(idx), 0)) + 1
        attempts_map[str(idx)] = attempts
        session["attempts"] = attempts_map

        if lesson["checker"](answer):
            progress["python_done"] += 1
            progress["score"] += 10
            _save_progress(progress)
            attempts_map[str(idx)] = 0
            session["attempts"] = attempts_map
            return render_template(
                "python.html",
                progress=progress,
                complete=False,
                lesson=lesson,
                lesson_number=idx + 1,
                total_lessons=len(lessons),
                attempts=attempts,
                feedback={
                    "title": "Correct!",
                    "message": lesson["success_message"],
                    "explanation": lesson["explanation"],
                    "example": lesson["example"],
                    "award": "+10 points",
                },
                status="success",
            )

        status = "retry"
        feedback = {
            "title": "Not yet",
            "message": "Good attempt. Learning is step-by-step.",
            "explanation": lesson["gentle_explanation"],
            "example": lesson["example"],
            "award": None,
            "hint": lesson["hint"],
        }

        if attempts >= 3:
            status = "reveal"
            feedback = {
                "title": "Review Mode",
                "message": "You used all attempts for this round. Here is the solution path.",
                "explanation": lesson["solution_breakdown"],
                "example": f"Reference answer: {lesson['model_answer']}",
                "award": "No points this round, but you can continue learning.",
                "hint": None,
            }

        return render_template(
            "python.html",
            progress=progress,
            complete=False,
            lesson=lesson,
            lesson_number=idx + 1,
            total_lessons=len(lessons),
            attempts=attempts,
            feedback=feedback,
            status=status,
        )

    @app.post("/python/continue")
    def continue_after_review():
        progress = _get_progress()
        lessons = _python_lessons()
        idx = progress["python_done"]
        if idx < len(lessons):
            progress["python_done"] += 1
            _save_progress(progress)
            attempts_map = session.get("attempts", {})
            attempts_map[str(idx)] = 0
            session["attempts"] = attempts_map
        return redirect(url_for("python_lesson"))

    @app.post("/reset")
    def reset():
        session["progress"] = {"python_done": 0, "score": 0}
        session["attempts"] = {}
        return redirect(url_for("home"))

    return app


def _get_progress() -> dict:
    progress = session.get("progress", {"python_done": 0, "score": 0})
    return {"python_done": int(progress.get("python_done", 0)), "score": int(progress.get("score", 0))}


def _save_progress(progress: dict) -> None:
    session["progress"] = {"python_done": int(progress["python_done"]), "score": int(progress["score"])}


def _python_lessons() -> list[dict]:
    challenges = default_python_challenges()
    return [
        {
            "title": "Lists + sum()",
            "concept": "A list can store many values. `sum()` adds numeric items together.",
            "prompt": challenges[0].prompt,
            "hint": challenges[0].hint,
            "checker": challenges[0].checker,
            "success_message": challenges[0].success_message,
            "explanation": "The list contains 1, 2, and 3. `sum(numbers)` performs 1 + 2 + 3, which equals 6.",
            "gentle_explanation": "Focus on what `sum()` does: it adds every number in the list.",
            "solution_breakdown": "Step 1: Identify list values (1, 2, 3). Step 2: Add them in order. Step 3: Final output is 6.",
            "example": "Try: `print(sum([4, 5, 6]))` -> 15",
            "model_answer": "6",
        },
        {
            "title": "for-loops + range()",
            "concept": "`range(n)` creates numbers from 0 up to (but not including) n.",
            "prompt": challenges[1].prompt,
            "hint": challenges[1].hint,
            "checker": challenges[1].checker,
            "success_message": challenges[1].success_message,
            "explanation": "`range(3)` gives 0, 1, 2. The loop prints each value one by one.",
            "gentle_explanation": "A loop needs something iterable. `range()` is the standard way to generate simple index values.",
            "solution_breakdown": "Step 1: Need three values (0,1,2). Step 2: `range(3)` provides exactly that. Step 3: loop prints each.",
            "example": "Try: `for i in range(5): print(i)` -> 0 1 2 3 4",
            "model_answer": "range",
        },
        {
            "title": "Dictionaries",
            "concept": "A dictionary stores key/value pairs, like labels and their values.",
            "prompt": challenges[2].prompt,
            "hint": challenges[2].hint,
            "checker": challenges[2].checker,
            "success_message": challenges[2].success_message,
            "explanation": "Both `{...}` syntax and `dict(...)` syntax are valid ways to create dictionaries.",
            "gentle_explanation": "Think of a dictionary as named slots: `name` and `skill` each hold one value.",
            "solution_breakdown": "Step 1: Create keys `name` and `skill`. Step 2: assign values `Ada` and `SQL`. Step 3: return dictionary.",
            "example": "Try: `{'city': 'Austin', 'state': 'TX'}`",
            "model_answer": "{'name': 'Ada', 'skill': 'SQL'}",
        },
    ]


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5000)
