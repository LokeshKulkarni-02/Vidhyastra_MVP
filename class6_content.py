"""Class 6 Mathematics pilot: 20 questions for each mapped chapter.

Each chapter contains exactly 8 easy, 8 medium and 4 hard questions.
Questions are original practice items aligned to the listed concepts; they
are not copied from the NCERT textbook.
"""

import random


def _item(question, answer, distractors, explanation, difficulty):
    answer = str(answer)
    options = [answer] + [str(value) for value in distractors if str(value) != answer]
    unique = []
    for option in options:
        if option not in unique:
            unique.append(option)
    fallback = 0
    while len(unique) < 4:
        candidate = f"Option {fallback + 1}"
        fallback += 1
        if candidate not in unique and candidate != answer:
            unique.append(candidate)
    unique = unique[:4]
    seed = sum(ord(char) for char in question)
    random.Random(seed).shuffle(unique)
    return (question, unique, answer, explanation, difficulty)


def _num(question, answer, explanation, difficulty, wrong=None):
    answer = int(answer)
    if wrong is None:
        wrong = [answer + 1, answer - 1, answer + 10]
    return _item(question, str(answer), [str(x) for x in wrong], explanation, difficulty)


def _patterns():
    items = []
    easy = [(2, 2), (5, 5), (3, 4), (10, 3), (7, 2), (1, 6), (4, 4)]
    for start, step in easy:
        seq = [start + step * i for i in range(4)]
        ans = start + step * 4
        items.append(_num(
            f"What comes next: {', '.join(map(str, seq))}, __?", ans,
            f"The sequence increases by {step} each time.", "easy",
            [ans + step, ans - step, ans + 1]
        ))
    items.append(_item("Which rule describes 6, 12, 18, 24?", "Add 6 each time",
                       ["Add 4 each time", "Multiply by 2 each time", "Subtract 6 each time"],
                       "Each term is 6 more than the previous term.", "easy"))

    medium_specs = [
        ([4, 8, 12, 16], 20, "The pattern adds 4 each time."),
        ([30, 25, 20, 15], 10, "The pattern subtracts 5 each time."),
        ([1, 4, 9, 16], 25, "These are square numbers: 1², 2², 3², 4²; next is 5²."),
        ([2, 6, 12, 20], 30, "The terms are 1×2, 2×3, 3×4, 4×5; next is 5×6."),
        ([3, 6, 12, 24], 48, "Each term is double the previous term."),
        ([50, 45, 39, 32], 24, "The subtractions are 5, 6, 7, then 8."),
        ([2, 5, 10, 17], 26, "The terms are 1²+1, 2²+1, 3²+1, 4²+1; next is 5²+1."),
        ([1, 3, 6, 10], 15, "The pattern adds 2, then 3, then 4; next add 5."),
    ]
    for seq, ans, why in medium_specs:
        items.append(_num(f"Find the next number: {', '.join(map(str, seq))}, __.", ans,
                           why, "medium", [ans + 2, ans - 2, ans + 5]))

    hard_specs = [
        ([2, 5, 10, 17, 26], 37, "The differences are 3, 5, 7, 9; next difference is 11."),
        ([81, 72, 63, 54], 45, "The sequence decreases by 9 each time."),
        ([1, 8, 27, 64], 125, "These are cubes: 1³, 2³, 3³, 4³; next is 5³."),
        ([4, 7, 13, 22], 34, "The differences are 3, 6, 9; next difference is 12."),
    ]
    for seq, ans, why in hard_specs:
        items.append(_num(f"A number pattern is {', '.join(map(str, seq))}, __. What is the next term?",
                           ans, why, "hard", [ans + 3, ans - 3, ans + 12]))
    return items


def _angles():
    items = []
    easy_degrees = [35, 90, 125, 180, 72, 148, 15, 110]
    for deg in easy_degrees:
        kind = "Acute" if deg < 90 else "Right" if deg == 90 else "Obtuse" if deg < 180 else "Straight"
        items.append(_item(f"An angle measures {deg}°. What type of angle is it?", kind,
                           ["Acute", "Right", "Obtuse", "Straight"],
                           f"{deg}° is {('less than 90°' if deg < 90 else 'exactly 90°' if deg == 90 else 'between 90° and 180°' if deg < 180 else 'exactly 180°')}, so it is {kind.lower()}.", "easy"))

    medium_values = [(28, "complement", 62), (41, "complement", 49), (115, "supplement", 65),
                     (136, "supplement", 44), (57, "complement", 33), (98, "supplement", 82),
                     (23, "complement", 67), (151, "supplement", 29)]
    for value, kind, answer in medium_values:
        total = 90 if kind == "complement" else 180
        items.append(_num(f"What is the {kind} of an angle of {value}°?", answer,
                           f"Angles that are {kind}s add to {total}°; {total}° − {value}° = {answer}°.",
                           "medium", [total - value + 5, total - value - 5, value]))

    hard_specs = [
        ("Two angles on a straight line are 3x° and 60°. What is x?", 40,
         "Angles on a straight line add to 180°. 3x + 60 = 180, so x = 40.", [30, 50, 60]),
        ("Angles around a point are 90°, 75°, 110° and x°. Find x.", 85,
         "Angles around a point add to 360°. x = 360 − (90 + 75 + 110) = 85°.", [75, 95, 105]),
        ("One angle at an intersection is 128°. What is its vertically opposite angle?", 128,
         "Vertically opposite angles are equal.", [52, 62, 90]),
        ("A straight angle is split into x° and (x + 40)°. Find the smaller angle.", 70,
         "x + x + 40 = 180, so 2x = 140 and x = 70°.", [60, 80, 90]),
    ]
    for q, a, why, wrong in hard_specs:
        items.append(_num(q, a, why, "hard", wrong))
    return items


