# Scikit-learn mock assessments: answer key and reference metrics

Open this file only after attempting the candidate notebooks. The complete implementations are in the three adjacent `*_reference.py` files.

All results below use the shipped deterministic CSV files, the stated random seeds, and scikit-learn defaults except where a notebook specifies otherwise. Small floating-point differences are acceptable.

## Mock 1 - Cement-strength classification

### Intended sequence

1. Audit schemas, duplicate IDs, missing values, and training-label balance.
2. Select only the five ingredient and curing features.
3. Make a 75%/25% stratified split with `random_state=20261101`.
4. Fit median imputation, `StandardScaler`, and `LogisticRegression` inside one pipeline.
5. Compare validation performance with a prior-frequency dummy classifier.
6. Freeze the model, refit on all 1,200 training rows, and evaluate the 300 protected test rows once.
7. Extract a prediction audit and standardized coefficients.

The train data contains 620 weak and 580 strong observations. The protected test contains 155 weak and 145 strong observations.

### Reference results

| Split/model | Accuracy | Balanced accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|
| Validation dummy | 0.516667 | 0.500000 | 0.000000 | 0.000000 | 0.000000 | 0.500000 |
| Validation logistic | 0.836667 | 0.834594 | 0.875000 | 0.772414 | 0.820513 | 0.914127 |
| Test logistic | 0.833333 | 0.832036 | 0.851852 | 0.793103 | 0.821429 | 0.919911 |

Test confusion matrix, with actual classes as rows and predicted classes as columns:

```text
[[135, 20],
 [ 30, 115]]
```

The largest standardized effects are positive cement content, positive curing time, positive superplasticizer, negative water, and positive blast-furnace slag. These are predictive effects in synthetic data, not causal estimates.

If accepting weak cement is the expensive error, a false positive is more costly. Threshold selection should therefore emphasize precision, a cost-weighted rule, or an explicit false-positive constraint rather than blindly maximizing accuracy.

### Optional extension

- Search thresholds using validation probabilities only; never optimize a threshold on test labels.
- A random forest can capture nonlinear interactions, but compare it on the same untouched validation partition.
- Calibration and ranking are different: ROC-AUC can remain strong even if predicted probabilities are poorly calibrated.

## Mock 2 - Market-regime clustering

### Intended sequence

1. Exclude `date`, median-impute if necessary, and standardize all five features.
2. Fit KMeans for `k=2` through `k=6` with `n_init=20` and `random_state=20261102`.
3. Select `k=3` from the silhouette maximum and the interpretable original-unit profiles.
4. Fit final KMeans on all five scaled features.
5. Use PCA only to visualize the fitted assignments.

### Model-selection results

| k | Inertia | Silhouette |
|---:|---:|---:|
| 2 | 2071.306206 | 0.517725 |
| 3 | 847.930546 | 0.593564 |
| 4 | 757.184157 | 0.505729 |
| 5 | 668.206894 | 0.327396 |
| 6 | 610.715625 | 0.322901 |

### Regime profiles

Cluster numbers may be permuted by another valid implementation. Match regimes from their profiles rather than the numeric ID.

| Reference cluster | Interpretation | Count | Share | Return 5d | Volatility 20d | Volume z | Correlation | Drawdown 60d |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | Stressed/risk-off | 247 | 0.274444 | -0.020900 | 0.031061 | 0.522805 | 0.756139 | -0.210977 |
| 1 | Neutral/high-activity | 442 | 0.491111 | 0.001062 | 0.017124 | 1.002838 | 0.483056 | -0.081211 |
| 2 | Calm/risk-on | 211 | 0.234444 | 0.011772 | 0.008031 | -0.473606 | 0.223304 | -0.018419 |

The first two principal components explain approximately 0.7230 and 0.1718 of standardized variance. KMeans assignments are perfectly stable across the supplied seed check because the synthetic groups are deliberately clear enough for a timed assessment.

### Optional DBSCAN extension

With `eps=0.75` and `min_samples=12`, the reference solution finds three non-noise clusters, labels about 6.33% of rows as noise, and obtains a silhouette of approximately 0.6140 after excluding noise. DBSCAN can leave observations unassigned; KMeans cannot.

## Mock 3 - Next-period volatility regression

### Intended sequence

1. Keep dates ordered and split the training file 80%/20% without shuffling.
2. Use `TimeSeriesSplit(n_splits=5, gap=5)` inside `GridSearchCV`.
3. Search Ridge alpha over `[0.01, 0.1, 1.0, 10.0, 100.0]` using negative MAE.
4. Compare with a mean dummy regressor on the final validation block.
5. Freeze alpha, refit on all training rows, and evaluate the later protected test period once.
6. Audit predictions, residuals, and standardized coefficients.

The selected alpha is `0.01`.

### Reference results

| Split/model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Validation dummy | 0.006176 | 0.007030 | -0.482201 |
| Validation Ridge | 0.003344 | 0.004230 | 0.463325 |
| Test dummy | 0.004401 | 0.005289 | -0.424155 |
| Test Ridge | 0.002747 | 0.003446 | 0.395342 |

Ridge reduces test MAE by approximately 37.6% relative to the dummy model. The largest standardized coefficient belongs to cross-asset correlation, followed by trailing 20-day and 5-day volatility. These coefficients describe association after standardization, not causality.

### Optional extension

The reference random forest obtains validation MAE of approximately `0.003146`, slightly better than Ridge on that one block. That is not enough evidence to declare it superior: it adds complexity, is less stable to regime change, and still needs walk-forward validation. Permutation importance must be calculated on validation data, not the fitting sample.

## General leakage checklist

- Fit imputers, scalers, PCA, and models only in the appropriate training boundary.
- Never use IDs as numeric predictors.
- Do not tune a threshold, model, or hyperparameter on protected test labels.
- Preserve time ordering for forward-looking market targets.
- Treat feature importance and coefficients as model diagnostics, not causal conclusions.
