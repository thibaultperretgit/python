# Answer key and reference notes

Open this file only after completing the 82-minute mock. Select-all questions use exact-match scoring in this key.

## Mathematics and statistics

| Q | Answer | Rationale |
|---:|:---:|---|
| 1 | C | Bayes: `0.20*0.60 / (0.20*0.60 + 0.80*0.10) = 0.60`. |
| 2 | C | Gamma-Poisson conjugacy gives posterior shape `3+11=14`, rate `2+3=5`, so the posterior mean is `14/5=2.8`. |
| 3 | D | For `Uniform(0, theta)`, `E[X]=theta/2`; equating this to 4.2 gives `theta=8.4`. |
| 4 | D | The fitted line passes through the sample means: `a = y_bar - b*x_bar = 0.7 - (-0.8)(1.5) = 1.9`. |
| 5 | B | The z-score is `(58-50)/4 = 2`. |
| 6 | C | The third row is the sum of the first two, while the first two are independent, so the rank is 2. |
| 7 | B | The integral of `x+2y` on the unit square is `1/2+1=3/2`; therefore `c=2/3`. |
| 8 | C | Degrees of freedom are `categories - 1 - fitted_parameters = 7-1-2 = 4`. |
| 9 | C | `Var(2X-Y) = 4 Var(X) + Var(Y) - 4 Cov(X,Y) = 16+9-12 = 13`. |
| 10 | A, B | Full column rank gives a unique OLS coefficient vector, and zero conditional mean gives conditional unbiasedness. Homoskedasticity and normality are not required for those two properties. |

## Machine-learning fundamentals

| Q | Answer | Rationale |
|---:|:---:|---|
| 11 | C | Fitting a scaler before the split lets validation information affect training-time preprocessing. |
| 12 | A, C, D | Stronger penalties usually add bias; Lasso can create exact zeros; scale affects the relative penalty. Ridge generally does not create exact zeros, and stronger regularization usually reduces variance. |
| 13 | B | PR-AUC focuses on positive-class precision and recall and is usually more informative than raw accuracy when positives are rare. |
| 14 | C | An expanding-window split preserves chronology and trains only on data available before each validation block. |
| 15 | B | K-means learns structure without labeled targets, so it is unsupervised. |

## Advanced machine learning

| Q | Answer | Rationale |
|---:|:---:|---|
| 16 | A, B | Bootstrap sampling and random feature subsets reduce tree correlation; deeper trees alone do not create the same decorrelation mechanism. |
| 17 | B | Under squared error, the negative gradient is the current residual, so the next weak learner fits residual-like targets. |
| 18 | A, C | Adam tracks exponential moving averages of first and second moments and uses them for parameter-specific scaling. It does not guarantee a global optimum or remove learning-rate tuning. |
| 19 | C | PCA must be fitted inside each training fold and then applied to that fold's validation data to avoid leakage. |
| 20 | A, D | A correlated partner can substitute for a permuted feature, understating individual importance; permuting the correlated group is a useful sensitivity check. |
| 21 | B | The inner loop selects hyperparameters; the untouched outer folds estimate the full selection procedure's generalization performance. |
| 22 | A | A strictly increasing transform preserves score order and therefore ROC-AUC, but it can change probability calibration and log loss. |
| 23 | C | Stable `P(X)` with changed `P(Y|X)` is concept drift (also called real drift). |

## Coding question

The full implementation is in `coding_reference_solution.py`. The intended sequence is:

1. parse timestamps, stable-sort, and keep the latest duplicate;
2. impute by `(date, sector)` median with a date-median fallback;
3. winsorize within date at 5% and 95%;
4. compute daily population z-scores;
5. filter the holdout starting 2025-06-02;
6. deterministically take six assets per tail on each 30-asset day;
7. compute the long-minus-short return and rank IC;
8. summarize the 53 holdout days.

With the shipped deterministic CSV and the stated conventions, the reference metrics are:

| Metric | Expected value |
|---|---:|
| `n_days` | 53 |
| `annualized_return` | 0.443213 |
| `annualized_volatility` | 0.101345 |
| `sharpe_ratio` | 4.373326 |
| `mean_rank_ic` | 0.078079 |
| `positive_day_rate` | 0.660377 |
| `max_drawdown` | -0.019381 |

Small floating-point differences in the last decimal are acceptable. The intentionally strong synthetic performance makes implementation errors easier to spot; it is not a plausible claim about a real tradable strategy because the mock omits costs, market impact, borrow constraints, selection bias, and live-regime uncertainty.