def _number_play():
    items = []
    easy_specs = [
        ("What is the place value of 6 in 46,218?", "6,000", ["6", "60", "600"], "6 is in the thousands place."),
        ("What is the place value of 3 in 53,721?", "3,000", ["3", "30", "300"], "3 is in the thousands place."),
        ("Which number is divisible by 5?", "65", ["32", "43", "72"], "A number ending in 0 or 5 is divisible by 5."),
        ("Which number is divisible by 10?", "430", ["435", "443", "434"], "A number ending in 0 is divisible by 10."),
        ("What is 2,500 + 300 + 40 + 6?", "2,846", ["2,346", "2,536", "2,806"], "Add the place values to get 2,846."),
        ("Which is the greatest number?", "8,305", ["8,035", "8,300", "8,053"], "Compare digits from left to right; 8,305 is greatest."),
        ("What is the successor of 9,999?", "10,000", ["9,998", "9,990", "10,001"], "The successor is one more than the number."),
        ("Which digit is in the hundreds place in 72,491?", "4", ["2", "9", "1"], "In 72,491, the hundreds digit is 4."),
    ]
    items.extend(_item(q, a, wrong, why, "easy") for q, a, wrong, why in easy_specs)

    med_specs = [
        ("Round 4,768 to the nearest hundred.", "4,800", ["4,700", "4,760", "5,000"], "The tens digit is 6, so round 4,700 up to 4,800."),
        ("Round 28,349 to the nearest thousand.", "28,000", ["29,000", "28,300", "28,400"], "The hundreds digit is 3, so round down to 28,000."),
        ("Which number is divisible by both 2 and 3?", "246", ["245", "247", "250"], "246 is even and its digit sum is 12, which is divisible by 3."),
        ("Which is the expanded form of 60,508?", "60,000 + 500 + 8", ["6,000 + 500 + 8", "60,000 + 50 + 8", "60,000 + 5,000 + 8"], "Write each non-zero place value and add them."),
        ("What is 7 × 100 + 4 × 10 + 9?", "749", ["7,049", "7,490", "794"], "700 + 40 + 9 = 749."),
        ("Which number is divisible by 9?", "729", ["724", "725", "728"], "7 + 2 + 9 = 18, which is divisible by 9."),
        ("Arrange 3,506; 3,560; 3,065; 3,650 in ascending order. Which is third?", "3,560", ["3,506", "3,065", "3,650"], "The order is 3,065, 3,506, 3,560, 3,650."),
        ("What is the difference between the greatest and smallest 4-digit numbers?", "8,999", ["9,000", "9,998", "8,990"], "9,999 − 1,000 = 8,999."),
    ]
    items.extend(_item(q, a, wrong, why, "medium") for q, a, wrong, why in med_specs)

    hard_specs = [
        ("A 5-digit number has 4 in the ten-thousands place, 7 in the hundreds place and 2 in the ones place. The other digits are zero. What is the number?", "40,702", ["47,002", "40,720", "4,702"], "The place values are 40,000 + 700 + 2 = 40,702."),
        ("A number rounded to the nearest hundred is 6,300. Which could be the original number?", "6,348", ["6,251", "6,399", "6,405"], "Numbers from 6,250 through 6,349 round to 6,300."),
        ("Using 2, 4, 5 and 8 once each, what is the greatest 4-digit even number?", "8,542", ["8,524", "8,452", "5,842"], "To make the greatest even number, arrange the largest digits first and keep an even digit in the ones place: 8,542."),
        ("A number is divisible by 5 and 9. Which option could be the number?", "315", ["316", "320", "325"], "315 ends in 5 and its digit sum is 9."),
    ]
    items.extend(_item(q, a, wrong, why, "hard") for q, a, wrong, why in hard_specs)
    return items


