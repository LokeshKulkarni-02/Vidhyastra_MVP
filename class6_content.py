
"""Class 6 Mathematics: 10 chapters and 3 practice questions per chapter."""

CHAPTER_DATA = [
    ("Patterns in Mathematics", [
        ("What comes next: 2, 4, 6, 8, __?", ["9", "10", "11", "12"], "10", "The pattern increases by 2."),
        ("What is the next square number after 16?", ["20", "24", "25", "32"], "25", "The square numbers are 1, 4, 9, 16, 25."),
        ("Which rule describes 5, 10, 15, 20?", ["Add 2", "Add 5", "Multiply by 5", "Subtract 5"], "Add 5", "Each number increases by 5.")
    ]),
    ("Lines and Angles", [
        ("How many degrees are in a right angle?", ["45°", "60°", "90°", "180°"], "90°", "A right angle measures 90 degrees."),
        ("Which angle is smaller than 90°?", ["Obtuse", "Straight", "Acute", "Reflex"], "Acute", "An acute angle is less than 90 degrees."),
        ("Which instrument measures angles?", ["Ruler", "Compass", "Protractor", "Divider"], "Protractor", "A protractor is used to measure angles.")
    ]),
    ("Number Play", [
        ("What is the place value of 6 in 46,218?", ["6", "60", "600", "6,000"], "6,000", "The digit 6 is in the thousands place."),
        ("Which number is divisible by 5?", ["32", "43", "65", "72"], "65", "Numbers ending in 0 or 5 are divisible by 5."),
        ("What is 2,500 + 300 + 40 + 6?", ["2,346", "2,846", "2,536", "2,806"], "2,846", "Add the place values to get 2,846.")
    ]),
    ("Data Handling and Presentation", [
        ("What is the average of 4, 6 and 8?", ["5", "6", "7", "8"], "6", "(4 + 6 + 8) ÷ 3 = 6."),
        ("In a pictograph, one star represents 2 books. What do 4 stars represent?", ["4", "6", "8", "10"], "8", "Four stars represent 4 × 2 = 8 books."),
        ("Which graph uses rectangular bars?", ["Bar graph", "Pictograph", "Number line", "Circle"], "Bar graph", "A bar graph represents data using rectangular bars.")
    ]),
    ("Prime Time", [
        ("Which is a prime number?", ["9", "15", "17", "21"], "17", "17 has exactly two factors: 1 and 17."),
        ("Which number is a factor of 24?", ["5", "7", "8", "10"], "8", "24 ÷ 8 = 3, so 8 is a factor."),
        ("What is the smallest prime number?", ["0", "1", "2", "3"], "2", "2 is the smallest prime number.")
    ]),
    ("Perimeter and Area", [
        ("A square has a side of 5 cm. What is its perimeter?", ["10 cm", "15 cm", "20 cm", "25 cm"], "20 cm", "Perimeter = 4 × 5 = 20 cm."),
        ("Find the area of a rectangle 6 cm long and 4 cm wide.", ["10 cm²", "20 cm²", "24 cm²", "28 cm²"], "24 cm²", "Area = length × width = 6 × 4."),
        ("A triangle has sides 3 cm, 4 cm and 5 cm. Find its perimeter.", ["9 cm", "10 cm", "12 cm", "15 cm"], "12 cm", "Add the sides: 3 + 4 + 5 = 12 cm.")
    ]),
    ("Fractions", [
        ("What is 1/2 + 1/4?", ["1/4", "2/4", "3/4", "4/4"], "3/4", "1/2 = 2/4, so 2/4 + 1/4 = 3/4."),
        ("Which fraction is equivalent to 1/2?", ["1/3", "2/4", "3/4", "2/3"], "2/4", "Multiplying the numerator and denominator by 2 gives 2/4."),
        ("What is 3/4 of 20?", ["5", "10", "15", "16"], "15", "20 ÷ 4 × 3 = 15.")
    ]),
    ("Playing with Constructions", [
        ("Which instrument is used to draw a circle?", ["Ruler", "Compass", "Protractor", "Set square"], "Compass", "A compass is used to draw circles and arcs."),
        ("Which tool measures a line segment?", ["Ruler", "Compass", "Eraser", "Protractor"], "Ruler", "A ruler measures length."),
        ("What is the diameter of a circle with radius 4 cm?", ["2 cm", "4 cm", "8 cm", "16 cm"], "8 cm", "Diameter = 2 × radius = 8 cm.")
    ]),
    ("Symmetry", [
        ("How many lines of symmetry does a square have?", ["1", "2", "3", "4"], "4", "A square has four lines of symmetry."),
        ("A line of symmetry divides a shape into:", ["Two matching halves", "Three parts", "Four circles", "Unequal halves"], "Two matching halves", "Both halves match when folded along the symmetry line."),
        ("How many lines of symmetry does an equilateral triangle have?", ["1", "2", "3", "4"], "3", "An equilateral triangle has three lines of symmetry.")
    ]),
    ("The Other Side of Zero", [
        ("Which number is less than zero?", ["5", "2", "-3", "8"], "-3", "Negative numbers are less than zero."),
        ("Which is greater: -2 or -5?", ["-5", "-2", "Both equal", "0"], "-2", "-2 is to the right of -5 on the number line."),
        ("What is -5 + 8?", ["-13", "-3", "3", "13"], "3", "Adding 8 to -5 gives 3.")
    ])
]


def build_class6_questions():
    """Return questions in the format expected by question_bank.py."""
    questions = []

    for chapter_number, (chapter_title, items) in enumerate(CHAPTER_DATA, start=1):
        chapter_id = f"c6-math-ch{chapter_number:02d}"

        for question_number, item in enumerate(items, start=1):
            q, options, answer, why = item

            questions.append({
                "id": f"C6M{chapter_number:02d}-{question_number:03d}",
                "grade": "Class 6",
                "subject": "Mathematics",
                "chapter_id": chapter_id,
                "topic": chapter_title,
                "concept_id": f"c6-ch{chapter_number:02d}-q{question_number:03d}",
                "concept": chapter_title,
                "prerequisites": [],
                "difficulty": "easy" if question_number == 1 else "medium",
                "q": q,
                "options": options,
                "answer": answer,
                "why": why
            })

    return questions
