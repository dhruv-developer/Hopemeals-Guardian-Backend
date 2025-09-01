# filename: app/ml/anomaly.py
"""
Anomaly detection utilities for Hopemeals Guardian.

Provides a small, self-contained wrapper around IsolationForest with:
- feature building integration
- percentile-based thresholding
- rule-based reason codes for explainability
- graceful fallback when sample sizes are small

Intended usage:
    from app.ml.anomaly import analyze_events

    alerts = analyze_events(events, contamination=0.03)
    # => list of {"event_id", "score", "severity", "reasons"}

Notes
-----
- Higher scores indicate more anomalous samples.
- Severity mapping (default):
    score >= p99 -> 3
    score >= p97 -> 2
    else        -> 0 (not returned)
- Reasons are basic, rule-based complements to the model score and are
  derived from the current demo feature set.

Dependencies: scikit-learn, numpy
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np
from sklearn.ensemble import IsolationForest

from app.utils.features import build_features


# ------------------------------
# Core helpers
# ------------------------------


def train_iforest(
    X: Sequence[Sequence[float]],
    contamination: float = 0.03,
    random_state: int = 42,
) -> IsolationForest:
    """
    Fit an IsolationForest model on X.

    Parameters
    ----------
    X : 2D sequence of shape (n_samples, n_features)
    contamination : float
        Proportion of outliers in the data set.
    random_state : int
        RNG seed for reproducibility.

    Returns
    -------
    IsolationForest
    """
    X = np.asarray(X, dtype=float)
    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=200,
        max_samples="auto",
        n_jobs=-1,
    )
    model.fit(X)
    return model


def anomaly_scores(model: IsolationForest, X: Sequence[Sequence[float]]) -> np.ndarray:
    """
    Return anomaly scores where higher = more anomalous.
    Using negative of sklearn's score_samples (which is higher for inliers).
    """
    X = np.asarray(X, dtype=float)
    return -model.score_samples(X)


def threshold_by_percentile(scores: np.ndarray, pct: float = 97.0) -> float:
    """Percentile threshold (inclusive) for flagging anomalies."""
    if scores.size == 0:
        return float("inf")
    pct = float(np.clip(pct, 0.0, 100.0))
    return float(np.percentile(scores, pct))


# ------------------------------
# Reason extraction (rule-based)
# ------------------------------


def derive_reasons_from_features(
    feat: Sequence[float],
    qty_surge_threshold: float = 240.0,
    jump_impossible_km: float = 500.0,
) -> List[str]:
    """
    Map the current 4D feature vector to human-readable reasons.

    Expected feature order (per app.utils.features.build_features):
        [quantity, hour, gps_jump_km, unique_beneficiaries]
    """
    reasons: List[str] = []
    try:
        qty, hour, jump, uniq_b = feat
    except Exception:
        return reasons

    if float(qty) > qty_surge_threshold:
        reasons.append("surge_volume")
    if float(jump) > jump_impossible_km:
        reasons.append("impossible_route")
    # Optional: low unique beneficiaries with high quantity
    if float(qty) >= 150.0 and float(uniq_b) <= 1.0:
        reasons.append("beneficiary_anomaly")
    # Optional: unusual hour (very late night) can be a weak signal
    if int(hour) in (0, 1, 2, 3, 4):
        reasons.append("odd_hour_activity")

    return reasons


# ------------------------------
# Fallback heuristic (small n)
# ------------------------------


def heuristic_scores(X: Sequence[Sequence[float]]) -> np.ndarray:
    """
    Lightweight scoring when not enough data is available to fit a model.
    Emphasize quantity and GPS jump (km).
    """
    X = np.asarray(X, dtype=float)
    if X.size == 0:
        return np.array([], dtype=float)
    # weights: qty (1x), jump (5x), weak penalty for off-hour if hour in [0..4]
    qty = X[:, 0]
    hour = X[:, 1]
    jump = X[:, 2]
    off_hour_bonus = np.where(np.isin(hour.astype(int), [0, 1, 2, 3, 4]), 15.0, 0.0)
    return qty + 5.0 * jump + off_hour_bonus


# ------------------------------
# Public API: analyze_events
# ------------------------------


def analyze_events(
    events: Iterable[Dict[str, Any]],
    contamination: float = 0.03,
    p97: float = 97.0,
    p99: float = 99.0,
    min_samples_for_model: int = 20,
) -> List[Dict[str, Any]]:
    """
    Analyze raw event documents and produce alert candidates.

    Parameters
    ----------
    events : iterable of dict
        Each event must contain keys expected by build_features().
    contamination : float
        IsolationForest contamination parameter.
    p97 : float
        Percentile threshold for severity 2.
    p99 : float
        Percentile threshold for severity 3.
    min_samples_for_model : int
        Minimum number of samples required to fit IsolationForest.
        If not met, a heuristic scorer is used.

    Returns
    -------
    List[dict]
        Each dict contains: event_id, score, severity, reasons
    """
    events_list = list(events)
    if not events_list:
        return []

    X, meta = build_features(events_list)  # X: List[List[float]], meta: List[event_id]
    if not X or not meta:
        return []

    # Choose model or heuristic based on data volume
    if len(X) >= min_samples_for_model:
        model = train_iforest(X, contamination=contamination)
        scores = anomaly_scores(model, X)
    else:
        scores = heuristic_scores(X)

    # Compute thresholds
    thr97 = threshold_by_percentile(scores, p97)
    thr99 = threshold_by_percentile(scores, p99)

    alerts: List[Dict[str, Any]] = []
    for eid, s, feat in zip(meta, scores, X):
        sev = 0
        if s >= thr99:
            sev = 3
        elif s >= thr97:
            sev = 2

        reasons = derive_reasons_from_features(feat)
        # escalate severity if strong reasons exist
        if "impossible_route" in reasons:
            sev = max(sev, 3)
        elif reasons:
            sev = max(sev, 2)

        if sev > 0:
            alerts.append(
                {
                    "event_id": eid,
                    "score": float(s),
                    "severity": int(sev),
                    "reasons": reasons if reasons else ["model_anomaly"],
                }
            )

    return alerts
