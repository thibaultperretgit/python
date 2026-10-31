# QRT-style Quant Research Mock Assessment

This folder contains an original, unofficial practice assessment modeled on the format in the supplied brief:

- 82 minutes total;
- 1 data-science coding question;
- 10 mathematics and statistics questions;
- 5 machine-learning fundamentals questions;
- 8 advanced machine-learning questions.

No question is copied from a live assessment. Public reports were used only to calibrate the format and topic mix. See `sources_and_methodology.md` for what is corroborated, what conflicts, and what remains unknown.

It also contains three independent, progressive scikit-learn coding mocks. They are original practice exercises rather than claims about the contents of any live assessment.

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

### Progressive scikit-learn mocks

- `QRT_ml_01_cement_classification.ipynb` - binary classification with a protected labeled test set, pipelines, scaling, baselines, classification metrics, and model extraction.
- `QRT_ml_02_market_regime_clustering.ipynb` - KMeans selection and profiling, PCA visualization, and optional KMeans-stability/DBSCAN work.
- `QRT_ml_03_volatility_regression.ipynb` - chronological Ridge regression with walk-forward cross-validation, a five-row gap, residual diagnostics, and optional random-forest comparison.
- `data/cement_train.csv` and `data/cement_test.csv` - deterministic synthetic cement-strength classification data.
- `data/market_regimes.csv` - deterministic unlabeled market-regime data.
- `data/volatility_train.csv` and `data/volatility_test.csv` - deterministic chronological volatility-regression data.
- `solutions/*_reference.py` - separate reference implementations; keep these closed during timed attempts.
- `solutions/ml_answer_key.md` - expected metrics, interpretations, and optional-section guidance.
- `scripts/generate_ml_data.py` - shared deterministic generator for the five ML CSV files.
- `scripts/build_ml_notebooks.py` - reproducible builder for all three candidate notebooks.
- `scripts/validate_ml_assessments.py` - data, solution, leakage-boundary, metric, and clean-kernel notebook checks.

## Run the notebook

From this folder:

```bash
python3 -m pip install -r requirements.txt
jupyter notebook QRT_data_science.ipynb
```

The notebook uses only NumPy and pandas for the actual exercise. It is intentionally runnable before completion: unfinished checks report `NOT YET` rather than crashing the kernel. After implementation, all three checks should report `PASS`.

The three ML notebooks follow the same convention: every unfinished notebook runs from top to bottom, incomplete core checks report `NOT YET`, and optional advanced cells can be skipped. Suggested core timing is 45-60 minutes for classification, 45-60 minutes for clustering, and 55-70 minutes for regression.

## Rebuild and validate

From the parent repository folder:

```bash
python3 QRT_mock_test/scripts/generate_synthetic_data.py
python3 QRT_mock_test/scripts/build_notebook.py
python3 QRT_mock_test/scripts/validate_package.py
```

The validation script imports the reference solution, checks deterministic data invariants, and executes a temporary copy of the candidate notebook from top to bottom.

For the three ML mocks:

```bash
python3 QRT_mock_test/scripts/generate_ml_data.py
python3 QRT_mock_test/scripts/build_ml_notebooks.py
python3 QRT_mock_test/scripts/validate_ml_assessments.py
```

The ML validator checks reproducibility, schemas, class balance, chronology, model quality, cluster quality, feature boundaries, and clean-kernel execution of all three candidate notebooks.

## Fair-use note

QRT is a trademark of its owner. This independent practice package is not affiliated with, endorsed by, or sourced from Qube Research & Technologies. Treat the invitation for your own assessment as authoritative if it differs from this mock.
