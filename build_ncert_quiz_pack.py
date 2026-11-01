"""Build additive original NCERT-aligned MCQs for all missing Maths/Science chapters.

Run from the Vidhyastra project root after copying ncert_quiz_catalog.py:
    python build_ncert_quiz_pack.py

This creates question_banks/ncert_maths_science_classes6_10.json. It never edits
question_bank.json or any existing class6_content.py/class8_content.py questions.
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path
from typing import Any

from ncert_quiz_catalog import (
    MATHS_CHAPTERS,
    SCIENCE_CHAPTERS,
    _math_chapter_id,
    _science_chapter_id,
    syllabus_sources,
)

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "question_banks" / "ncert_maths_science_classes6_10.json"

# Each chapter has two tightly scoped concepts. Questions are original and are
# phrased from the chapter's learning themes rather than copied from textbooks.
# A concept is (term, definition, example, application).
CONCEPTS: dict[tuple[str, str, str], tuple[tuple[str, str, str, str], tuple[str, str, str, str]]] = {}


def add(grade: int, subject: str, title: str, c1: tuple[str, str, str, str], c2: tuple[str, str, str, str]) -> None:
    CONCEPTS[(f"Class {grade}", subject, title)] = (c1, c2)

# ---------------------------------------------------------------------------
# MATHEMATICS — CLASS 7 (Ganita Prakash, 8 chapters)
# ---------------------------------------------------------------------------
add(7,"Mathematics","Large Numbers Around Us",
    ("place value","the value of a digit determined by its position in a number","in 48,26,315 the digit 8 represents 8,00,000","read, compare and write large numbers accurately"),
    ("rounding and estimation","replacing a number with a nearby convenient value to make an estimate","rounding 7,849 to the nearest hundred gives 7,800","check whether a calculated result is reasonable"))
add(7,"Mathematics","Arithmetic Expressions",
    ("order of operations","the agreed sequence for evaluating operations in an expression","multiplication is completed before addition in 8 + 3 × 4","evaluate expressions consistently without changing their meaning"),
    ("use of brackets","brackets group parts of an expression that must be evaluated together","(8 + 3) × 4 groups the addition first","represent a calculation with the intended grouping"))
add(7,"Mathematics","A Peek Beyond the Point",
    ("decimal place value","the position of a digit to the right of the decimal point","in 5.27 the digit 7 is in the hundredths place","read, compare and calculate with decimal numbers"),
    ("decimal equivalence","different decimal forms can represent the same value","0.5, 0.50 and 0.500 represent the same number","compare quantities and convert between decimal forms"))
add(7,"Mathematics","Expressions Using Letter-Numbers",
    ("variable","a letter that represents a number that may be unknown or may change","in 4n + 3, n represents a number","write general rules and describe changing quantities"),
    ("coefficient","the numerical factor multiplying a variable in a term","the coefficient of x in 7x is 7","interpret and simplify algebraic expressions"))
add(7,"Mathematics","Parallel and Intersecting Lines",
    ("parallel lines","lines in one plane that do not meet however far they are extended","the opposite edges of a straight rectangular tabletop are parallel","recognise line relationships in diagrams and designs"),
    ("transversal","a line that intersects two or more other lines","a line crossing two parallel lines forms corresponding angles","use angle relationships to determine unknown angles"))
add(7,"Mathematics","Number Play",
    ("parity","the property of an integer being even or odd","18 is even because it is divisible by 2","reason about sums, products and number patterns"),
    ("divisibility rule","a test that determines whether one whole number divides another exactly","a whole number is divisible by 5 when its last digit is 0 or 5","test factors and multiples without carrying out long division"))
add(7,"Mathematics","A Tale of Three Intersecting Lines",
    ("triangle inequality","the sum of any two side lengths of a triangle must exceed the third side","lengths 4 cm, 5 cm and 6 cm can form a triangle","decide whether given lengths can form a triangle"),
    ("triangle construction","drawing a triangle accurately from specified side and angle information","a compass and ruler can construct a triangle when its three side lengths are given","construct and classify triangles from given measurements"))
add(7,"Mathematics","Working with Fractions",
    ("equivalent fractions","fractions with different numerators and denominators that represent the same value","2/3 and 4/6 are equivalent fractions","compare fractions and choose a useful common denominator"),
    ("common denominator","a shared denominator used to add or subtract fractions","1/2 and 1/3 can be rewritten as 3/6 and 2/6","add and subtract fractions with unlike denominators"))
# ---------------------------------------------------------------------------
# MATHEMATICS — CLASS 8 (Chapter 1 remains untouched)
# ---------------------------------------------------------------------------
add(8,"Mathematics","Power Play",
    ("exponent","a notation showing how many times a base is used as a factor","3^4 means 3 × 3 × 3 × 3","write repeated multiplication compactly"),
    ("law of exponents","a rule for simplifying expressions involving powers with related bases","2^3 × 2^2 = 2^5","simplify products and quotients of powers"))
add(8,"Mathematics","A Story of Numbers",
    ("rational number","a number expressible as a ratio of two integers with non-zero denominator","−3/4 is a rational number","represent and compare numbers in fraction and decimal form"),
    ("number pattern","a sequence whose terms follow a defined mathematical rule","2, 4, 8, 16 follows a doubling rule","predict later terms and explain how the pattern is formed"))
add(8,"Mathematics","Quadrilaterals",
    ("quadrilateral","a polygon with four sides and four interior angles","a rectangle is a quadrilateral","classify four-sided figures by their properties"),
    ("interior angle sum","the sum of the interior angles of a simple quadrilateral is 360 degrees","90° + 90° + 90° + 90° = 360° in a rectangle","find unknown angles in four-sided figures"))
add(8,"Mathematics","Number Play",
    ("prime factorisation","writing a composite whole number as a product of prime numbers","60 = 2 × 2 × 3 × 5","analyse factors and solve HCF or LCM problems"),
    ("divisibility pattern","a numerical pattern used to test exact division","a number whose digits add to a multiple of 3 is divisible by 3","reason about factors and multiples efficiently"))
add(8,"Mathematics","We Distribute, Yet Things Multiply",
    ("distributive property","multiplying a number by a sum is equivalent to multiplying each addend and adding","3(5 + 2) = 3×5 + 3×2","expand expressions and calculate efficiently"),
    ("factorisation","rewriting a sum or difference as a product of factors","6x + 12 = 6(x + 2)","identify common factors and simplify algebraic expressions"))
add(8,"Mathematics","Proportional Reasoning-1",
    ("ratio","a comparison of two quantities by division","the ratio 2:3 compares two parts with three parts","compare quantities and scale recipes or diagrams"),
    ("unit rate","a rate expressed for one unit of the second quantity","₹180 for 3 notebooks is ₹60 per notebook","compare prices and solve rate problems"))
add(8,"Mathematics","Fractions in Disguise",
    ("fraction equivalence","two fractions are equivalent when they represent the same rational value","3/4 = 6/8","rewrite rational quantities in convenient forms"),
    ("fraction operation","addition, subtraction, multiplication or division performed on rational parts","2/3 × 3/5 = 2/5","solve sharing, scaling and comparison problems"))
add(8,"Mathematics","The Baudhayana-Pythagoras Theorem",
    ("Pythagorean theorem","in a right triangle, the square of the hypotenuse equals the sum of the squares of the other two sides","a right triangle with legs 3 and 4 has hypotenuse 5","find missing side lengths in right triangles"),
    ("hypotenuse","the side opposite the right angle and the longest side of a right triangle","the side of length 5 is the hypotenuse in a 3-4-5 triangle","identify the side used in the Pythagorean relationship"))
add(8,"Mathematics","Proportional Reasoning-2",
    ("direct proportion","two quantities change in the same ratio so their quotient remains constant","at a fixed price, twice as many items cost twice as much","model scale, price and distance relationships"),
    ("inverse proportion","one quantity increases as the other decreases so their product remains constant","for a fixed journey, doubling speed halves travel time","solve shared-work and rate problems"))
add(8,"Mathematics","Exploring Some Geometric Themes",
    ("geometric property","a relationship that remains true for a defined class of shapes","opposite sides of a parallelogram are parallel","classify shapes and justify geometric conclusions"),
    ("angle relationship","a rule connecting two or more angles in a figure","vertically opposite angles are equal","calculate unknown angles from a diagram"))
add(8,"Mathematics","Tales by Dots and Lines",
    ("point","an exact location with no length, width or thickness","the point (2, 3) marks one location on a coordinate plane","represent positions and relationships precisely"),
    ("line relationship","a geometric relationship such as parallelism or intersection","two non-parallel lines in a plane meet at one point","interpret diagrams and locate intersections"))
add(8,"Mathematics","Algebra Play",
    ("algebraic expression","a combination of numbers, variables and operations without an equality sign","4x + 7 is an algebraic expression","represent general rules and simplify calculations"),
    ("linear equation","an equation in which the variable has degree one","2x + 3 = 11 is a linear equation","find an unknown using inverse operations"))
add(8,"Mathematics","Area",
    ("area","the measure of the surface enclosed by a two-dimensional figure","a rectangle 5 cm by 3 cm has area 15 cm²","compare surfaces and calculate the amount of covering material"),
    ("composite area","the total area of a shape formed by combining or removing simpler regions","an L-shaped region can be split into two rectangles","solve area problems by decomposition"))

# ---------------------------------------------------------------------------
# MATHEMATICS — CLASS 9 (Ganita Manjari, Parts I and II)
# ---------------------------------------------------------------------------
add(9,"Mathematics","Orienting Yourself: The Use of Coordinates",
    ("Cartesian coordinate","an ordered pair locating a point relative to two perpendicular axes","(−2, 3) is two units left and three units up from the origin","plot locations and describe positions on a plane"),
    ("midpoint","the point exactly halfway between the endpoints of a segment","the midpoint of (0,0) and (4,2) is (2,1)","find the centre of a segment and analyse geometric figures"))
add(9,"Mathematics","Introduction to Linear Polynomials",
    ("polynomial degree","the highest exponent of the variable with a non-zero coefficient","5x − 2 has degree 1","classify polynomials and describe their behaviour"),
    ("linear polynomial","a polynomial whose variable has degree one","3x + 7 is linear","model linear growth and relationships"))
add(9,"Mathematics","The World of Numbers",
    ("rational number","a number that can be written as p/q for integers p and q with q not zero","0.75 = 3/4 is rational","represent rational numbers and compare their decimal forms"),
    ("irrational number","a real number that cannot be expressed as a ratio of two integers","√2 is irrational","distinguish rational and irrational values on the number line"))
add(9,"Mathematics","Exploring Algebraic Identities",
    ("algebraic identity","an equality true for every permitted value of its variables","(a+b)^2 = a^2 + 2ab + b^2","expand and simplify algebraic expressions"),
    ("factorisation using identities","rewriting an expression as a product by recognising a standard identity","x^2 − 9 = (x−3)(x+3)","factor expressions and simplify rational forms"))
add(9,"Mathematics","I'm Up and Down, and Round and Round",
    ("cyclic pattern","a pattern that repeats after a fixed interval or number of steps","the sequence of days repeats every seven days","recognise repeating patterns and predict later positions"),
    ("rotation","a turn of a figure about a fixed centre through an angle","a quarter-turn is a rotation of 90 degrees","describe circular movement and rotational symmetry"))
add(9,"Mathematics","Measuring Space: Perimeter and Area",
    ("perimeter","the total distance around the boundary of a plane figure","a rectangle of length 6 and width 4 has perimeter 20 units","measure boundaries and solve fencing problems"),
    ("area","the amount of two-dimensional surface enclosed by a boundary","a 6 by 4 rectangle has area 24 square units","compare regions and calculate material requirements"))
add(9,"Mathematics","The Mathematics of Maybe: Introduction to Probability",
    ("sample space","the set of all possible outcomes of a random experiment","a coin toss has sample space {heads, tails}","list outcomes before calculating a probability"),
    ("theoretical probability","the ratio of favourable equally likely outcomes to all possible outcomes","the probability of heads on a fair coin is 1/2","quantify chance in simple random experiments"))
add(9,"Mathematics","Predicting What Comes Next: Exploring Sequences and Progressions",
    ("arithmetic progression","a sequence in which the difference between consecutive terms is constant","4, 7, 10, 13 has common difference 3","find later terms and model regular growth"),
    ("geometric progression","a sequence in which the ratio of consecutive non-zero terms is constant","2, 6, 18, 54 has common ratio 3","model repeated multiplication and scaling"))
add(9,"Mathematics","Propositions and their Converses",
    ("proposition","a declarative statement that has a definite truth value","the statement 'every square is a rectangle' is true","distinguish mathematical claims from questions or commands"),
    ("converse","a statement formed by reversing the hypothesis and conclusion of a conditional statement","the converse of 'if a figure is a square, it is a rectangle' is 'if it is a rectangle, it is a square'","test whether reversing a true statement remains true"))
add(9,"Mathematics","How Quantities Combine: Understanding Data",
    ("mean","the arithmetic average found by dividing the total by the number of observations","the mean of 2, 4 and 6 is 4","summarise numerical data and compare groups"),
    ("median","the middle observation after data are arranged in order","the median of 3, 5 and 9 is 5","describe the centre of a data set, especially when extreme values occur"))
add(9,"Mathematics","The World of Algorithms",
    ("algorithm","a finite ordered set of steps for solving a problem","a written method for finding the HCF of two numbers is an algorithm","design clear and repeatable mathematical procedures"),
    ("iteration","repeating a defined step until a stopping condition is met","repeatedly subtracting a smaller remainder in Euclid's method","solve problems through controlled repetition"))
add(9,"Mathematics","Quadrilaterals",
    ("parallelogram property","opposite sides of a parallelogram are parallel and equal in length","a parallelogram has both pairs of opposite sides parallel","identify and prove properties of four-sided figures"),
    ("midpoint theorem","the segment joining the midpoints of two sides of a triangle is parallel to the third side and half its length","a mid-segment in a triangle is parallel to the base","solve length and parallelism problems in triangles"))
add(9,"Mathematics","Two Variables, One Line",
    ("linear equation in two variables","an equation of the form ax + by + c = 0 where a and b are not both zero","2x + y = 5 is linear in x and y","represent relationships between two changing quantities"),
    ("slope","the ratio of vertical change to horizontal change between two points on a line","a line rising 2 units for every 1 unit across has slope 2","interpret steepness and rates of change on a graph"))
add(9,"Mathematics","Math of Space: Surface Area and Volume",
    ("surface area","the total area covering the outside of a three-dimensional object","a cube of side 2 has total surface area 24 square units","calculate material needed to cover a solid"),
    ("volume","the amount of three-dimensional space occupied by a solid","a cube of side 2 has volume 8 cubic units","calculate capacity and compare solid objects"))

# ---------------------------------------------------------------------------
# MATHEMATICS — CLASS 10 (NCERT textbook chapter structure)
# ---------------------------------------------------------------------------
add(10,"Mathematics","Real Numbers",
    ("Euclid's division lemma","for positive integers a and b, a = bq + r with 0 ≤ r < b","29 = 5×5 + 4","find HCFs and reason about integer division"),
    ("prime factorisation","writing a positive integer as a product of prime factors","180 = 2² × 3² × 5","use prime factors to study HCF, LCM and number properties"))
add(10,"Mathematics","Polynomials",
    ("zero of a polynomial","a value of the variable for which the polynomial evaluates to zero","x−4 has zero 4","connect algebraic expressions with their graphs"),
    ("relationship between zeroes and coefficients","for a quadratic ax²+bx+c, the sum of zeroes is −b/a and product is c/a","for x²−5x+6, the zeroes sum to 5 and multiply to 6","check or construct polynomial relationships"))
add(10,"Mathematics","Pair of Linear Equations in Two Variables",
    ("pair of linear equations","two linear equations involving the same two variables","x+y=7 and x−y=1 form a pair","model situations with two unknown quantities"),
    ("elimination method","solving a pair by adding or subtracting equations to remove one variable","adding x+y=7 and x−y=1 gives 2x=8, so x=4 and y=3","find a common solution systematically"))
add(10,"Mathematics","Quadratic Equations",
    ("quadratic equation","an equation that can be written as ax²+bx+c=0 with a not zero","x²−5x+6=0 is quadratic","model problems whose unknown appears squared"),
    ("discriminant","the value b²−4ac that determines the nature of quadratic roots","for x²−4x+4, the discriminant is zero","predict whether roots are distinct, equal or non-real"))
add(10,"Mathematics","Arithmetic Progressions",
    ("common difference","the constant amount added to each term of an arithmetic progression","in 5, 8, 11, 14 the common difference is 3","identify and describe a regular additive pattern"),
    ("nth term of an AP","the term a_n = a + (n−1)d for first term a and common difference d","for 2, 5, 8, the tenth term is 29","find a distant term without listing every previous term"))
add(10,"Mathematics","Triangles",
    ("similar triangles","triangles with equal corresponding angles and proportional corresponding sides","triangles with side ratios 3:4:5 and 6:8:10 are similar","use proportional sides to find unknown lengths"),
    ("Pythagoras relationship","in a right triangle the square of the hypotenuse equals the sum of the squares of the legs","5² = 3² + 4²","verify right triangles and calculate missing sides"))
add(10,"Mathematics","Coordinate Geometry",
    ("distance formula","the distance between (x1,y1) and (x2,y2) is √((x2−x1)²+(y2−y1)²)","the distance from (0,0) to (3,4) is 5","measure straight-line distances on a coordinate plane"),
    ("section formula","a formula for coordinates of a point dividing a segment in a given ratio","the midpoint divides a segment in the ratio 1:1","find points between two known endpoints"))
add(10,"Mathematics","Introduction to Trigonometry",
    ("trigonometric ratio","a ratio of two sides of a right triangle for a chosen acute angle","sin θ = opposite/hypotenuse","relate angles and side lengths in right triangles"),
    ("identity","an equality among trigonometric ratios that holds for permitted angles","sin²θ + cos²θ = 1","simplify expressions and verify trigonometric relationships"))
add(10,"Mathematics","Some Applications of Trigonometry",
    ("angle of elevation","the angle between the horizontal and an upward line of sight","looking up at the top of a tower forms an angle of elevation","model heights and distances using right triangles"),
    ("angle of depression","the angle between the horizontal and a downward line of sight","looking down from a balcony at a car forms an angle of depression","solve line-of-sight distance problems"))
add(10,"Mathematics","Circles",
    ("tangent","a line that touches a circle at exactly one point","a tangent is perpendicular to the radius at the point of contact","reason about tangent lengths and radii"),
    ("radius-tangent theorem","the radius drawn to the point of tangency is perpendicular to the tangent","the angle between a radius and tangent at contact is 90°","use right-triangle reasoning in circle problems"))
add(10,"Mathematics","Areas Related to Circles",
    ("circumference","the distance around a circle, equal to 2πr","a circle of radius 7 cm has circumference 14π cm","measure circular boundaries"),
    ("sector area","the area of a region bounded by two radii and an arc","a 90° sector is one quarter of a circle's area","find areas of slices and portions of circles"))
add(10,"Mathematics","Surface Areas and Volumes",
    ("curved surface area","the area of the curved outer surface of a solid, excluding its flat ends","a cylinder's curved surface area is 2πrh","calculate material for curved coverings"),
    ("volume of a solid","the three-dimensional capacity or space occupied by an object","a cylinder has volume πr²h","calculate capacity and compare solid shapes"))
add(10,"Mathematics","Statistics",
    ("grouped frequency distribution","a table arranging observations into class intervals with frequencies","a table may show how many scores lie between 0 and 10","organise and analyse large data sets"),
    ("cumulative frequency","the running total of frequencies up to a given class","the cumulative frequency at the third class includes the first three class frequencies","read ogives and estimate medians"))
add(10,"Mathematics","Probability",
    ("empirical probability","an estimate of probability based on observed outcomes","if a coin lands heads 48 times in 100 tosses, the empirical probability is 0.48","use repeated trials to estimate chance"),
    ("equally likely outcomes","outcomes that have the same chance of occurring","each face of a fair six-sided die is equally likely","calculate theoretical probability for fair experiments"))

# ---------------------------------------------------------------------------
# SCIENCE — CLASS 7 (Curiosity)
# ---------------------------------------------------------------------------
add(7,"Science","The Ever-Evolving World of Science",
    ("observation","carefully noticing and recording features or changes using senses or instruments","recording that a shadow becomes longer in the evening","collect evidence before forming an explanation"),
    ("hypothesis","a testable proposed explanation for an observation","predicting that a plant near a window will grow towards light","plan an investigation that can support or reject an idea"))
add(7,"Science","Exploring Substances: Acidic, Basic, and Neutral",
    ("acidic substance","a substance that shows acidic behaviour and turns blue litmus red","lemon juice turns blue litmus red","identify and compare common household substances safely"),
    ("neutralisation","a reaction between an acid and a base that produces salt and water","an acid reacting with a base can form salt and water","explain how acidity or basicity can be reduced"))
add(7,"Science","Electricity: Circuits and their Components",
    ("closed circuit","a complete conducting path that allows electric current to flow","a connected cell, wire and bulb can form a closed circuit","diagnose why a bulb does or does not glow"),
    ("conducting material","a material that allows electric charge to pass through it relatively easily","copper is used in connecting wires","choose suitable materials for electrical connections"))
add(7,"Science","The World of Metals and Non-metals",
    ("metallic property","a characteristic such as lustre, malleability or electrical conductivity","copper can be drawn into wires","compare materials and select them for particular uses"),
    ("non-metallic property","a characteristic commonly associated with non-metals, such as brittleness in solid form or poor conductivity","sulphur is a non-metal and is not malleable","distinguish materials using observed properties"))
add(7,"Science","Changes Around Us: Physical and Chemical",
    ("physical change","a change in form or state that does not create a new substance","ice melting into liquid water","distinguish changes of state and shape from chemical reactions"),
    ("chemical change","a change in which one or more new substances are formed","iron rusting forms iron oxide","identify evidence of a chemical reaction"))
add(7,"Science","Adolescence: A Stage of Growth and Change",
    ("puberty","the stage when the body undergoes changes leading towards reproductive maturity","a growth spurt can occur during puberty","understand normal physical changes during adolescence"),
    ("hormone","a chemical messenger produced by glands and carried to target organs","insulin helps regulate blood glucose","explain how body changes are coordinated"))
add(7,"Science","Heat Transfer in Nature",
    ("conduction","transfer of heat through a material without bulk movement of the material","a metal spoon becomes warm when placed in hot tea","explain heat transfer through solids"),
    ("convection","transfer of heat through movement in liquids or gases","warm air rising and cool air sinking forms a convection current","explain circulation in fluids and air"))
add(7,"Science","Measurement of Time and Motion",
    ("periodic motion","motion that repeats itself after equal intervals of time","a pendulum swinging repeatedly","measure time using repeating events"),
    ("speed","distance travelled per unit time","a cyclist travels 60 metres in 10 seconds at 6 m/s","compare how fast objects move"))
add(7,"Science","Life Processes in Animals",
    ("digestion","breaking down complex food into simpler soluble substances","enzymes help break down food in the digestive system","explain how food becomes available for the body"),
    ("respiration","the cellular process that releases energy from food molecules","cells release energy from glucose during respiration","connect breathing and energy release in living organisms"))
add(7,"Science","Life Processes in Plants",
    ("photosynthesis","the process by which green plants use light energy to make food from carbon dioxide and water","a green leaf makes sugars in sunlight","explain how plants make food and release oxygen"),
    ("transport in plants","movement of water, minerals and prepared food through plant tissues","xylem carries water from roots towards leaves","explain how materials move through a plant"))
add(7,"Science","Light: Shadows and Reflections",
    ("reflection","the bouncing back of light from a surface","a plane mirror forms an image by reflecting light","explain image formation in mirrors"),
    ("opaque object","an object that does not allow light to pass through it","a wooden board blocks light and can form a shadow","predict when and how a shadow forms"))
add(7,"Science","Earth, Moon, and the Sun",
    ("rotation","the spinning of a body about its own axis","Earth's rotation causes the cycle of day and night","explain daily changes in the apparent position of the Sun"),
    ("revolution","the movement of one body around another along an orbit","Earth revolves around the Sun","explain yearly cycles and changing positions in the sky"))

# ---------------------------------------------------------------------------
# SCIENCE — CLASS 8 (Curiosity)
# ---------------------------------------------------------------------------
add(8,"Science","Exploring the Investigative World of Science",
    ("variable","a factor that can be changed, measured or kept constant in an investigation","the amount of light supplied to plants","design a fair test and interpret its results"),
    ("controlled experiment","an investigation that changes one factor while keeping other relevant factors constant","comparing two plants while keeping soil and water the same","identify whether evidence supports a causal conclusion"))
add(8,"Science","The Invisible Living World: Beyond Our Naked Eye",
    ("microorganism","a living organism too small to be seen clearly without magnification","many bacteria are microscopic","explain why microscopes are useful in studying life"),
    ("cell","the basic structural and functional unit of living organisms","onion peel cells can be seen under a microscope","relate cell structure to the organisation of living things"))
add(8,"Science","Health: The Ultimate Treasure",
    ("balanced diet","a diet containing required nutrients, fibre and water in suitable amounts","a meal with grains, pulses, vegetables and fruit","explain how food supports growth and health"),
    ("communicable disease","a disease that can spread from one host to another by a route of transmission","influenza can spread through respiratory droplets","identify prevention measures such as hygiene and vaccination"))
add(8,"Science","Electricity: Magnetic and Heating Effects",
    ("heating effect of current","electrical energy converted into heat when current passes through resistance","a toaster wire becomes hot when current flows","explain the working of electrical heating devices"),
    ("electromagnet","a magnet produced by electric current flowing through a coil, often wound around an iron core","a current-carrying coil around an iron nail can attract pins","explain temporary magnets and their uses"))
add(8,"Science","Exploring Forces",
    ("force","a push or pull that can change an object's motion or shape","pushing a stationary trolley can set it in motion","analyse how interactions change motion"),
    ("balanced forces","forces whose resultant is zero so they do not change the state of motion","equal opposite forces on a stationary book keep it at rest","distinguish balanced and unbalanced interactions"))
add(8,"Science","Pressure, Winds, Storms, and Cyclones",
    ("pressure","force acting per unit area","the same force produces greater pressure on a smaller area","explain pressure in solids, liquids and gases"),
    ("air pressure difference","a difference in atmospheric pressure that drives air from higher towards lower pressure","unequal heating of air can create winds","explain wind formation and storm development"))
add(8,"Science","Particulate Nature of Matter",
    ("particle model","the idea that matter is made of tiny particles with spaces and motion between them","a smell spreads through a room as gas particles move","explain diffusion and changes in state"),
    ("diffusion","spreading of particles from a region of higher concentration to lower concentration","ink gradually spreads through still water","explain mixing in gases and liquids"))
add(8,"Science","Nature of Matter: Elements, Compounds, and Mixtures",
    ("element","a pure substance made of only one kind of atom","copper is an element","distinguish elements from compounds and mixtures"),
    ("compound","a pure substance formed when elements combine chemically in a fixed ratio","water contains hydrogen and oxygen chemically combined","interpret chemical composition and formulae"))
add(8,"Science","The Amazing World of Solutes, Solvents, and Solutions",
    ("solute","the substance that dissolves in a solvent to form a solution","sugar is the solute in sugar water","identify the components of a solution"),
    ("concentration","the amount of solute present in a given amount of solution","a solution with more dissolved salt per volume is more concentrated","compare solutions and describe dilution"))
add(8,"Science","Light: Mirrors and Lenses",
    ("plane mirror image","an image in a plane mirror that is virtual, upright and the same size as the object","a person sees an upright image of the same height in a plane mirror","describe images formed by mirrors"),
    ("convex lens","a lens thicker at the centre that converges parallel rays of light","a magnifying glass uses a convex lens","explain image formation and common lens applications"))
add(8,"Science","Keeping Time with the Skies",
    ("apparent motion","the observed movement of a celestial object across the sky caused partly by Earth's rotation","the Sun appears to move from east to west during a day","interpret regular patterns in the sky"),
    ("lunar phase","the changing visible shape of the Moon's illuminated portion as seen from Earth","a crescent Moon shows only part of its lit side","explain the changing appearance of the Moon"))
add(8,"Science","How Nature Works in Harmony",
    ("ecosystem","a community of organisms interacting with one another and with their physical environment","a pond contains plants, animals, water and microorganisms","analyse relationships among organisms and surroundings"),
    ("food web","a network of interconnected food chains in an ecosystem","grass may feed insects and rabbits, which feed different predators","predict how changes to one population affect others"))
add(8,"Science","Our Home: Earth, a Unique Life Sustaining Planet",
    ("habitable conditions","environmental conditions that allow life to exist, such as liquid water and suitable temperatures","Earth has liquid water on much of its surface","identify factors that support life on a planet"),
    ("atmosphere","the layer of gases surrounding a planet","Earth's atmosphere contains nitrogen and oxygen","explain how a planet's gaseous envelope supports life"))

# ---------------------------------------------------------------------------
# SCIENCE — CLASS 9 (Exploration)
# ---------------------------------------------------------------------------
add(9,"Science","Exploration: Entering the World of Secondary Science",
    ("scientific inquiry","a systematic process of asking questions, testing ideas and analysing evidence","investigating why a plant bends towards light","develop explanations that can be checked with evidence"),
    ("evidence-based conclusion","a conclusion supported by observations or measurements","a table of repeated measurements supports a claim about growth","separate reliable findings from unsupported guesses"))
add(9,"Science","Cell: The Building Block of Life",
    ("cell membrane","a selectively permeable boundary that controls movement into and out of a cell","water and some dissolved substances can cross the membrane","explain exchange between a cell and its surroundings"),
    ("nucleus","a cell structure containing genetic material and helping regulate cell activities","a stained onion cell often shows a visible nucleus","relate cell organisation to living functions"))
add(9,"Science","Tissues in Action",
    ("tissue","a group of similar cells working together to perform a function","muscle tissue helps produce movement","explain how cells organise into larger structures"),
    ("specialisation","the adaptation of a cell's structure to perform a particular role","a nerve cell has extensions that help transmit signals","connect structure and function in organisms"))
add(9,"Science","Describing Motion Around Us",
    ("displacement","the change in position in a specified direction from start to finish","walking 3 m east and then 3 m west gives zero displacement","distinguish straight-line change in position from total path length"),
    ("acceleration","the rate of change of velocity with time","a vehicle speeding up from rest has positive acceleration","interpret changes in motion using data and graphs"))
add(9,"Science","Exploring Mixtures and their Separation",
    ("mixture","a physical combination of substances that retain their identities","sand and salt mixed together form a mixture","choose methods to separate useful components"),
    ("filtration","separation of an insoluble solid from a fluid using a porous barrier","filter paper separates sand from water","select a separation method based on particle properties"))
add(9,"Science","How Forces Affect Motion",
    ("Newton's laws of motion","principles relating force, mass and changes in motion","a trolley accelerates more when a greater net force acts on it","explain motion using the relationship between force and mass"),
    ("inertia","the tendency of an object to resist a change in its state of motion","a passenger leans forward when a moving bus stops suddenly","explain everyday effects of changing motion"))
add(9,"Science","Work, Energy, and Simple Machines",
    ("work","in physics, work is done when a force causes displacement in its direction","lifting a box upward transfers energy by doing work","calculate and interpret work in mechanical situations"),
    ("mechanical advantage","the ratio of output force to input force for a machine","a lever can multiply the applied force","explain how simple machines make tasks easier"))
add(9,"Science","Journey Inside the Atom",
    ("atomic nucleus","the small dense central region of an atom containing protons and neutrons","most of an atom's mass is concentrated in its nucleus","describe the internal structure of atoms"),
    ("electron","a negatively charged subatomic particle found outside the nucleus","an atom has electrons arranged around its nucleus","relate subatomic particles to atomic structure"))
add(9,"Science","Atomic Foundations of Matter",
    ("molecule","a group of two or more atoms chemically bonded together","an oxygen molecule contains two oxygen atoms","interpret how atoms form substances"),
    ("law of conservation of mass","mass is conserved in a chemical reaction in a closed system","the total mass before and after a reaction remains the same","reason about chemical equations and measured masses"))
add(9,"Science","Sound Waves: Characteristics and Applications",
    ("frequency","the number of complete vibrations or wave cycles per second","a 200 Hz tone has 200 cycles per second","relate frequency to pitch and wave behaviour"),
    ("amplitude","the maximum displacement of a vibrating particle from its equilibrium position","a larger sound-wave amplitude generally corresponds to a louder sound","compare wave strength and sound intensity"))
add(9,"Science","Reproduction: How Life Continues",
    ("sexual reproduction","reproduction involving fusion of male and female gametes","fertilisation forms a zygote","explain inheritance and variation in offspring"),
    ("asexual reproduction","reproduction from one parent without fusion of gametes","budding in yeast can produce a new individual","compare reproductive strategies in organisms"))
add(9,"Science","Patterns in Life: Diversity and Classification",
    ("classification","organising organisms into groups based on shared characteristics","organisms can be grouped by cell type and body organisation","compare biodiversity systematically"),
    ("adaptation","an inherited feature that helps an organism survive or reproduce in its environment","a cactus has structures that reduce water loss","relate organism features to environmental conditions"))
add(9,"Science","Earth as a System: Energy, Matter, and Life",
    ("Earth system","the interacting spheres of air, water, land, ice and living things","the water cycle links the atmosphere, land and oceans","explain how changes in one Earth sphere affect others"),
    ("biogeochemical cycle","the movement of elements through living organisms and the physical environment","carbon moves among air, organisms, soil and oceans","trace matter through natural systems"))

# ---------------------------------------------------------------------------
# SCIENCE — CLASS 10 (current NCERT 13-chapter Science book structure)
# ---------------------------------------------------------------------------
add(10,"Science","Chemical Reactions and Equations",
    ("balanced chemical equation","a chemical equation with equal numbers of each type of atom on both sides","2H₂ + O₂ → 2H₂O is balanced","represent reactions while obeying conservation of mass"),
    ("oxidation and reduction","processes involving electron transfer or changes in oxidation state","copper oxide can be reduced to copper by hydrogen","identify redox changes in chemical reactions"))
add(10,"Science","Acids, Bases and Salts",
    ("acid","a substance that produces hydrogen ions in aqueous solution","dilute hydrochloric acid turns blue litmus red","identify acidic substances and explain their reactions"),
    ("neutralisation","reaction of an acid with a base to form salt and water","hydrochloric acid reacts with sodium hydroxide to form sodium chloride and water","explain everyday uses of neutralisation"))
add(10,"Science","Metals and Non-metals",
    ("reactivity series","an arrangement of metals in order of their chemical reactivity","zinc is more reactive than copper","predict displacement reactions"),
    ("corrosion","gradual damage to a metal through chemical reaction with its environment","iron rusts in the presence of oxygen and moisture","identify ways to protect metals"))
add(10,"Science","Carbon and its Compounds",
    ("covalent bond","a chemical bond formed when atoms share electron pairs","carbon forms covalent bonds in methane","explain bonding and structures of carbon compounds"),
    ("homologous series","a family of organic compounds with the same functional group and successive members differing by CH₂","methane, ethane and propane are alkanes","recognise patterns in organic compounds"))
add(10,"Science","Life Processes",
    ("nutrition","the process of obtaining and using food for energy, growth and repair","green plants make food by photosynthesis","compare modes of nutrition in organisms"),
    ("transportation","movement of materials such as water, nutrients and gases within an organism","blood transports oxygen and nutrients in humans","explain how organisms distribute essential substances"))
add(10,"Science","Control and Coordination",
    ("reflex action","a rapid automatic response to a stimulus, often coordinated through the spinal cord","withdrawing a hand from a hot object","explain quick protective responses"),
    ("hormonal coordination","control of body functions by chemical messengers released by endocrine glands","insulin helps regulate blood glucose","compare nervous and hormonal control"))
add(10,"Science","How Do Organisms Reproduce?",
    ("fertilisation","fusion of male and female gametes to form a zygote","a sperm and ovum fuse in human reproduction","explain the start of development in sexual reproduction"),
    ("vegetative propagation","asexual reproduction in plants through roots, stems or leaves","a potato can grow from an eye on its tuber","compare natural and artificial plant reproduction"))
add(10,"Science","Heredity",
    ("gene","a unit of heredity consisting of a segment of DNA that influences a trait","a gene can affect the form of a seed","explain how traits pass from parents to offspring"),
    ("dominant allele","an allele expressed in a heterozygote under simple Mendelian inheritance","a dominant allele can mask a recessive allele","predict inheritance patterns in simple crosses"))
add(10,"Science","Light: Reflection and Refraction",
    ("law of reflection","the angle of incidence equals the angle of reflection","a ray striking a plane mirror at 30° to the normal reflects at 30°","trace reflected rays and locate images"),
    ("refraction","change in direction of light when it passes obliquely between media with different optical densities","a pencil appears bent at the water surface","explain image formation by lenses and apparent depth"))
add(10,"Science","The Human Eye and the Colourful World",
    ("accommodation","the eye lens changes curvature to focus objects at different distances on the retina","ciliary muscles adjust the lens for near vision","explain how the eye focuses images"),
    ("dispersion","separation of white light into its component colours","a prism can produce a spectrum","explain the formation of a spectrum and natural colour effects"))
add(10,"Science","Electricity",
    ("electric current","the rate of flow of electric charge through a conductor","a current of 2 A means 2 coulombs pass each second","calculate charge flow and analyse circuits"),
    ("Ohm's law","at constant temperature, current through a conductor is proportional to potential difference across it","doubling voltage across an ohmic resistor doubles current","relate voltage, current and resistance"))
add(10,"Science","Magnetic Effects of Electric Current",
    ("magnetic field","the region around a magnet or current-carrying conductor where magnetic force can be detected","iron filings show the pattern around a bar magnet","represent magnetic interactions and field directions"),
    ("electromagnetic induction","production of an induced current when magnetic flux linked with a circuit changes","moving a magnet relative to a coil can induce current","explain the basic principle of electric generators"))
add(10,"Science","Our Environment",
    ("food chain","a sequence showing transfer of food energy from one organism to another","grass → deer → tiger is a food chain","trace energy transfer in an ecosystem"),
    ("biodegradable waste","waste that can be broken down by microorganisms into simpler substances","vegetable peels decompose naturally","choose responsible waste-management methods"))


def _seed_group(grade: str, subject: str, chapter_id: str, title: str,
                ordinal: int) -> tuple[tuple[str, str, str, str], tuple[str, str, str, str]]:
    try:
        return CONCEPTS[(grade, subject, title)]
    except KeyError as exc:
        raise KeyError(f"No original concept seed for {grade} / {subject} / {chapter_id} / {title}") from exc


def _stable_shuffle(options: list[str], seed_text: str) -> list[str]:
    unique: list[str] = []
    for item in options:
        if item and item not in unique:
            unique.append(item)
    filler = [
        "A guess made without checking any evidence",
        "A description of an unrelated process",
        "A value chosen without using the stated information",
        "A rule that contradicts the conditions in the question",
    ]
    for item in filler:
        if len(unique) >= 4:
            break
        if item not in unique:
            unique.append(item)
    if len(unique) < 4:
        raise ValueError(f"Cannot construct four distinct options for {seed_text}")
    result = unique[:4]
    seed = sum((i + 1) * ord(ch) for i, ch in enumerate(seed_text))
    random.Random(seed).shuffle(result)
    return result


def _make_question(qid: str, grade: str, subject: str, chapter_id: str,
                   chapter_title: str, difficulty: str, prompt: str,
                   answer: str, distractors: list[str], why: str,
                   concept_id: str, concept: str) -> dict[str, Any]:
    options = _stable_shuffle([answer] + distractors, qid + prompt)
    return {
        "id": qid,
        "grade": grade,
        "subject": subject,
        "chapter_id": chapter_id,
        "topic": "Chapter Assessment",
        "concept_id": concept_id,
        "concept": concept,
        "prerequisites": [],
        "difficulty": difficulty,
        "q": prompt,
        "options": options,
        "answer": answer,
        "why": why,
    }


def build_chapter_questions(grade: str, subject: str, chapter_id: str,
                            title: str, ordinal: int) -> list[dict[str, Any]]:
    """Return one fixed 20-item chapter assessment with an exact 8/8/4 split."""
    concepts = _seed_group(grade, subject, chapter_id, title, ordinal)
    (t1, d1, e1, a1), (t2, d2, e2, a2) = concepts
    definitions = [d1, d2]
    examples = [e1, e2]
    applications = [a1, a2]
    terms = [t1, t2]
    questions: list[dict[str, Any]] = []
    prefix = f"N26C{grade.split()[-1]}{'M' if subject == 'Mathematics' else 'S'}CH{ordinal:02d}"

    # 8 easy: meaning, example, accurate statement and purpose for each concept.
    easy_specs = [
        (f"What does {t1} mean in {title}?", d1, [d2, "A guess made without checking evidence", "A description of an unrelated process"], f"{t1.capitalize()} means {d1}", t1, 1),
        (f"Which situation is the clearest example of {t1} in {title}?", e1, [e2, "A result selected before any observation", "A method that ignores the quantities in the problem"], f"The example illustrates {t1}: {e1}", t1, 2),
        (f"Which statement about {t1} is correct in {title}?", d1, [d2, "It is unrelated to the chapter's main ideas", "It is always decided by guessing"], f"The correct statement describes {t1}: {d1}", t1, 3),
        (f"Why is {t1} useful when studying {title}?", a1, [a2, "It replaces the need to examine the given information", "It guarantees an answer without a method"], f"{t1.capitalize()} is useful because it helps learners {a1}", t1, 4),
        (f"What is meant by {t2} in {title}?", d2, [d1, "A guess made without checking evidence", "A rule that contradicts the stated conditions"], f"{t2.capitalize()} means {d2}", t2, 5),
        (f"Which situation is an example of {t2} in {title}?", e2, [e1, "A claim made before collecting observations", "A calculation that ignores the units or conditions"], f"The example illustrates {t2}: {e2}", t2, 6),
        (f"Which statement about {t2} is accurate in {title}?", d2, [d1, "It applies only when the question is ignored", "It is an unsupported conclusion"], f"The correct statement describes {t2}: {d2}", t2, 7),
        (f"Why is {t2} useful when studying {title}?", a2, [a1, "It allows the learner to skip all reasoning", "It is a rule for a different subject"], f"{t2.capitalize()} is useful because it helps learners {a2}", t2, 8),
    ]
    for prompt, answer, wrong, why, term, n in easy_specs:
        questions.append(_make_question(
            f"{prefix}-E{n:02d}", grade, subject, chapter_id, title,
            "easy", prompt, answer, wrong, why,
            f"{chapter_id}-concept-{1 if term == t1 else 2}", term
        ))

    # 8 medium: choose and apply the correct idea to a short described task.
    medium_specs = [
        (f"In {title}, a learner needs to {a1}. Which concept should guide the work?", t1, [t2, "random guessing", "unrelated memorisation"], f"The task is an application of {t1}, which helps learners {a1}", t1, 1),
        (f"While studying {title}, a student observes: {e1}. Which idea best explains it?", t1, [t2, "an unsupported prediction", "a process outside this chapter"], f"The situation is an example of {t1}: {e1}", t1, 2),
        (f"Which action best applies {t1} while working on {title}?", a1, [a2, "ignore the information supplied", "choose a result before using a method"], f"Applying {t1} helps the learner {a1}", t1, 3),
        (f"In {title}, a classmate describes {t1}. Which description should be accepted?", d1, [d2, "A guess without evidence", "A rule that changes the given conditions"], f"{d1} is the accurate description of {t1}", t1, 4),
        (f"In {title}, a learner needs to {a2}. Which concept is most directly involved?", t2, [t1, "random guessing", "an unrelated measurement"], f"The task is an application of {t2}, which helps learners {a2}", t2, 5),
        (f"While studying {title}, a student records: {e2}. Which idea is being used?", t2, [t1, "an unsupported opinion", "a procedure unrelated to the observation"], f"The example illustrates {t2}: {e2}", t2, 6),
        (f"Which action best applies {t2} in {title}?", a2, [a1, "ignore the relevant observations", "change the question instead of solving it"], f"Applying {t2} helps the learner {a2}", t2, 7),
        (f"Which description of {t2} is accurate in {title}?", d2, [d1, "A guess without evidence", "A statement that contradicts the given conditions"], f"{d2} is the accurate description of {t2}", t2, 8),
    ]
    for prompt, answer, wrong, why, term, n in medium_specs:
        questions.append(_make_question(
            f"{prefix}-M{n:02d}", grade, subject, chapter_id, title,
            "medium", prompt, answer, wrong, why,
            f"{chapter_id}-concept-{1 if term == t1 else 2}", term
        ))

    # 4 hard: combine the chapter's two central concepts in a short reasoning task.
    combined_1 = f"Use {t1} to {a1}, then use {t2} to {a2}."
    combined_2 = f"Use {t2} to {a2}, then use {t1} to {a1}."
    combined_3 = f"Use only {t1}; the second idea is never relevant to this chapter."
    combined_4 = f"Choose an answer first and use {t1} and {t2} only if it agrees with the guess."
    hard_specs = [
        (f"A multi-step task in {title} requires both {t1} and {t2}. Which plan uses both ideas appropriately?", combined_1, [combined_2, combined_3, combined_4], f"The plan is sound because {t1} supports the first part ({a1}) and {t2} supports the second part ({a2}).", f"{t1} + {t2}"),
        (f"A learner uses {t1} but ignores {t2}. What is the strongest reason this solution may be incomplete?", f"It may miss an important part of the reasoning: {a2}.", [f"It is incomplete because {a1} is never needed.", "Every answer is correct without checking the conditions.", "The chapter does not involve either concept."], f"Both ideas matter: {t1} helps with {a1}, while {t2} helps with {a2}.", f"{t1} + {t2}"),
        (f"Which statement best connects {t1} and {t2} in {title}?", f"{d1} and {d2} describe related parts of the chapter's reasoning.", ["The two ideas always mean exactly the same thing.", "The two ideas cannot be used in the same problem.", "Neither idea depends on the information in a question."], f"The concepts are distinct but complementary: {t1} ({d1}) and {t2} ({d2}).", f"{t1} + {t2}"),
        (f"A student wants to check a final answer involving {t1} and {t2}. Which check is most reliable?", f"Check that the result follows from {d1} and is also consistent with {d2}.", ["Check only whether the answer looks familiar.", "Change the given facts until the answer fits.", "Ignore one of the two concepts to save time."], f"A reliable check uses both concepts and verifies the result against the conditions of the problem.", f"{t1} + {t2}"),
    ]
    for n, (prompt, answer, wrong, why, concept) in enumerate(hard_specs, 1):
        questions.append(_make_question(
            f"{prefix}-H{n:02d}", grade, subject, chapter_id, title,
            "hard", prompt, answer, wrong, why,
            f"{chapter_id}-integrated-reasoning", concept
        ))

    if len(questions) != 20:
        raise AssertionError(f"{grade}/{subject}/{title}: expected 20 questions, got {len(questions)}")
    return questions


def build_all_questions() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    for grade in (f"Class {n}" for n in range(6, 11)):
        for subject in ("Mathematics", "Science"):
            if subject == "Mathematics":
                entries = MATHS_CHAPTERS[grade]
            else:
                entries = [(title, None, n) for n, title in enumerate(SCIENCE_CHAPTERS[grade], 1)]
            for ordinal, (title, part, number) in enumerate(entries, 1):
                chapter_id = _math_chapter_id(grade, number, part) if subject == "Mathematics" else _science_chapter_id(grade, number)
                # Keep all already-working question content intact. These chapters
                # are served by existing class6_content/class8_content/JSON packs.
                if grade == "Class 6":
                    continue
                if grade == "Class 8" and subject == "Mathematics" and number == 1 and part == "Part I":
                    continue
                questions.extend(build_chapter_questions(grade, subject, chapter_id, title, ordinal))
    return questions


def main() -> None:
    questions = build_all_questions()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "bank_version": "ncert-maths-science-classes6-10-2026-27-1.0",
        "curriculum_version": "NCERT-2026-27",
        "source_note": (
            "Original Vidhyastra questions aligned to publicly listed NCERT chapter titles and syllabus themes. "
            "They are not copied from NCERT textbook pages or third-party question banks. Teacher review is recommended."
        ),
        "sources": syllabus_sources(),
        "questions": questions,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(questions)} questions to {OUTPUT}")
    print(f"Chapter groups: {len(questions) // 20}; each group contains 8 easy, 8 medium and 4 hard.")


if __name__ == "__main__":
    main()
