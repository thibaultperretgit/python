#!/usr/bin/env python3
"""Generate the deterministic synthetic panel used by the coding exercise."""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "market_panel.csv"
SEED = 20261028


def build_panel() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    dates = pd.bdate_range("2025-01-02", periods=160)
    assets = [f"A{i:02d}" for i in range(30)]
    sectors = ["Energy", "Finance", "Healthcare", "Industrials", "Technology"]
    sector_of = {asset: sectors[i // 6] for i, asset in enumerate(assets)}

    latent = {asset: rng.normal(0.0, 0.6) for asset in assets}
    rows: list[dict[str, object]] = []

    for date in dates:
        market_shock = rng.normal(0.0, 0.0025)
        sector_shock = {sector: rng.normal(0.0, 0.0018) for sector in sectors}
        for asset in assets:
            latent[asset] = 0.62 * latent[asset] + rng.normal(0.0, 0.78)
            volume_z = rng.normal(0.0, 1.0)
            volatility = 0.0075 + 0.0045 * (1.0 / (1.0 + np.exp(-abs(latent[asset]))))
            observed_signal = latent[asset] + 0.18 * volume_z + rng.normal(0.0, 0.22)
            next_return = (
                0.00055 * latent[asset]
                + market_shock
                + sector_shock[sector_of[asset]]
                + rng.normal(0.0, volatility)
            )
            rows.append(
                {
                    "date": date,
                    "asset": asset,
                    "sector": sector_of[asset],
                    "observation_time": date + pd.Timedelta(hours=16),
                    "signal_raw": observed_signal,
                    "volatility_20d": volatility,
                    "volume_z": volume_z,
                    "next_day_return": next_return,
                }
            )

    panel = pd.DataFrame(rows)

    missing_idx = rng.choice(panel.index, size=132, replace=False)
    panel.loc[missing_idx, "signal_raw"] = np.nan

    available = panel.index.difference(missing_idx)
    outlier_idx = rng.choice(available, size=42, replace=False)
    panel.loc[outlier_idx, "signal_raw"] *= rng.choice([-7.5, 7.5], size=len(outlier_idx))

    duplicate_idx = rng.choice(panel.index, size=72, replace=False)
    corrections = panel.loc[duplicate_idx].copy()
    corrections["observation_time"] += pd.Timedelta(minutes=5)
    correction_noise = rng.normal(0.0, 0.06, size=len(corrections))
    corrections["signal_raw"] = corrections["signal_raw"].fillna(
        pd.Series(rng.normal(0.0, 1.0, size=len(corrections)), index=corrections.index)
    ) + correction_noise

    panel = pd.concat([panel, corrections], ignore_index=True)
    panel = panel.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    return panel


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    panel = build_panel()
    panel.to_csv(OUTPUT, index=False, float_format="%.8f", date_format="%Y-%m-%d %H:%M:%S")
    print(f"Wrote {len(panel):,} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
