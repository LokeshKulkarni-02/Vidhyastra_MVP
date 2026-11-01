"""Additional original Class 8 Mathematics questions for Chapter 1.

The existing question_bank.json contains 9 Square Numbers questions and
6 Cubic Numbers questions. This module adds the missing questions so each
topic has exactly 8 easy, 8 medium and 4 hard questions (20 total).
"""


def _question(qid, topic, concept_id, concept, difficulty, q, options, answer, why):
    options = [str(value) for value in options]
    answer = str(answer)
    if len(options) != 4 or len(set(options)) != 4 or answer not in options:
        raise ValueError(f"Invalid options or answer for {qid}")
    return {
        "id": qid,
        "grade": "Class 8",
        "subject": "Mathematics",
        "chapter_id": "c8-math-ch01",
        "topic": topic,
        "concept_id": concept_id,
        "concept": concept,
        "prerequisites": [],
        "difficulty": difficulty,
        "q": q,
        "options": options,
        "answer": answer,
        "why": why,
    }


SQUARE_QUESTIONS = [
    _question("C8M1-SQ-010", "Square Numbers", "square-as-product", "A square number as n × n", "easy",
              "What is 9 × 9?", ["18", "72", "81", "90"], "81", "9 squared is 9 × 9 = 81."),
    _question("C8M1-SQ-011", "Square Numbers", "recognising-square-numbers", "Recognising perfect squares", "easy",
              "Which number is the square of 11?", ["22", "111", "121", "131"], "121", "11 × 11 = 121."),
    _question("C8M1-SQ-012", "Square Numbers", "square-as-product", "A square number as n × n", "easy",
              "What is 5 squared?", ["10", "15", "20", "25"], "25", "5² means 5 × 5, which equals 25."),
    _question("C8M1-SQ-013", "Square Numbers", "square-roots", "Finding square roots", "easy",
              "What is the square root of 49?", ["6", "7", "8", "9"], "7", "7 × 7 = 49, so √49 = 7."),

    _question("C8M1-SQ-014", "Square Numbers", "square-number-patterns", "Patterns in square numbers", "medium",
              "What is the difference between 8² and 7²?", ["13", "14", "15", "16"], "15", "8² − 7² = 64 − 49 = 15."),
    _question("C8M1-SQ-015", "Square Numbers", "recognising-square-numbers", "Recognising perfect squares", "medium",
              "Which number is not a perfect square?", ["100", "121", "130", "144"], "130", "100 = 10², 121 = 11² and 144 = 12²; 130 is not a square."),
    _question("C8M1-SQ-016", "Square Numbers", "square-roots", "Finding square roots", "medium",
              "A square has area 196 cm². What is its side length?", ["12 cm", "13 cm", "14 cm", "16 cm"], "14 cm", "The side is √196 = 14 cm."),
    _question("C8M1-SQ-017", "Square Numbers", "square-number-patterns", "Patterns in square numbers", "medium",
              "What is the sum of the first five odd positive numbers?", ["20", "25", "30", "36"], "25", "1 + 3 + 5 + 7 + 9 = 25 = 5²."),

    _question("C8M1-SQ-018", "Square Numbers", "square-roots", "Finding square roots", "hard",
              "A number multiplied by itself is 576. What is the positive number?", ["22", "23", "24", "26"], "24", "24 × 24 = 576, so the positive square root is 24."),
    _question("C8M1-SQ-019", "Square Numbers", "square-number-patterns", "Patterns in square numbers", "hard",
              "The sum of two consecutive positive square numbers is 145. Which pair is it?", ["6² and 7²", "8² and 9²", "9² and 10²", "10² and 11²"], "8² and 9²", "64 + 81 = 145."),
    _question("C8M1-SQ-020", "Square Numbers", "square-as-product", "A square number as n × n", "hard",
              "A square floor has area 324 m². How many metres of border are needed around it?", ["36 m", "54 m", "72 m", "81 m"], "72 m", "The side is √324 = 18 m; perimeter = 4 × 18 = 72 m."),
]


