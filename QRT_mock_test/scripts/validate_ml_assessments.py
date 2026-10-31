#!/usr/bin/env python3
"""Validate ML datasets, reference solutions, and candidate notebooks."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory

import nbformat
import numpy as np
import pandas as pd
from nbconvert.preprocessors import ExecutePreprocessor

from generate_ml_data import build_cement_data, build_market_regimes, build_volatility_data


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_module(filename: str):
    path = ROOT / "solutions" / filename
    spec = spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_frame_exact(left: pd.DataFrame, right: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(left, right, check_exact=True)


def validate_determinism() -> None:
    first_cement = build_cement_data()
    second_cement = build_cement_data()
    for first, second in zip(first_cement, second_cement, strict=True):
        assert_frame_exact(first, second)
    assert_frame_exact(build_market_regimes(), build_market_regimes())
    first_volatility = build_volatility_data()
    second_volatility = build_volatility_data()
    for first, second in zip(first_volatility, second_volatility, strict=True):
        assert_frame_exact(first, second)


def validate_cement() -> dict[str, float]:
    columns = [
        "sample_id",
        "production_date",
        "cement_kg_m3",
        "water_kg_m3",
        "blast_furnace_slag_kg_m3",
        "superplasticizer_kg_m3",
        "curing_days",
        "is_strong",
    ]
    train = pd.read_csv(DATA / "cement_train.csv")
    test = pd.read_csv(DATA / "cement_test.csv")
    assert list(train.columns) == columns == list(test.columns)
    assert train.shape == (1_200, 8) and test.shape == (300, 8)
    assert set(train["is_strong"]) == {0.0, 1.0} == set(test["is_strong"])
    assert train["sample_id"].is_unique and test["sample_id"].is_unique
    assert set(train["sample_id"]).isdisjoint(test["sample_id"])
    assert train[columns[2:-1]].isna().sum().sum() > 0
    assert train["is_strong"].mean() > 0.40 and train["is_strong"].mean() < 0.60

    solution = load_module("cement_classification_reference.py")
    result = solution.solve(DATA / "cement_train.csv", DATA / "cement_test.csv")
    metrics = result["test"]
    numeric = {key: float(value) for key, value in metrics.items() if key != "confusion_matrix"}
    assert all(np.isfinite(list(numeric.values())))
    assert numeric["roc_auc"] > 0.85 and numeric["f1"] > 0.75
    assert list(result["predictions"].columns) == ["sample_id", "production_date", "actual", "predicted", "probability_strong"]
    assert set(result["coefficients"]["feature"]) == set(solution.FEATURES)
    return numeric


def validate_clustering() -> dict[str, float]:
    columns = ["date", "return_5d", "volatility_20d", "volume_z", "cross_asset_corr_20d", "drawdown_60d"]
    data = pd.read_csv(DATA / "market_regimes.csv")
    assert data.shape == (900, 6)
    assert list(data.columns) == columns
    assert data["date"].is_unique
    assert "regime" not in " ".join(data.columns).lower()

    solution = load_module("market_clustering_reference.py")
    result = solution.solve(DATA / "market_regimes.csv")
    selection = result["selection"]
    best = selection.loc[selection["silhouette"].idxmax()]
    assert int(best["k"]) == 3 and float(best["silhouette"]) > 0.40
    assert result["profile"]["share"].min() > 0.10
    assert np.isclose(result["profile"]["share"].sum(), 1.0)
    assert result["stability"]["adjusted_rand_vs_seed_0"].min() > 0.95
    assert result["dbscan"]["n_clusters"] >= 2
    return {
        "best_k": float(best["k"]),
        "silhouette": float(best["silhouette"]),
        "minimum_cluster_share": float(result["profile"]["share"].min()),
    }


def validate_regression() -> dict[str, float]:
    columns = [
        "date",
        "return_1d",
        "abs_return_1d",
        "volatility_5d",
        "volatility_20d",
        "volume_z",
        "cross_asset_corr_20d",
        "drawdown_60d",
        "next_5d_volatility",
    ]
    train = pd.read_csv(DATA / "volatility_train.csv", parse_dates=["date"])
    test = pd.read_csv(DATA / "volatility_test.csv", parse_dates=["date"])
    assert list(train.columns) == columns == list(test.columns)
    assert train.shape == (996, 9) and test.shape == (249, 9)
    assert train["date"].is_monotonic_increasing and test["date"].is_monotonic_increasing
    assert train["date"].max() < test["date"].min()
    assert train["next_5d_volatility"].notna().all() and test["next_5d_volatility"].notna().all()

    solution = load_module("volatility_regression_reference.py")
    fitting, _ = solution.chronological_train_validation(train)
    search = solution.select_ridge_alpha(fitting)
    assert search.cv.gap == 5
    result = solution.solve(DATA / "volatility_train.csv", DATA / "volatility_test.csv")
    dummy = result["test"]["dummy"]
    ridge = result["test"]["ridge"]
    assert all(np.isfinite(list(dummy.values()) + list(ridge.values())))
    improvement = 1.0 - ridge["mae"] / dummy["mae"]
    assert improvement > 0.20 and ridge["r2"] > 0.0
    assert list(result["audit"].columns) == ["date", "actual", "predicted", "residual", "absolute_error"]
    assert set(result["coefficients"]["feature"]) == set(solution.FEATURES)
    return {
        "best_alpha": float(result["best_alpha"]),
        "test_mae": float(ridge["mae"]),
        "test_r2": float(ridge["r2"]),
        "mae_improvement": float(improvement),
    }


def validate_notebooks() -> None:
    notebooks = [
        ROOT / "QRT_ml_01_cement_classification.ipynb",
        ROOT / "QRT_ml_02_market_regime_clustering.ipynb",
        ROOT / "QRT_ml_03_volatility_regression.ipynb",
    ]
    required_markers = {
        notebooks[0]: ["audit_classification_data", "build_classifier", "classification_metrics", "make_test_predictions"],
        notebooks[1]: ["prepare_clustering_data", "evaluate_kmeans", "fit_market_clusters", "make_pca_embedding"],
        notebooks[2]: ["chronological_train_validation", "select_ridge_alpha", "regression_metrics", "make_prediction_audit"],
    }
    for path in notebooks:
        notebook = nbformat.read(path, as_version=4)
        sources = "\n".join(cell.get("source", "") for cell in notebook.cells)
        assert "TODO" in sources
        for marker in required_markers[path]:
            assert marker in sources
        with TemporaryDirectory() as tmp:
            executed = nbformat.from_dict(notebook)
            executor = ExecutePreprocessor(timeout=180, kernel_name="python3")
            executor.preprocess(executed, {"metadata": {"path": str(ROOT)}})
            output = Path(tmp) / path.name
            nbformat.write(executed, output)
            assert output.exists()


def main() -> None:
    validate_determinism()
    classification = validate_cement()
    clustering = validate_clustering()
    regression = validate_regression()
    validate_notebooks()
    print("All ML datasets, references, and candidate notebooks validated.")
    print("classification", classification)
    print("clustering", clustering)
    print("regression", regression)


if __name__ == "__main__":
    main()