def _data_handling():
    items = []
    easy_specs = [
        ("What is the average of 4, 6 and 8?", "6", ["5", "7", "8"], "(4 + 6 + 8) ÷ 3 = 6."),
        ("Find the range of 3, 5, 7 and 9.", "6", ["4", "7", "8"], "Range = highest − lowest = 9 − 3 = 6."),
        ("What is the mode of 2, 4, 4, 5, 7?", "4", ["2", "5", "7"], "4 appears most often."),
        ("What is the median of 1, 3, 5, 7, 9?", "5", ["3", "7", "9"], "The middle number in the ordered list is 5."),
        ("A pictograph uses one star for 2 books. What do 4 stars represent?", "8 books", ["4 books", "6 books", "10 books"], "4 × 2 = 8 books."),
        ("Which graph uses rectangular bars to compare values?", "Bar graph", ["Pictograph", "Number line", "Circle"], "A bar graph uses rectangular bars."),
        ("Find the total of 5, 6 and 4 observations.", "15", ["14", "16", "20"], "5 + 6 + 4 = 15."),
        ("Which value occurs most often in 3, 3, 4, 6, 6, 6, 8?", "6", ["3", "4", "8"], "6 occurs three times, more than any other value."),
    ]
    items.extend(_item(q, a, wrong, why, "easy") for q, a, wrong, why in easy_specs)

    medium_specs = [
        ("Find the mean of 8, 10, 12 and 14.", "11", ["10", "12", "13"], "The sum is 44; 44 ÷ 4 = 11."),
        ("Find the median of 4, 8, 10, 12, 16, 20.", "11", ["10", "12", "13"], "The middle two values are 10 and 12; their mean is 11."),
        ("The values are 2, 5, 5, 7, 9, 9, 9. What is the mode?", "9", ["5", "7", "2"], "9 appears three times, the most often."),
        ("A bar chart shows 12 students choosing cricket and 8 choosing football. How many students are represented?", "20", ["4", "18", "22"], "12 + 8 = 20 students."),
        ("The mean of 5 numbers is 6. What is their total?", "30", ["11", "25", "35"], "Total = mean × number of values = 6 × 5 = 30."),
        ("Find the range of 14, 22, 19, 31 and 17.", "17", ["14", "16", "18"], "The range is 31 − 14 = 17."),
        ("A pictograph shows 6 symbols, each representing 5 plants. How many plants are shown?", "30", ["11", "25", "35"], "6 × 5 = 30 plants."),
        ("What is the mean of 7, 9, 11, 13 and 15?", "11", ["9", "10", "12"], "The total is 55; 55 ÷ 5 = 11."),
    ]
    items.extend(_item(q, a, wrong, why, "medium") for q, a, wrong, why in medium_specs)

    hard_specs = [
        ("The mean of 4 numbers is 12. Three numbers are 8, 10 and 14. Find the fourth number.", "16", ["14", "18", "20"], "The total must be 4 × 12 = 48; the missing value is 48 − 32 = 16."),
        ("The median of five ordered numbers is 14. The numbers are 5, 9, __, 18, 21. What is the missing middle value?", "14", ["12", "15", "16"], "The median is the middle value in the ordered list."),
        ("The average of 6, 8, 10 and x is 9. Find x.", "12", ["10", "11", "13"], "The total must be 4 × 9 = 36; x = 36 − 24 = 12."),
        ("A class survey records 18, 22, 25 and 35 votes. How many more votes did the highest choice receive than the lowest?", "17", ["13", "15", "18"], "35 − 18 = 17 votes."),
    ]
    items.extend(_item(q, a, wrong, why, "hard") for q, a, wrong, why in hard_specs)
    return items


