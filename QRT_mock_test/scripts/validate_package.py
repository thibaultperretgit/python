#!/usr/bin/env python3
"""Validate the generated dataset, reference solution, and candidate notebook."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

import nbformat
import numpy as np
import pandas as pd
from nbconvert.preprocessors import ExecutePreprocessor
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def load_solution():
    path = ROOT / "solutions" / "coding_reference_solution.py"
    spec = spec_from_file_location("coding_reference_solution", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_data_and_solution() -> dict[str, float]:
    raw = pd.read_csv(ROOT / "data" / "market_panel.csv")
    assert len(raw) == 4_872
    assert raw["asset"].nunique() == 30
    solution = load_solution()
    clean = solution.clean_panel(raw)
    assert len(clean) == 4_800
    assert clean["date"].nunique() == 160
    assert not clean.duplicated(["date", "asset"]).any()
    assert clean[["signal_winsor", "signal_z"]].notna().all().all()
    assert np.allclose(clean.groupby("date")["signal_z"].mean(), 0.0, atol=1e-10)
    assert np.allclose(clean.groupby("date")["signal_z"].std(ddof=0), 1.0, atol=1e-10)

    daily = solution.compute_daily_performance(clean, "2025-06-02")
    assert len(daily) == 53
    assert daily[["factor_return", "rank_ic"]].notna().all().all()
    assert (daily["n_assets"] == 30).all()
    assert (daily["n_per_leg"] == 6).all()
    metrics = solution.summarize_performance(daily)
    assert all(np.isfinite(value) for value in metrics.values())
    assert metrics["sharpe_ratio"] > 0.5
    assert metrics["mean_rank_ic"] > 0.0
    return metrics


def validate_notebook() -> None:
    path = ROOT / "QRT_data_science.ipynb"
    notebook = nbformat.read(path, as_version=4)
    sources = "\n".join(cell.get("source", "") for cell in notebook.cells)
    for marker in ["def clean_panel", "def compute_daily_performance", "def summarize_performance"]:
        assert marker in sources
    assert "TODO" in sources

    with TemporaryDirectory() as tmp:
        executed = nbformat.from_dict(notebook)
        executor = ExecutePreprocessor(timeout=120, kernel_name="python3")
        executor.preprocess(executed, {"metadata": {"path": str(ROOT)}})
        output = Path(tmp) / "executed.ipynb"
        nbformat.write(executed, output)
        assert output.exists()


def validate_pdfs() -> None:
    path = ROOT / "QRT_mock_test.pdf"
    reader = PdfReader(str(path))
    assert len(reader.pages) == 7
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    assert text.count("Question ") == 23
    for number in range(1, 24):
        assert f"Question {number}" in text
    for section in [
        "Section A: Mathematics and Statistics",
        "Section B: Machine Learning Fundamentals",
        "Section C: Machine Learning Advanced",
    ]:
        assert section in text

    guide_path = ROOT / "QRT_formula_and_revision_guide.pdf"
    guide_reader = PdfReader(str(guide_path))
    assert len(guide_reader.pages) == 19
    guide_text = "\n".join((page.extract_text() or "") for page in guide_reader.pages)
    for marker in [
        "Probability foundations",
        "Linear algebra",
        "Machine-learning",
        "Quant and time-series formulas",
        "Pandas coding reference",
        "Rapid Recall",
        "Final checklist",
    ]:
        assert marker in guide_text


def main() -> None:
    metrics = validate_data_and_solution()
    validate_notebook()
    validate_pdfs()
    print("Dataset, solution, notebook, mock PDF, and revision PDF validation passed.")
    for name, value in metrics.items():
        print(f"{name:24s} {value:.6f}")


if __name__ == "__main__":
    main()
