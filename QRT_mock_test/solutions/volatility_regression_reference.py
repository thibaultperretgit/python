#!/usr/bin/env python3
"""Reference implementation for the next-period volatility regression mock."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = [
    "return_1d",
    "abs_return_1d",
    "volatility_5d",
    "volatility_20d",
    "volume_z",
    "cross_asset_corr_20d",
    "drawdown_60d",
]
TARGET = "next_5d_volatility"
RANDOM_STATE = 20261103
ALPHAS = [0.01, 0.1, 1.0, 10.0, 100.0]


def chronological_train_validation(
    train_data: pd.DataFrame,
    validation_fraction: float = 0.20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return strictly chronological model-selection partitions."""
    required = set(FEATURES + [TARGET, "date"])
    missing = required.difference(train_data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    ordered = train_data.copy()
    ordered["date"] = pd.to_datetime(ordered["date"])
    ordered = ordered.sort_values("date").reset_index(drop=True)
    split = int((1.0 - validation_fraction) * len(ordered))
    return ordered.iloc[:split].copy(), ordered.iloc[split:].copy()


def build_ridge_pipeline(alpha: float = 1.0) -> Pipeline:
    """Build the leakage-safe imputation, scaling, and Ridge pipeline."""
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=alpha)),
        ]
    )


def select_ridge_alpha(train_partition: pd.DataFrame) -> GridSearchCV:
    """Select Ridge regularization using walk-forward folds and a five-row gap."""
    splitter = TimeSeriesSplit(n_splits=5, gap=5)
    search = GridSearchCV(
        estimator=build_ridge_pipeline(),
        param_grid={"model__alpha": ALPHAS},
        scoring="neg_mean_absolute_error",
        cv=splitter,
        refit=True,
    )
    return search.fit(train_partition[FEATURES], train_partition[TARGET])


def regression_metrics(y_true: pd.Series | np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Return the requested regression metrics."""
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(root_mean_squared_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def make_prediction_audit(model: Pipeline, test_data: pd.DataFrame) -> pd.DataFrame:
    """Return dates, actuals, predictions, residuals, and absolute errors."""
    prediction = model.predict(test_data[FEATURES])
    actual = test_data[TARGET].to_numpy()
    residual = actual - prediction
    return pd.DataFrame(
        {
            "date": pd.to_datetime(test_data["date"]).to_numpy(),
            "actual": actual,
            "predicted": prediction,
            "residual": residual,
            "absolute_error": np.abs(residual),
        }
    )


def coefficient_table(model: Pipeline) -> pd.DataFrame:
    """Return standardized Ridge coefficients ranked by absolute size."""
    coefficients = model.named_steps["model"].coef_
    result = pd.DataFrame({"feature": FEATURES, "coefficient": coefficients})
    result["absolute_coefficient"] = result["coefficient"].abs()
    return result.sort_values("absolute_coefficient", ascending=False).reset_index(drop=True)


def fit_random_forest(train_partition: pd.DataFrame) -> Pipeline:
    """Optional extension: fit a nonlinear comparison model."""
    model = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=400,
                    max_depth=7,
                    min_samples_leaf=5,
                    random_state=RANDOM_STATE,
                    n_jobs=1,
                ),
            ),
        ]
    )
    return model.fit(train_partition[FEATURES], train_partition[TARGET])


def forest_permutation_importance(model: Pipeline, validation: pd.DataFrame) -> pd.DataFrame:
    """Optional extension: calculate validation-set permutation importance."""
    importance = permutation_importance(
        model,
        validation[FEATURES],
        validation[TARGET],
        scoring="neg_mean_absolute_error",
        n_repeats=20,
        random_state=RANDOM_STATE,
    )
    result = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance_mean": importance.importances_mean,
            "importance_std": importance.importances_std,
        }
    )
    return result.sort_values("importance_mean", ascending=False).reset_index(drop=True)


def solve(train_path: str | Path, test_path: str | Path) -> dict[str, object]:
    """Run chronological model selection and one protected-test evaluation."""
    train_data = pd.read_csv(train_path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    test_data = pd.read_csv(test_path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    fitting, validation = chronological_train_validation(train_data)

    dummy = DummyRegressor(strategy="mean").fit(fitting[FEATURES], fitting[TARGET])
    search = select_ridge_alpha(fitting)
    validation_predictions = {
        "dummy": dummy.predict(validation[FEATURES]),
        "ridge": search.predict(validation[FEATURES]),
    }
    validation_metrics = {
        name: regression_metrics(validation[TARGET], prediction)
        for name, prediction in validation_predictions.items()
    }

    best_alpha = float(search.best_params_["model__alpha"])
    final_dummy = DummyRegressor(strategy="mean").fit(train_data[FEATURES], train_data[TARGET])
    final_model = build_ridge_pipeline(best_alpha).fit(train_data[FEATURES], train_data[TARGET])
    audit = make_prediction_audit(final_model, test_data)
    test_metrics = {
        "dummy": regression_metrics(test_data[TARGET], final_dummy.predict(test_data[FEATURES])),
        "ridge": regression_metrics(audit["actual"], audit["predicted"]),
    }
    forest = fit_random_forest(fitting)
    return {
        "best_alpha": best_alpha,
        "validation": validation_metrics,
        "test": test_metrics,
        "audit": audit,
        "coefficients": coefficient_table(final_model),
        "forest_validation": regression_metrics(validation[TARGET], forest.predict(validation[FEATURES])),
        "forest_importance": forest_permutation_importance(forest, validation),
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = solve(root / "data" / "volatility_train.csv", root / "data" / "volatility_test.csv")
    print("best_alpha", result["best_alpha"])
    print(pd.DataFrame(result["validation"]).T)
    print(pd.DataFrame(result["test"]).T)
    print(result["coefficients"])