def _prime_time():
    items = []
    easy_specs = [
        ("Which is a prime number?", "17", ["9", "15", "21"], "17 has exactly two factors: 1 and 17."),
        ("Which number is a factor of 24?", "8", ["5", "7", "10"], "24 ÷ 8 = 3, so 8 is a factor."),
        ("What is the smallest prime number?", "2", ["0", "1", "3"], "2 is the smallest prime number."),
        ("Which of these numbers is composite?", "21", ["11", "13", "17"], "21 has factors 1, 3, 7 and 21."),
        ("Which number has exactly two factors?", "19", ["12", "15", "20"], "A number with exactly two factors is prime; 19 is prime."),
        ("Which is a multiple of 7?", "42", ["40", "41", "43"], "7 × 6 = 42."),
        ("Which is a common factor of 12 and 18?", "6", ["5", "8", "9"], "6 divides both 12 and 18."),
        ("Which number is divisible by 3?", "27", ["25", "26", "28"], "2 + 7 = 9, which is divisible by 3."),
    ]
    items.extend(_item(q, a, wrong, why, "easy") for q, a, wrong, why in easy_specs)

    medium_specs = [
        ("Find the HCF of 12 and 18.", "6", ["3", "9", "12"], "The common factors are 1, 2, 3 and 6; the greatest is 6."),
        ("Find the LCM of 4 and 6.", "12", ["8", "18", "24"], "12 is the smallest positive number divisible by both 4 and 6."),
        ("What is the prime factorisation of 18?", "2 × 3 × 3", ["2 × 9 × 2", "3 × 6", "2 × 3 × 2"], "18 = 2 × 9 = 2 × 3 × 3."),
        ("Find the HCF of 20 and 30.", "10", ["5", "15", "20"], "10 is the greatest number that divides both 20 and 30."),
        ("Find the LCM of 5 and 8.", "40", ["13", "20", "80"], "The first common multiple of 5 and 8 is 40."),
        ("Which pair is co-prime?", "8 and 15", ["6 and 9", "10 and 15", "12 and 18"], "8 and 15 have no common factor other than 1."),
        ("How many factors does 16 have?", "5", ["3", "4", "6"], "The factors are 1, 2, 4, 8 and 16."),
        ("Which is the prime factorisation of 36?", "2 × 2 × 3 × 3", ["4 × 9 × 2", "2 × 3 × 6", "3 × 12"], "36 = 4 × 9 = 2 × 2 × 3 × 3."),
    ]
    items.extend(_item(q, a, wrong, why, "medium") for q, a, wrong, why in medium_specs)

    hard_specs = [
        ("Two bells ring every 6 minutes and 8 minutes. If they ring together now, after how many minutes will they next ring together?", "24", ["14", "18", "48"], "The next common ringing time is LCM(6, 8) = 24 minutes."),
        ("Find the greatest number that divides 36 and 54 exactly.", "18", ["9", "12", "27"], "The HCF of 36 and 54 is 18."),
        ("A number has prime factorisation 2 × 2 × 3 × 5. What is the number?", "60", ["30", "50", "120"], "2 × 2 × 3 × 5 = 60."),
        ("What is the smallest number divisible by 3, 4 and 5?", "60", ["30", "45", "120"], "The LCM of 3, 4 and 5 is 60."),
    ]
    items.extend(_item(q, a, wrong, why, "hard") for q, a, wrong, why in hard_specs)
    return items


def _perimeter_area():
    items = []
    easy_specs = [
        ("A square has a side of 5 cm. What is its perimeter?", "20 cm", ["10 cm", "15 cm", "25 cm"], "Perimeter = 4 × side = 4 × 5 = 20 cm."),
        ("Find the area of a rectangle 6 cm long and 4 cm wide.", "24 cm²", ["10 cm²", "20 cm²", "28 cm²"], "Area = length × width = 6 × 4 = 24 cm²."),
        ("A triangle has sides 3 cm, 4 cm and 5 cm. Find its perimeter.", "12 cm", ["9 cm", "10 cm", "15 cm"], "Add the three sides: 3 + 4 + 5 = 12 cm."),
        ("What is the perimeter of a rectangle 8 cm long and 3 cm wide?", "22 cm", ["11 cm", "16 cm", "24 cm"], "Perimeter = 2 × (8 + 3) = 22 cm."),
        ("Find the area of a square with side 7 cm.", "49 cm²", ["14 cm²", "28 cm²", "56 cm²"], "Area = side × side = 7 × 7 = 49 cm²."),
        ("A rectangle has length 9 cm and width 2 cm. What is its area?", "18 cm²", ["11 cm²", "20 cm²", "22 cm²"], "Area = 9 × 2 = 18 cm²."),
        ("A square has a side of 6 m. What is its perimeter?", "24 m", ["12 m", "18 m", "36 m"], "Perimeter = 4 × 6 = 24 m."),
        ("What is the area of a rectangle 5 m by 3 m?", "15 m²", ["8 m²", "12 m²", "16 m²"], "Area = 5 × 3 = 15 m²."),
    ]
    items.extend(_item(q, a, wrong, why, "easy") for q, a, wrong, why in easy_specs)

    medium_specs = [
        ("A rectangle has perimeter 30 cm and length 9 cm. Find its width.", "6 cm", ["5 cm", "7 cm", "12 cm"], "30 = 2 × (9 + width), so 15 = 9 + width; width = 6 cm."),
        ("The area of a rectangle is 48 cm² and its width is 6 cm. Find its length.", "8 cm", ["7 cm", "9 cm", "12 cm"], "Length = area ÷ width = 48 ÷ 6 = 8 cm."),
        ("A square has perimeter 36 cm. Find its side length.", "9 cm", ["6 cm", "8 cm", "12 cm"], "Each side is 36 ÷ 4 = 9 cm."),
        ("A rectangular garden is 12 m long and 7 m wide. How much fencing is needed around it?", "38 m", ["19 m", "84 m", "42 m"], "Fencing equals perimeter: 2 × (12 + 7) = 38 m."),
        ("A floor is 8 m by 5 m. How many square metres of tile cover it?", "40 m²", ["13 m²", "26 m²", "45 m²"], "Floor area = 8 × 5 = 40 m²."),
        ("A square and a rectangle both have perimeter 24 cm. A rectangle has length 8 cm. Find its width.", "4 cm", ["3 cm", "6 cm", "8 cm"], "24 = 2 × (8 + width), so width = 4 cm."),
        ("A rectangular sheet is 10 cm by 6 cm. What is its perimeter?", "32 cm", ["16 cm", "30 cm", "60 cm"], "2 × (10 + 6) = 32 cm."),
        ("A square has area 64 cm². What is its perimeter?", "32 cm", ["16 cm", "24 cm", "36 cm"], "Side = √64 = 8 cm; perimeter = 4 × 8 = 32 cm."),
    ]
    items.extend(_item(q, a, wrong, why, "medium") for q, a, wrong, why in medium_specs)

    hard_specs = [
        ("A rectangular field is 20 m long. Its perimeter is 56 m. Find its area.", "160 m²", ["120 m²", "180 m²", "200 m²"], "Width = 28 − 20 = 8 m; area = 20 × 8 = 160 m²."),
        ("A square has the same area as a rectangle 4 cm by 9 cm. What is the square's side length?", "6 cm", ["5 cm", "8 cm", "9 cm"], "The rectangle area is 36 cm²; √36 = 6 cm."),
        ("A rectangle is 12 cm by 8 cm. Its length is reduced by 4 cm to make a square. What is the new square's perimeter?", "32 cm", ["24 cm", "36 cm", "40 cm"], "The new square has side 8 cm; perimeter = 4 × 8 = 32 cm.", "hard"),
        ("A path is 2 m wide all around the outside of a 10 m by 6 m garden. What is the outside perimeter?", "48 m", ["32 m", "40 m", "56 m"], "The outer rectangle is (10 + 4) m by (6 + 4) m, or 14 m by 10 m; perimeter = 2 × (14 + 10) = 48 m."),
    ]
    for spec in hard_specs:
        if len(spec) == 5:
            q, a, wrong, why, diff = spec
            items.append(_item(q, a, wrong, why, diff))
        else:
            q, a, wrong, why = spec
            items.append(_item(q, a, wrong, why, "hard"))
    return items


