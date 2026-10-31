#!/usr/bin/env python3
"""Reference implementation for the market-regime clustering mock."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = [
    "return_5d",
    "volatility_20d",
    "volume_z",
    "cross_asset_corr_20d",
    "drawdown_60d",
]
RANDOM_STATE = 20261102


def build_preprocessor() -> Pipeline:
    """Build the numeric imputation and scaling pipeline."""
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )


def select_cluster_count(
    data: pd.DataFrame,
    candidates: range | list[int] = range(2, 7),
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, Pipeline, np.ndarray]:
    """Fit candidate KMeans models and return inertia and silhouette scores."""
    missing = set(FEATURES).difference(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    preprocessor = build_preprocessor().fit(data[FEATURES])
    scaled = preprocessor.transform(data[FEATURES])
    rows = []
    for k in candidates:
        model = KMeans(n_clusters=k, n_init=20, random_state=random_state)
        labels = model.fit_predict(scaled)
        rows.append(
            {
                "k": int(k),
                "inertia": float(model.inertia_),
                "silhouette": float(silhouette_score(scaled, labels)),
            }
        )
    return pd.DataFrame(rows), preprocessor, scaled


def fit_market_clusters(
    data: pd.DataFrame,
    n_clusters: int = 3,
    random_state: int = RANDOM_STATE,
) -> tuple[KMeans, Pipeline, pd.DataFrame, np.ndarray]:
    """Fit KMeans on scaled features and append cluster labels to raw data."""
    preprocessor = build_preprocessor().fit(data[FEATURES])
    scaled = preprocessor.transform(data[FEATURES])
    model = KMeans(n_clusters=n_clusters, n_init=20, random_state=random_state)
    labels = model.fit_predict(scaled)
    clustered = data.copy()
    clustered["cluster"] = labels
    return model, preprocessor, clustered, scaled


def cluster_profile(clustered: pd.DataFrame) -> pd.DataFrame:
    """Return cluster counts, shares, and original-unit feature means."""
    means = clustered.groupby("cluster")[FEATURES].mean()
    counts = clustered.groupby("cluster").size().rename("count")
    profile = means.join(counts)
    profile["share"] = profile["count"] / len(clustered)
    return profile[["count", "share", *FEATURES]]


def pca_coordinates(scaled: np.ndarray, labels: np.ndarray) -> tuple[pd.DataFrame, PCA]:
    """Return a two-dimensional PCA view for visualization only."""
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coordinates = pca.fit_transform(scaled)
    return pd.DataFrame({"pc1": coordinates[:, 0], "pc2": coordinates[:, 1], "cluster": labels}), pca


def kmeans_stability(scaled: np.ndarray, n_clusters: int = 3) -> pd.DataFrame:
    """Optional extension: compare cluster assignments across seeds."""
    reference = KMeans(n_clusters=n_clusters, n_init=20, random_state=0).fit_predict(scaled)
    rows = []
    for seed in range(1, 11):
        labels = KMeans(n_clusters=n_clusters, n_init=20, random_state=seed).fit_predict(scaled)
        rows.append({"seed": seed, "adjusted_rand_vs_seed_0": adjusted_rand_score(reference, labels)})
    return pd.DataFrame(rows)


def dbscan_comparison(scaled: np.ndarray, eps: float = 0.75, min_samples: int = 12) -> dict[str, object]:
    """Optional extension: fit DBSCAN and summarize clusters, noise, and silhouette."""
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(scaled)
    clustered_mask = labels != -1
    unique_clusters = set(labels[clustered_mask])
    silhouette = np.nan
    if len(unique_clusters) >= 2 and clustered_mask.sum() > len(unique_clusters):
        silhouette = silhouette_score(scaled[clustered_mask], labels[clustered_mask])
    return {
        "labels": labels,
        "n_clusters": len(unique_clusters),
        "noise_fraction": float((labels == -1).mean()),
        "silhouette_without_noise": float(silhouette),
    }


def solve(data_path: str | Path) -> dict[str, object]:
    """Run cluster selection, final profiling, PCA, and optional diagnostics."""
    data = pd.read_csv(data_path, parse_dates=["date"])
    selection, _, _ = select_cluster_count(data)
    model, preprocessor, clustered, scaled = fit_market_clusters(data)
    profile = cluster_profile(clustered)
    coordinates, pca = pca_coordinates(scaled, model.labels_)
    return {
        "selection": selection,
        "model": model,
        "preprocessor": preprocessor,
        "clustered": clustered,
        "profile": profile,
        "pca_coordinates": coordinates,
        "pca_explained_variance": pca.explained_variance_ratio_,
        "stability": kmeans_stability(scaled),
        "dbscan": dbscan_comparison(scaled),
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = solve(root / "data" / "market_regimes.csv")
    print(result["selection"])
    print(result["profile"])
    print(result["stability"].describe())
    print({key: value for key, value in result["dbscan"].items() if key != "labels"})
