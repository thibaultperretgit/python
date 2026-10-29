# QRT-style Quant Research Mock Assessment

This folder contains an original, unofficial practice assessment modeled on the format in the supplied brief:

- 82 minutes total;
- 1 data-science coding question;
- 10 mathematics and statistics questions;
- 5 machine-learning fundamentals questions;
- 8 advanced machine-learning questions.

No question is copied from a live assessment. Public reports were used only to calibrate the format and topic mix. See `sources_and_methodology.md` for what is corroborated, what conflicts, and what remains unknown.

## Start here

1. Before the timed attempt, review `QRT_formula_and_revision_guide.pdf` and note any weak topics.
2. Close the `solutions/` folder.
3. Set an 82-minute timer.
4. Open `QRT_mock_test.pdf` for instructions and Questions 1-23.
5. Open `QRT_data_science.ipynb` for the coding question.
6. Follow the suggested split: 42 minutes coding, 18 minutes mathematics, 8 minutes ML fundamentals, and 14 minutes ML advanced.

## Files

- `QRT_mock_test.pdf` - the single printable PDF containing all 23 non-coding questions.
- `QRT_mock_test.tex` - editable LaTeX source for the PDF.
- `QRT_formula_and_revision_guide.pdf` - 19-page formula sheet and revision handbook covering the highest-value math, statistics, ML, quant, and pandas concepts.
- `QRT_formula_and_revision_guide.tex` - editable LaTeX source for the revision handbook.
- `QRT_data_science.ipynb` - candidate notebook with three functions to complete and visible validation checks.
- `data/market_panel.csv` - deterministic synthetic market panel used by the notebook.
- `solutions/answer_key.md` - MCQ answers, explanations, and expected coding metrics.
- `solutions/coding_reference_solution.py` - complete reference implementation.
- `sources_and_methodology.md` - evidence grading, public sources, and design decisions.
- `scripts/generate_synthetic_data.py` - reproducible dataset generator.
- `scripts/build_notebook.py` - reproducible notebook builder.
- `scripts/validate_package.py` - package and top-to-bottom notebook validator.

## Run the notebook

From this folder:

```bash
python3 -m pip install -r requirements.txt
jupyter notebook QRT_data_science.ipynb
```

The notebook uses only NumPy and pandas for the actual exercise. It is intentionally runnable before completion: unfinished checks report `NOT YET` rather than crashing the kernel. After implementation, all three checks should report `PASS`.

## Rebuild and validate

From the parent repository folder:

```bash
python3 QRT_mock_test/scripts/generate_synthetic_data.py
python3 QRT_mock_test/scripts/build_notebook.py
python3 QRT_mock_test/scripts/validate_package.py
```

The validation script imports the reference solution, checks deterministic data invariants, and executes a temporary copy of the candidate notebook from top to bottom.

## Fair-use note

QRT is a trademark of its owner. This independent practice package is not affiliated with, endorsed by, or sourced from Qube Research & Technologies. Treat the invitation for your own assessment as authoritative if it differs from this mock.