def _fractions():
    items = []
    easy_specs = [
        ("What is 1/2 + 1/4?", "3/4", ["1/4", "2/4", "4/4"], "1/2 = 2/4, so 2/4 + 1/4 = 3/4."),
        ("Which fraction is equivalent to 1/2?", "2/4", ["1/3", "3/4", "2/3"], "Multiply numerator and denominator by 2: 1/2 = 2/4."),
        ("What is 3/4 of 20?", "15", ["5", "10", "16"], "20 ÷ 4 × 3 = 15."),
        ("Which fraction is greater: 1/3 or 1/4?", "1/3", ["1/4", "They are equal", "Cannot compare"], "For unit fractions, the smaller denominator gives the larger fraction."),
        ("Simplify 2/6.", "1/3", ["1/2", "2/3", "3/2"], "Divide numerator and denominator by 2."),
        ("What is 2/5 of 15?", "6", ["5", "7", "10"], "15 ÷ 5 × 2 = 6."),
        ("Which fraction is equal to 3/6?", "1/2", ["1/3", "2/3", "3/4"], "Divide numerator and denominator by 3."),
        ("What is 1 − 1/4?", "3/4", ["1/4", "1/2", "4/4"], "1 = 4/4, and 4/4 − 1/4 = 3/4."),
    ]
    items.extend(_item(q, a, wrong, why, "easy") for q, a, wrong, why in easy_specs)

    medium_specs = [
        ("What is 2/3 + 1/6?", "5/6", ["3/9", "1/2", "4/6"], "2/3 = 4/6; 4/6 + 1/6 = 5/6."),
        ("What is 5/8 − 1/4?", "3/8", ["4/4", "1/8", "1/2"], "1/4 = 2/8; 5/8 − 2/8 = 3/8."),
        ("Which is the simplest form of 12/18?", "2/3", ["3/4", "4/5", "6/9"], "Divide numerator and denominator by 6."),
        ("A ribbon is 3/4 m long. If 1/8 m is cut off, how much remains?", "5/8 m", ["2/8 m", "4/8 m", "7/8 m"], "3/4 = 6/8; 6/8 − 1/8 = 5/8 m."),
        ("What is 2/5 + 1/10?", "1/2", ["3/15", "2/10", "3/5"], "2/5 = 4/10; 4/10 + 1/10 = 5/10 = 1/2."),
        ("Which is larger: 5/6 or 7/9?", "5/6", ["7/9", "They are equal", "Cannot compare"], "5/6 = 15/18 and 7/9 = 14/18, so 5/6 is larger."),
        ("A tank is 2/3 full. What fraction is empty?", "1/3", ["2/3", "1/2", "3/2"], "1 − 2/3 = 1/3."),
        ("What is 3/5 of 40?", "24", ["20", "25", "30"], "40 ÷ 5 × 3 = 24."),
    ]
    items.extend(_item(q, a, wrong, why, "medium") for q, a, wrong, why in medium_specs)

    hard_specs = [
        ("A class has 36 students. 2/3 are present. How many students are present?", "24", ["12", "18", "26"], "36 ÷ 3 × 2 = 24 students."),
        ("A water bottle is 3/5 full. After drinking 1/4 of the bottle's full capacity, what fraction remains?", "7/20", ["2/5", "9/20", "11/20"], "3/5 − 1/4 = 12/20 − 5/20 = 7/20."),
        ("A recipe needs 3/4 cup of flour. You make half the recipe. How much flour is needed?", "3/8 cup", ["1/4 cup", "1/2 cup", "2/3 cup"], "Half of 3/4 is 1/2 × 3/4 = 3/8 cup."),
        ("Ravi reads 2/5 of a book on Monday and 1/3 on Tuesday. What fraction of the book is left?", "4/15", ["7/15", "8/15", "2/15"], "Read = 2/5 + 1/3 = 6/15 + 5/15 = 11/15; left = 4/15."),
    ]
    items.extend(_item(q, a, wrong, why, "hard") for q, a, wrong, why in hard_specs)
    return items


