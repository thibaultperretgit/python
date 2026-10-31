#!/usr/bin/env python3
"""Generate deterministic synthetic datasets for the three ML mock assessments."""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CEMENT_SEED = 20261101
CLUSTER_SEED = 20261102
REGRESSION_SEED = 20261103


def build_cement_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return labeled train and protected-test concrete classification data."""
    rng = np.random.default_rng(CEMENT_SEED)
    n_rows = 1_500
    cement = np.clip(rng.normal(325.0, 68.0, n_rows), 180.0, 520.0)
    water = np.clip(rng.normal(178.0, 24.0, n_rows), 120.0, 245.0)
    slag = np.clip(rng.gamma(1.7, 38.0, n_rows), 0.0, 220.0)
    superplasticizer = np.clip(rng.gamma(2.0, 3.4, n_rows), 0.0, 22.0)
    curing_days = rng.choice([3, 7, 14, 28, 56, 90], size=n_rows, p=[0.07, 0.13, 0.16, 0.34, 0.18, 0.12])

    water_cement_ratio = water / cement
    strength_mpa = (
        9.0
        + 29.0 * (1.0 - water_cement_ratio)
        + 0.047 * cement
        + 0.030 * slag
        + 0.52 * superplasticizer
        + 3.8 * np.log1p(curing_days)
        + 0.00022 * slag * curing_days
        + rng.normal(0.0, 4.2, n_rows)
    )
    is_strong = (strength_mpa >= 56.0).astype(float)
    dates = pd.Timestamp("2024-01-02") + pd.to_timedelta(rng.integers(0, 540, n_rows), unit="D")
    frame = pd.DataFrame(
        {
            "sample_id": [f"CMT-{i:05d}" for i in range(1, n_rows + 1)],
            "production_date": dates,
            "cement_kg_m3": cement,
            "water_kg_m3": water,
            "blast_furnace_slag_kg_m3": slag,
            "superplasticizer_kg_m3": superplasticizer,
            "curing_days": curing_days.astype(float),
            "is_strong": is_strong,
        }
    )

    feature_columns = [
        "cement_kg_m3",
        "water_kg_m3",
        "blast_furnace_slag_kg_m3",
        "superplasticizer_kg_m3",
        "curing_days",
    ]
    missing_mask = rng.random((n_rows, len(feature_columns))) < 0.018
    frame.loc[:, feature_columns] = frame.loc[:, feature_columns].mask(missing_mask)

    test_indices: list[int] = []
    for label in (0.0, 1.0):
        label_indices = frame.index[frame["is_strong"] == label].to_numpy(copy=True)
        rng.shuffle(label_indices)
        test_indices.extend(label_indices[: round(0.20 * len(label_indices))].tolist())
    test_index = pd.Index(test_indices)
    if len(test_index) > 300:
        test_index = test_index[:300]
    elif len(test_index) < 300:
        remaining = frame.index.difference(test_index).to_numpy()
        rng.shuffle(remaining)
        test_index = test_index.append(pd.Index(remaining[: 300 - len(test_index)]))

    test = frame.loc[test_index].sample(frac=1.0, random_state=CEMENT_SEED).reset_index(drop=True)
    train = frame.drop(index=test_index).sample(frac=1.0, random_state=CEMENT_SEED + 1).reset_index(drop=True)
    return train, test


def build_market_regimes() -> pd.DataFrame:
    """Return an unlabeled market panel with three persistent latent regimes."""
    rng = np.random.default_rng(CLUSTER_SEED)
    n_rows = 900
    transition = np.array(
        [
            [0.940, 0.030, 0.030],
            [0.030, 0.940, 0.030],
            [0.030, 0.030, 0.940],
        ]
    )
    regimes = np.empty(n_rows, dtype=int)
    regimes[0] = 1
    for i in range(1, n_rows):
        regimes[i] = rng.choice(3, p=transition[regimes[i - 1]])

    means = np.array(
        [
            [0.0120, 0.0080, -0.45, 0.22, -0.018],
            [0.0010, 0.0170, 1.00, 0.48, -0.080],
            [-0.0210, 0.0310, 0.55, 0.76, -0.210],
        ]
    )
    scales = np.array(
        [
            [0.0055, 0.0016, 0.28, 0.050, 0.014],
            [0.0080, 0.0025, 0.34, 0.055, 0.028],
            [0.0110, 0.0040, 0.40, 0.055, 0.045],
        ]
    )
    values = means[regimes] + rng.normal(size=(n_rows, 5)) * scales[regimes]
    values[:, 1] = np.clip(values[:, 1], 0.003, None)
    values[:, 3] = np.clip(values[:, 3], 0.05, 0.95)
    values[:, 4] = np.clip(values[:, 4], -0.45, 0.0)
    return pd.DataFrame(
        {
            "date": pd.bdate_range("2022-01-03", periods=n_rows),
            "return_5d": values[:, 0],
            "volatility_20d": values[:, 1],
            "volume_z": values[:, 2],
            "cross_asset_corr_20d": values[:, 3],
            "drawdown_60d": values[:, 4],
        }
    )


def build_volatility_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return chronological train and protected-test next-volatility data."""
    rng = np.random.default_rng(REGRESSION_SEED)
    n_simulated = 1_310
    latent_volatility = np.empty(n_simulated)
    latent_volatility[0] = 0.014
    regime_level = 0.014
    for i in range(1, n_simulated):
        if rng.random() < 0.025:
            regime_level = rng.choice([0.009, 0.014, 0.024, 0.034], p=[0.22, 0.44, 0.24, 0.10])
        latent_volatility[i] = (
            0.92 * latent_volatility[i - 1]
            + 0.08 * regime_level
            + rng.normal(0.0, 0.00075)
        )
        latent_volatility[i] = np.clip(latent_volatility[i], 0.0045, 0.0500)

    returns = rng.normal(0.00015, latent_volatility)
    prices = 100.0 * np.cumprod(1.0 + returns)
    series = pd.Series(returns)
    price_series = pd.Series(prices)
    volatility_5d = series.rolling(5).std(ddof=0)
    volatility_20d = series.rolling(20).std(ddof=0)
    rolling_peak = price_series.rolling(60, min_periods=1).max()
    drawdown_60d = price_series / rolling_peak - 1.0
    volume_z = 0.25 * np.abs(returns) / latent_volatility + 18.0 * (latent_volatility - 0.014) + rng.normal(0.0, 0.65, n_simulated)
    cross_asset_corr = np.clip(0.24 + 15.0 * latent_volatility + rng.normal(0.0, 0.045, n_simulated), 0.08, 0.92)

    future_realized = np.full(n_simulated, np.nan)
    for i in range(n_simulated - 5):
        realized = np.sqrt(np.mean(np.square(returns[i + 1 : i + 6])))
        latent_average = latent_volatility[i + 1 : i + 6].mean()
        future_realized[i] = 0.58 * latent_average + 0.42 * realized

    frame = pd.DataFrame(
        {
            "date": pd.bdate_range("2021-01-04", periods=n_simulated),
            "return_1d": returns,
            "abs_return_1d": np.abs(returns),
            "volatility_5d": volatility_5d,
            "volatility_20d": volatility_20d,
            "volume_z": volume_z,
            "cross_asset_corr_20d": cross_asset_corr,
            "drawdown_60d": drawdown_60d,
            "next_5d_volatility": future_realized,
        }
    ).iloc[60:-5].reset_index(drop=True)

    feature_columns = [
        "return_1d",
        "abs_return_1d",
        "volatility_5d",
        "volatility_20d",
        "volume_z",
        "cross_asset_corr_20d",
        "drawdown_60d",
    ]
    missing_mask = rng.random((len(frame), len(feature_columns))) < 0.008
    frame.loc[:, feature_columns] = frame.loc[:, feature_columns].mask(missing_mask)
    split = int(0.80 * len(frame))
    return frame.iloc[:split].reset_index(drop=True), frame.iloc[split:].reset_index(drop=True)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    cement_train, cement_test = build_cement_data()
    regimes = build_market_regimes()
    volatility_train, volatility_test = build_volatility_data()
    outputs = {
        "cement_train.csv": cement_train,
        "cement_test.csv": cement_test,
        "market_regimes.csv": regimes,
        "volatility_train.csv": volatility_train,
        "volatility_test.csv": volatility_test,
    }
    for filename, frame in outputs.items():
        path = DATA / filename
        frame.to_csv(path, index=False, float_format="%.8f", date_format="%Y-%m-%d")
        print(f"Wrote {len(frame):,} rows to {path}")


if __name__ == "__main__":
    main()
