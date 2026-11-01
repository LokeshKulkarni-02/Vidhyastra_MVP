# Vidhyastra NCERT Maths + Science coverage summary

## Chapter assessment coverage after installation

| Class | Mathematics chapters | Science chapters | Total chapters |
|---|---:|---:|---:|
| 6 | 10 | 12 | 22 |
| 7 | 8 | 12 | 20 |
| 8 | 14 | 13 | 27 |
| 9 | 14 | 13 | 27 |
| 10 | 14 | 13 | 27 |
| **Total** | **60** | **63** | **123** |

Each formal chapter assessment contains exactly 20 questions: 8 easy, 8 medium and 4 hard.

- Formal chapter assessments: 123 × 20 = **2,460 questions**.
- Two existing supplementary Class 8 Mathematics drills remain available: **40 questions**.
- Total active records after installation: **2,500 questions**.
- New additive pack in this ZIP: **100 chapter assessments / 2,000 questions**.

## Existing question content preserved

- Class 6 Mathematics: all 10 existing chapter question sets remain in `class6_content.py` and the bank loader.
- Class 6 Science: all 12 existing chapter sets remain in `question_banks/class6_science.json`.
- Class 8 Mathematics Chapter 1: the existing Chapter Assessment, Square Numbers drill and Cubic Numbers drill remain in the bank.

The additive JSON intentionally excludes these existing groups. Question IDs in the additive pack are unique and its groups do not overwrite old records.

## Verification performed for this package

- Python syntax compilation for all new `.py` files: passed.
- Unit tests for the 2,000-question pack: 8 passed.
- Question ID uniqueness: passed.
- Question prompt uniqueness in the new pack: passed.
- Four distinct choices and correct answer membership: passed.
- Exact 20-question / 8-easy / 8-medium / 4-hard distribution for all 100 new chapter groups: passed.
- Patcher fixture: passed; all class subject chapter counts loaded and existing Class 6 / Class 8 topic mappings remained intact.

The full Flask application has not been run against the user's actual SQLite database in this package build. Run the post-install commands in `README_NCERT_QUIZ_INSTALL.md` and exercise the live site before production use.