def _constructions():
    items = []
    easy_specs = [
        ("Which instrument is used to draw a circle?", "Compass", ["Ruler", "Protractor", "Set square"], "A compass is used to draw circles and arcs."),
        ("Which tool measures an angle?", "Protractor", ["Ruler", "Compass", "Divider"], "A protractor measures angles in degrees."),
        ("Which tool is best for measuring a line segment?", "Ruler", ["Compass", "Eraser", "Protractor"], "A ruler measures length."),
        ("What is the diameter of a circle with radius 4 cm?", "8 cm", ["2 cm", "4 cm", "16 cm"], "Diameter = 2 × radius = 8 cm."),
        ("What is the radius of a circle with diameter 12 cm?", "6 cm", ["3 cm", "12 cm", "24 cm"], "Radius is half the diameter: 12 ÷ 2 = 6 cm."),
        ("Which instrument is used to draw a straight line?", "Ruler", ["Compass", "Protractor", "Divider"], "A ruler is used to draw and measure straight line segments."),
        ("A perpendicular line meets another line at what angle?", "90°", ["45°", "60°", "180°"], "Perpendicular lines meet at a right angle of 90°."),
        ("What is the fixed point at the centre of a circle called?", "Centre", ["Vertex", "Endpoint", "Chord"], "The centre is the fixed point equally distant from the circle."),
    ]
    items.extend(_item(q, a, wrong, why, "easy") for q, a, wrong, why in easy_specs)

    medium_specs = [
        ("A line segment is 8 cm long. What is the distance from its midpoint to one endpoint?", "4 cm", ["2 cm", "6 cm", "8 cm"], "The midpoint divides the segment into two equal parts: 8 ÷ 2 = 4 cm."),
        ("An angle of 70° is bisected. What is each smaller angle?", "35°", ["25°", "30°", "40°"], "An angle bisector divides an angle into two equal parts: 70 ÷ 2 = 35°."),
        ("A circle has radius 5 cm. What is its diameter?", "10 cm", ["5 cm", "15 cm", "25 cm"], "Diameter = 2 × 5 = 10 cm."),
        ("Which construction creates a line at 90° to a given line?", "Perpendicular construction", ["Parallel construction", "Circle construction", "Angle copy"], "Perpendicular lines meet at 90°."),
        ("An angle of 84° is divided into two equal angles. Find one part.", "42°", ["21°", "48°", "96°"], "84° ÷ 2 = 42°."),
        ("What is the length of a radius if the diameter is 18 cm?", "9 cm", ["6 cm", "12 cm", "36 cm"], "Radius = diameter ÷ 2 = 9 cm."),
        ("Which pair of tools is commonly used to construct a perpendicular bisector?", "Compass and ruler", ["Protractor and divider", "Two protractors", "Only a set square"], "Compass arcs and a ruler are used to construct a perpendicular bisector."),
        ("A 10 cm segment is divided into five equal parts. What is each part?", "2 cm", ["1 cm", "5 cm", "10 cm"], "10 ÷ 5 = 2 cm."),
    ]
    items.extend(_item(q, a, wrong, why, "medium") for q, a, wrong, why in medium_specs)

    hard_specs = [
        ("A circle's radius is doubled from 3 cm to 6 cm. What happens to its diameter?", "It doubles from 6 cm to 12 cm", ["It stays 6 cm", "It becomes 9 cm", "It becomes 18 cm"], "Diameter is twice the radius, so doubling the radius doubles the diameter."),
        ("A 120° angle is split into three equal angles. What is each angle?", "40°", ["30°", "45°", "60°"], "120° ÷ 3 = 40°."),
        ("Which set of lengths can form a triangle?", "4 cm, 5 cm and 6 cm", ["1 cm, 2 cm and 5 cm", "2 cm, 3 cm and 6 cm", "1 cm, 4 cm and 6 cm"], "The sum of any two sides must be greater than the third; 4 + 5 > 6, 4 + 6 > 5 and 5 + 6 > 4."),
        ("Two equal arcs are drawn from the endpoints of a line segment and joined. What line is constructed?", "Perpendicular bisector", ["Angle bisector", "Parallel line", "Diameter"], "The equal-radius arcs intersect on the perpendicular bisector of the segment."),
    ]
    items.extend(_item(q, a, wrong, why, "hard") for q, a, wrong, why in hard_specs)
    return items


