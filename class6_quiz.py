
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "vidhyastra-class6-quiz-secret"

QUESTIONS = [
    {
        "chapter": "Patterns in Mathematics",
        "question": "What comes next: 3, 6, 9, 12, __?",
        "options": ["13", "14", "15", "16"],
        "answer": "15",
        "explanation": "Each number increases by 3."
    },
    {
        "chapter": "Lines and Angles",
        "question": "How many degrees are there in a right angle?",
        "options": ["45°", "60°", "90°", "180°"],
        "answer": "90°",
        "explanation": "A right angle measures exactly 90 degrees."
    },
    {
        "chapter": "Number Play",
        "question": "Which of these numbers is divisible by 5?",
        "options": ["32", "43", "65", "72"],
        "answer": "65",
        "explanation": "Numbers ending in 0 or 5 are divisible by 5."
    },
    {
        "chapter": "Data Handling",
        "question": "Find the average of 4, 6 and 8.",
        "options": ["5", "6", "7", "8"],
        "answer": "6",
        "explanation": "(4 + 6 + 8) / 3 = 18 / 3 = 6."
    },
    {
        "chapter": "Prime Time",
        "question": "Which of these is a prime number?",
        "options": ["9", "15", "17", "21"],
        "answer": "17",
        "explanation": "17 has exactly two factors: 1 and 17."
    },
    {
        "chapter": "Perimeter and Area",
        "question": "A square has a side of 5 cm. What is its perimeter?",
        "options": ["10 cm", "15 cm", "20 cm", "25 cm"],
        "answer": "20 cm",
        "explanation": "Perimeter = 4 × side = 4 × 5 = 20 cm."
    },
    {
        "chapter": "Fractions",
        "question": "What is 1/2 + 1/4?",
        "options": ["1/4", "2/4", "3/4", "4/4"],
        "answer": "3/4",
        "explanation": "1/2 = 2/4, so 2/4 + 1/4 = 3/4."
    },
    {
        "chapter": "Playing with Constructions",
        "question": "Which instrument is commonly used to draw a circle?",
        "options": ["Ruler", "Compass", "Set square", "Protractor"],
        "answer": "Compass",
        "explanation": "A compass is used to draw circles and arcs."
    },
    {
        "chapter": "Symmetry",
        "question": "How many lines of symmetry does a square have?",
        "options": ["1", "2", "3", "4"],
        "answer": "4",
        "explanation": "A square has four lines of symmetry."
    },
    {
        "chapter": "The Other Side of Zero",
        "question": "What is -5 + 8?",
        "options": ["-13", "-3", "3", "13"],
        "answer": "3",
        "explanation": "-5 + 8 = 3."
    }
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Vidhyastra Class 6 Quiz</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #eef2ff;
            margin: 0;
            padding: 25px;
        }
        .container {
            max-width: 650px;
            margin: 35px auto;
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 5px 20px #0002;
        }
        h1 { color: #3730a3; }
        .chapter { color: #6366f1; font-weight: bold; }
        .option {
            display: block;
            padding: 14px;
            border: 1px solid #ddd;
            border-radius: 9px;
            margin: 12px 0;
            cursor: pointer;
        }
        .option:hover { background: #eef2ff; }
        input[type=radio] { margin-right: 12px; }
        button {
            background: #4f46e5;
            color: white;
            padding: 13px 25px;
            border: none;
            border-radius: 9px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 15px;
        }
        button:hover { background: #3730a3; }
        .feedback {
            background: #eef2ff;
            padding: 15px;
            border-radius: 9px;
            margin-top: 18px;
        }
        .score { font-size: 24px; color: #3730a3; }
        .error { color: #dc2626; }
    </style>
</head>
<body>
<div class="container">

{% if finished %}
    <h1>Quiz Completed!</h1>
    <p class="score">Your Score: {{ score }} / {{ total }}</p>
    <h3>
        {% if score == total %}
            Excellent! Perfect score!
        {% elif score >= total / 2 %}
            Good work! Keep practising!
        {% else %}
            Keep learning. You can do better!
        {% endif %}
    </h3>
    <p>You have completed your Class 6 Mathematics quiz.</p>
    <a href="{{ url_for('restart') }}">
        <button>Try Again</button>
    </a>

{% elif feedback %}
    <h1>Vidhyastra Quiz</h1>
    <h3>Question {{ index + 1 }} of {{ total }}</h3>
    <div class="feedback">
        <h3>{{ "Correct!" if correct else "Not quite! Try to learn from this." }}</h3>
        <p><b>Correct answer:</b> {{ answer }}</p>
        <p><b>Explanation:</b> {{ explanation }}</p>
    </div>
    <a href="{{ url_for('next_question') }}">
        <button>Next Question</button>
    </a>

{% else %}
    <h1>Vidhyastra</h1>
    <p><b>Class 6 Mathematics Quiz</b></p>
    <p>Question {{ index + 1 }} of {{ total }}</p>
    <p class="chapter">{{ question.chapter }}</p>
    <h3>{{ question.question }}</h3>

    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}

    <form method="POST">
        {% for option in question.options %}
            <label class="option">
                <input type="radio" name="answer" value="{{ option }}">
                {{ option }}
            </label>
        {% endfor %}
        <button type="submit">Submit Answer</button>
    </form>
{% endif %}

</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def quiz():
    index = session.get("index", 0)
    score = session.get("score", 0)
    feedback = session.get("feedback", False)

    if index >= len(QUESTIONS):
        return redirect(url_for("result"))

    if request.method == "POST":
        selected = request.form.get("answer")

        if selected not in QUESTIONS[index]["options"]:
            return render_template_string(
                HTML,
                question=QUESTIONS[index],
                index=index,
                total=len(QUESTIONS),
                feedback=False,
                error="Please select an answer first."
            )

        question = QUESTIONS[index]
        correct = selected == question["answer"]

        if correct:
            session["score"] = score + 1

        session["feedback"] = True
        session["correct"] = correct
        session["answer"] = question["answer"]
        session["explanation"] = question["explanation"]

        return redirect(url_for("quiz"))

    return render_template_string(
        HTML,
        question=QUESTIONS[index],
        index=index,
        total=len(QUESTIONS),
        feedback=feedback,
        correct=session.get("correct", False),
        answer=session.get("answer", ""),
        explanation=session.get("explanation", ""),
        error=None
    )


@app.route("/next")
def next_question():
    session["index"] = session.get("index", 0) + 1
    session["feedback"] = False

    if session["index"] >= len(QUESTIONS):
        return redirect(url_for("result"))

    return redirect(url_for("quiz"))


@app.route("/result")
def result():
    return render_template_string(
        HTML,
        finished=True,
        score=session.get("score", 0),
        total=len(QUESTIONS)
    )


@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("quiz"))


if __name__ == "__main__":
    app.run(debug=True)
