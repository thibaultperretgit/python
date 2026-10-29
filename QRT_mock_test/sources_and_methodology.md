# Sources and methodology

Prepared on 2026-10-28. This document distinguishes direct brief evidence, public corroboration, and design assumptions. Candidate reports are useful preparation signals, not official promises.

## Evidence grading

| Claim | Evidence status | How it is used here |
|---|---|---|
| 82 minutes; 1 coding data-science task; 10 math; 5 ML fundamentals; 8 ML advanced | Direct user brief, transcribed from the referenced screenshot. The image itself was not machine-readable in this continuation. | Treated as authoritative for this mock. |
| Four sections with exactly 1 + 10 + 5 + 8 items | Corroborated by a recent third-party guide summarizing candidate reports. | Reinforces the section structure. |
| The 23 non-coding questions are multiple choice, with some select-all questions | Reported by the same third-party guide; not published by QRT. | Used as a realistic mock convention. Every select-all item is explicitly labeled. |
| Coding is Python/data-science oriented | Corroborated by public candidate reports and by the third-party guide's description of a pandas task. | The notebook uses pandas on a synthetic panel. |
| Math/statistics and ML topics include OLS, probability, regularization, cross-validation, tree ensembles, optimization, feature importance, and hyperparameter tuning | Repeated across public candidate reports and interview aggregators. | Used only as a topic blueprint; every question here is original. |
| HackerRank, webcam proctoring, one overall clock, exact scoring, back navigation, calculator rules, negative marking | Unverified or inconsistently reported. | Not simulated or asserted. |

## Public sources

1. [QRT official Students and New Grads page](https://www.qube-rt.com/careers/research-and-trading/london/students-and-new-graduates/) - official evidence that QRT recruits into Research and Trading, but it does not publish an assessment blueprint.
2. [TraderMath QRT interview guide](https://www.tradermath.org/articles/qube-research-technologies-interview-guide) - a third-party synthesis that reports a 90-minute assessment with the same 1/10/5/8 section counts, and describes the 23 theory questions as a mix of single-answer and select-all MCQ. Its 90-minute report conflicts with the 82-minute direct brief, so this mock uses 82 minutes.
3. [Glassdoor Qube Research & Technologies interview page](https://www.glassdoor.com/Interview/Qube-Research-and-Technologies-Interview-Questions-E3226090.htm) - anonymous reports show probability, statistics, machine learning, OLS, XGBoost, LightGBM, and random forests, while also showing that process details vary.
4. [Wall Street Oasis Qube Research & Technologies interview entries](https://www.wallstreetoasis.com/company/qube-research-and-technologies/interview) - anonymous reports mention z-scores, p-values, regression, penalization, high-dimensional ML, and random forests. The same page also reports a LeetCode-style assessment for a quantitative developer role, illustrating why adjacent-role formats should not be generalized to this research mock.

## Design decisions

- **Timing:** 42 minutes coding + 18 mathematics + 8 ML fundamentals + 14 ML advanced = 82 minutes. This is a practice recommendation, not a claimed QRT rule.
- **Question type:** all 23 theory questions are MCQ. Five are select-all, clearly marked; exact-match scoring is suggested for those items.
- **Difficulty:** questions emphasize fast conceptual reasoning and short calculations rather than lengthy derivations.
- **Originality:** reported topic families shaped coverage, but no purported live question or leaked wording was reproduced.
- **Coding realism:** the notebook tests common research-data operations under time pressure: deterministic deduplication, groupwise imputation, winsorization, cross-sectional normalization, time-based holdout evaluation, long-short aggregation, and rank correlation.
- **Synthetic data:** the dataset contains no real securities or proprietary data. A fixed seed makes every expected output reproducible.

## Known uncertainty

The public sources do not establish the live test's platform, proctoring setup, permitted references, scoring thresholds, question randomization, calculator policy, or ability to move between sections. Use the actual invitation and on-screen rules if they differ from this mock.