def _symmetry():
    items = []
    easy_specs = [
        ("How many lines of symmetry does a square have?", "4", ["1", "2", "3"], "A square has two diagonals and two lines through the midpoints of opposite sides."),
        ("How many lines of symmetry does a rectangle that is not a square have?", "2", ["1", "3", "4"], "A non-square rectangle has one horizontal and one vertical line of symmetry."),
        ("How many lines of symmetry does an equilateral triangle have?", "3", ["1", "2", "4"], "Each vertex-to-opposite-side-midpoint line is a symmetry line."),
        ("How many lines of symmetry does a circle have?", "Infinitely many", ["1", "4", "8"], "Every diameter is a line of symmetry, so there are infinitely many."),
        ("How many lines of symmetry does a regular pentagon have?", "5", ["1", "2", "10"], "A regular pentagon has one symmetry line through each vertex and opposite side midpoint."),
        ("Which shape has no line of symmetry?", "A general scalene triangle", ["Square", "Circle", "Equilateral triangle"], "A scalene triangle has all sides and angles different, so it has no symmetry line."),
        ("How many lines of symmetry does an isosceles triangle (not equilateral) have?", "1", ["0", "2", "3"], "It has one line from the top vertex to the midpoint of the base."),
        ("How many lines of symmetry does a regular hexagon have?", "6", ["3", "4", "8"], "A regular hexagon has six symmetry lines."),
    ]
    items.extend(_item(q, a, wrong, why, "easy") for q, a, wrong, why in easy_specs)

    medium_specs = [
        ("What is the order of rotational symmetry of a square?", "4", ["1", "2", "8"], "A square matches itself four times in one full turn."),
        ("What is the order of rotational symmetry of an equilateral triangle?", "3", ["1", "2", "6"], "It matches itself three times in a full 360° turn."),
        ("What is the smallest angle of rotation that maps a square onto itself?", "90°", ["45°", "120°", "180°"], "360° ÷ 4 = 90°."),
        ("What is the smallest angle of rotation that maps an equilateral triangle onto itself?", "120°", ["60°", "90°", "180°"], "360° ÷ 3 = 120°."),
        ("A shape matches itself after a 180° turn. What is its rotational symmetry order?", "2", ["1", "3", "4"], "360° ÷ 180° = 2."),
        ("How many lines of symmetry does a regular octagon have?", "8", ["4", "6", "10"], "A regular n-sided polygon has n symmetry lines; for an octagon, n = 8."),
        ("A shape has rotational symmetry of order 6. What is its smallest rotation angle?", "60°", ["30°", "90°", "120°"], "360° ÷ 6 = 60°."),
        ("Which shape has rotational symmetry of order 2 but no reflection symmetry?", "A general parallelogram", ["Square", "Rectangle", "Equilateral triangle"], "A general parallelogram maps onto itself after 180° but usually has no reflection line."),
    ]
    items.extend(_item(q, a, wrong, why, "medium") for q, a, wrong, why in medium_specs)

    hard_specs = [
        ("A regular polygon has 9 lines of symmetry. How many sides does it have?", "9", ["8", "10", "18"], "A regular polygon has as many symmetry lines as sides."),
        ("A shape has rotational symmetry order 8. What is the smallest angle of rotation?", "45°", ["30°", "60°", "90°"], "360° ÷ 8 = 45°."),
        ("A regular polygon has a smallest rotation angle of 40°. How many sides does it have?", "9", ["8", "10", "12"], "360° ÷ 40° = 9; it is a regular nonagon."),
        ("A shape has 4 lines of symmetry and rotational symmetry order 4. Which shape could it be?", "Square", ["General rectangle", "Scalene triangle", "Regular pentagon"], "A square has four reflection lines and rotational symmetry order four."),
    ]
    items.extend(_item(q, a, wrong, why, "hard") for q, a, wrong, why in hard_specs)
    return items


