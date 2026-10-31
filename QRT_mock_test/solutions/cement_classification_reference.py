#!/usr/bin/env python3
"""Reference implementation for the cement-strength classification mock."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = [
    "cement_kg_m3",
    "water_kg_m3",
    "blast_furnace_slag_kg_m3",
    "superplasticizer_kg_m3",
    "curing_days",
]
TARGET = "is_strong"
RANDOM_STATE = 20261101


def split_train_validation(
    train_data: pd.DataFrame,
    validation_size: float = 0.25,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Return a reproducible stratified train/validation split."""
    missing = set(FEATURES + [TARGET]).difference(train_data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    X = train_data[FEATURES].copy()
    y = train_data[TARGET].astype(int)
    return train_test_split(
        X,
        y,
        test_size=validation_size,
        stratify=y,
        random_state=random_state,
    )


def build_classifier(random_state: int = RANDOM_STATE) -> Pipeline:
    """Build the leakage-safe logistic-regression pipeline."""
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=2_000, random_state=random_state)),
        ]
    )


def classification_metrics(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    y_probability: np.ndarray,
) -> dict[str, object]:
    """Return threshold and ranking metrics plus the confusion matrix."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_probability)),
        "confusion_matrix": confusion_matrix(y_true, y_pred),
    }


def evaluate_classifier(model: Pipeline | DummyClassifier, X: pd.DataFrame, y: pd.Series) -> dict[str, object]:
    """Evaluate a fitted classifier that supports class probabilities."""
    prediction = model.predict(X)
    probability = model.predict_proba(X)[:, 1]
    return classification_metrics(y, prediction, probability)


def make_test_predictions(model: Pipeline, test_data: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Create the compact protected-test prediction audit table."""
    probability = model.predict_proba(test_data[FEATURES])[:, 1]
    prediction = (probability >= threshold).astype(int)
    return pd.DataFrame(
        {
            "sample_id": test_data["sample_id"].to_numpy(),
            "production_date": pd.to_datetime(test_data["production_date"]).to_numpy(),
            "actual": test_data[TARGET].astype(int).to_numpy(),
            "predicted": prediction,
            "probability_strong": probability,
        }
    )


def coefficient_table(model: Pipeline) -> pd.DataFrame:
    """Return standardized logistic coefficients ranked by absolute size."""
    coefficients = model.named_steps["model"].coef_[0]
    result = pd.DataFrame({"feature": FEATURES, "coefficient": coefficients})
    result["absolute_coefficient"] = result["coefficient"].abs()
    return result.sort_values("absolute_coefficient", ascending=False).reset_index(drop=True)


def best_f1_threshold(y_true: pd.Series, probability: np.ndarray) -> tuple[float, pd.DataFrame]:
    """Optional extension: choose a probability threshold using validation F1 only."""
    rows = []
    for threshold in np.linspace(0.20, 0.80, 61):
        score = f1_score(y_true, probability >= threshold, zero_division=0)
        rows.append({"threshold": float(threshold), "f1": float(score)})
    scores = pd.DataFrame(rows)
    best = scores.sort_values(["f1", "threshold"], ascending=[False, True]).iloc[0]
    return float(best["threshold"]), scores


def build_random_forest(random_state: int = RANDOM_STATE) -> Pipeline:
    """Optional extension: build a nonlinear comparison model."""
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=350,
                    min_samples_leaf=4,
                    class_weight="balanced",
                    random_state=random_state,
                    n_jobs=1,
                ),
            ),
        ]
    )


def solve(train_path: str | Path, test_path: str | Path) -> dict[str, object]:
    """Run model selection, one final test evaluation, and interpretation."""
    train_data = pd.read_csv(train_path, parse_dates=["production_date"])
    test_data = pd.read_csv(test_path, parse_dates=["production_date"])
    X_train, X_validation, y_train, y_validation = split_train_validation(train_data)

    dummy = DummyClassifier(strategy="prior").fit(X_train, y_train)
    classifier = build_classifier().fit(X_train, y_train)
    validation = {
        "dummy": evaluate_classifier(dummy, X_validation, y_validation),
        "logistic": evaluate_classifier(classifier, X_validation, y_validation),
    }

    final_model = build_classifier().fit(train_data[FEATURES], train_data[TARGET].astype(int))
    predictions = make_test_predictions(final_model, test_data)
    test_metrics = classification_metrics(
        predictions["actual"],
        predictions["predicted"],
        predictions["probability_strong"],
    )
    return {
        "validation": validation,
        "test": test_metrics,
        "predictions": predictions,
        "coefficients": coefficient_table(final_model),
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = solve(root / "data" / "cement_train.csv", root / "data" / "cement_test.csv")
    print(pd.Series({key: value for key, value in result["test"].items() if key != "confusion_matrix"}))
    print("confusion_matrix")
    print(result["test"]["confusion_matrix"])
    print(result["coefficients"])
