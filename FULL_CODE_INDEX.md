# Full source-file index

The ZIP includes the complete contents of every new source file and the entire 2,000-question JSON pack.

## New source files (copy to the Vidhyastra project root)

- `ncert_quiz_catalog.py`
- `build_ncert_quiz_pack.py`
- `apply_ncert_quiz_expansion.py`
- `verify_ncert_quiz_expansion.py`

## New data file (copy into the existing question_banks folder)

- `question_banks/ncert_maths_science_classes6_10.json`

## Test file (copy into tests)

- `tests/test_ncert_maths_science_pack.py`

## Documentation

- `README_NCERT_QUIZ_INSTALL.md`
- `NCERT_QUESTION_SOURCES.md`
- `COVERAGE_SUMMARY.md`

## Existing application file modified by the patcher

`curriculum_catalog.py` is **not replaced**. `apply_ncert_quiz_expansion.py` inserts a short import hook immediately before its existing `# PUBLIC HELPER FUNCTIONS` marker. It creates a timestamped backup before writing. This avoids supplying a simplified replacement for the full catalogue file and preserves existing route/data structures.

No changes are made to `app.py`, `question_bank.py`, `question_bank.json`, existing `class6_content.py`, `class8_content.py`, existing JSON packs, templates or the database.