def _integers():
    items = []
    easy_specs = [
        ("Which number is less than zero?", "-3", ["5", "2", "8"], "Negative numbers are less than zero."),
        ("Which is greater: -2 or -5?", "-2", ["-5", "They are equal", "0"], "-2 is to the right of -5 on the number line."),
        ("What is -5 + 8?", "3", ["-13", "-3", "13"], "Moving 8 places right from -5 gives 3."),
        ("What is the opposite of -7?", "7", ["-7", "0", "1"], "The opposite has the same distance from zero on the other side."),
        ("Which is the smallest integer?", "-9", ["-4", "0", "3"], "Among these, -9 is farthest left on the number line."),
        ("What is -4 + 4?", "0", ["-8", "4", "8"], "A number and its opposite add to zero."),
        ("Which integer is immediately to the left of 0?", "-1", ["1", "-2", "2"], "The integer just left of zero is -1."),
        ("What is 6 − 9?", "-3", ["3", "-15", "15"], "Subtracting 9 from 6 gives -3."),
    ]
    items.extend(_item(q, a, wrong, why, "easy") for q, a, wrong, why in easy_specs)

    medium_specs = [
        ("What is -7 + 12?", "5", ["-19", "-5", "19"], "Starting at -7 and moving 12 units right gives 5."),
        ("What is 8 + (-13)?", "-5", ["5", "-21", "21"], "8 − 13 = -5."),
        ("What is -6 − 4?", "-10", ["-2", "2", "10"], "Move 4 more units left from -6 to get -10."),
        ("What is -9 − (-3)?", "-6", ["-12", "6", "12"], "Subtracting -3 is the same as adding 3: -9 + 3 = -6."),
        ("Arrange -3, 2, -8 and 0 in ascending order. Which is second?", "-3", ["-8", "0", "2"], "The order is -8, -3, 0, 2."),
        ("The temperature is -2°C and rises by 7°C. What is the new temperature?", "5°C", ["-9°C", "-5°C", "9°C"], "-2 + 7 = 5°C."),
        ("A lift is on floor 3 and descends 8 floors. Which floor does it reach?", "-5", ["5", "-11", "11"], "3 − 8 = -5."),
        ("What is the difference between -4 and 6 on the number line?", "10", ["2", "-2", "-10"], "The distance is 6 − (-4) = 10 units."),
    ]
    items.extend(_item(q, a, wrong, why, "medium") for q, a, wrong, why in medium_specs)

    hard_specs = [
        ("The temperature is 4°C. It falls 9°C, then rises 6°C. What is the final temperature?", "1°C", ["-1°C", "7°C", "-11°C"], "4 − 9 + 6 = 1°C."),
        ("A submarine is 35 m below sea level and rises 18 m. What is its new position relative to sea level?", "-17 m", ["17 m", "-53 m", "53 m"], "-35 + 18 = -17 m."),
        ("Evaluate: -8 + 15 − 11.", "-4", ["4", "-34", "18"], "-8 + 15 = 7, and 7 − 11 = -4."),
        ("A bank balance is -₹250. A deposit of ₹400 is made and then ₹175 is withdrawn. What is the balance?", "-₹25", ["₹25", "₹325", "-₹825"], "-250 + 400 − 175 = -25."),
    ]
    items.extend(_item(q, a, wrong, why, "hard") for q, a, wrong, why in hard_specs)
    return items


CHAPTER_BUILDERS = [
    ("Patterns in Mathematics", _patterns),
    ("Lines and Angles", _angles),
    ("Number Play", _number_play),
    ("Data Handling and Presentation", _data_handling),
    ("Prime Time", _prime_time),
    ("Perimeter and Area", _perimeter_area),
    ("Fractions", _fractions),
    ("Playing with Constructions", _constructions),
    ("Symmetry", _symmetry),
    ("The Other Side of Zero", _integers),
]


def _validate_question_sets():
    for chapter_title, builder in CHAPTER_BUILDERS:
        questions = builder()
        counts = {level: sum(q[4] == level for q in questions) for level in ("easy", "medium", "hard")}
        if len(questions) != 20 or counts != {"easy": 8, "medium": 8, "hard": 4}:
            raise ValueError(f"Invalid question distribution for {chapter_title}: {counts}")


_validate_question_sets()

# Compatibility for curriculum_catalog.py, which expects (chapter title, question list).
CHAPTER_DATA = [(title, builder()) for title, builder in CHAPTER_BUILDERS]


def build_class6_questions():
    """Return tagged questions in easy → medium → hard order for each chapter."""
    questions = []
    difficulty_order = {"easy": 0, "medium": 1, "hard": 2}

    for chapter_number, (chapter_title, chapter_questions) in enumerate(CHAPTER_DATA, start=1):
        ordered = sorted(chapter_questions, key=lambda item: difficulty_order[item[4]])
        for question_number, (q, options, answer, why, difficulty) in enumerate(ordered, start=1):
            questions.append({
                "id": f"C6M{chapter_number:02d}-{question_number:03d}",
                "grade": "Class 6",
                "subject": "Mathematics",
                "chapter_id": f"c6-math-ch{chapter_number:02d}",
                "topic": chapter_title,
                "concept_id": f"c6-ch{chapter_number:02d}-q{question_number:03d}",
                "concept": chapter_title,
                "prerequisites": [],
                "difficulty": difficulty,
                "q": q,
                "options": options,
                "answer": answer,
                "why": why,
            })
    return questions