CUBIC_QUESTIONS = [
    _question("C8M1-CU-007", "Cubic Numbers", "cube-as-product", "A cube number as n × n × n", "easy",
              "What is 2 cubed?", ["4", "6", "8", "12"], "8", "2³ = 2 × 2 × 2 = 8."),
    _question("C8M1-CU-008", "Cubic Numbers", "recognising-cubes", "Recognising perfect cubes", "easy",
              "Which is a perfect cube?", ["16", "27", "36", "45"], "27", "27 = 3 × 3 × 3 = 3³."),
    _question("C8M1-CU-009", "Cubic Numbers", "cube-roots", "Finding cube roots", "easy",
              "What is the cube root of 8?", ["2", "3", "4", "8"], "2", "2³ = 8, so the cube root of 8 is 2."),
    _question("C8M1-CU-010", "Cubic Numbers", "cube-as-product", "A cube number as n × n × n", "easy",
              "What is 4 × 4 × 4?", ["16", "32", "48", "64"], "64", "4³ = 4 × 4 × 4 = 64."),
    _question("C8M1-CU-011", "Cubic Numbers", "recognising-cubes", "Recognising perfect cubes", "easy",
              "Which number equals 5³?", ["25", "75", "100", "125"], "125", "5 × 5 × 5 = 125."),

    _question("C8M1-CU-012", "Cubic Numbers", "cube-roots", "Finding cube roots", "medium",
              "What is the cube root of 216?", ["4", "5", "6", "8"], "6", "6³ = 6 × 6 × 6 = 216."),
    _question("C8M1-CU-013", "Cubic Numbers", "recognising-cubes", "Recognising perfect cubes", "medium",
              "Which number is not a perfect cube?", ["64", "125", "150", "216"], "150", "64 = 4³, 125 = 5³ and 216 = 6³; 150 is not a perfect cube."),
    _question("C8M1-CU-014", "Cubic Numbers", "cube-number-patterns", "Patterns in cubic numbers", "medium",
              "What is the next cube number after 27?", ["36", "54", "64", "81"], "64", "The next cube after 3³ is 4³ = 64."),
    _question("C8M1-CU-015", "Cubic Numbers", "cube-as-product", "A cube number as n × n × n", "medium",
              "What is 7 cubed?", ["49", "147", "343", "729"], "343", "7³ = 7 × 7 × 7 = 343."),
    _question("C8M1-CU-016", "Cubic Numbers", "cube-number-patterns", "Patterns in cubic numbers", "medium",
              "What is the difference between 4³ and 3³?", ["27", "32", "37", "41"], "37", "4³ − 3³ = 64 − 27 = 37."),

    _question("C8M1-CU-017", "Cubic Numbers", "cube-roots", "Finding cube roots", "hard",
              "A cube has volume 729 cm³. What is the length of one edge?", ["7 cm", "8 cm", "9 cm", "27 cm"], "9 cm", "The edge is the cube root of 729; 9³ = 729."),
    _question("C8M1-CU-018", "Cubic Numbers", "cube-number-patterns", "Patterns in cubic numbers", "hard",
              "Which expression has a value of 189?", ["3³ + 4³", "2³ + 5³", "4³ + 5³", "3³ × 2"], "4³ + 5³", "4³ + 5³ = 64 + 125 = 189."),
    _question("C8M1-CU-019", "Cubic Numbers", "cube-as-product", "A cube number as n × n × n", "hard",
              "A cube has edge length 8 cm. What is its volume?", ["64 cm³", "256 cm³", "384 cm³", "512 cm³"], "512 cm³", "Volume = side³ = 8 × 8 × 8 = 512 cm³."),
    _question("C8M1-CU-020", "Cubic Numbers", "cube-roots", "Finding cube roots", "hard",
              "The volume of a cube is 1,000 cm³. What is the edge length?", ["10 cm", "20 cm", "100 cm", "1,000 cm"], "10 cm", "10³ = 10 × 10 × 10 = 1,000 cm³."),
]


def build_class8_questions():
    """Return the supplemental Class 8 items; base JSON items remain intact."""
    return [dict(question) for question in SQUARE_QUESTIONS + CUBIC_QUESTIONS]
