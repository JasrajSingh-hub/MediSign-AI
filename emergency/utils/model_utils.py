"""Model training and evaluation utilities (Phase 7).

The data-loading, stratified train/test split, and metric computation are
**pure Python** (no scikit-learn) so they are unit-testable offline. The
RandomForest, cross-validation, grid search, and model serialisation import
scikit-learn / joblib **lazily** and are skipped with a clear note when those
packages are absent.
"""
from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import config
from config import PATHS
from utils.io_utils import ensure_dir
from utils.logger import get_logger

logger = get_logger(__name__)

_METADATA_COLS = ["label", "video", "frame", "handedness", "score"]


# ---------------------------------------------------------------------------
# Pure helpers (offline-testable)
# ---------------------------------------------------------------------------
def load_features_csv(path: str | Path) -> Dict[str, object]:
    """Load a Phase-6 ``features.csv`` into feature matrix ``X`` and labels ``y``.

    Returns a dict with ``X`` (list of feature lists), ``y`` (list of labels),
    and ``feature_names`` (all non-metadata columns).
    """
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        feature_names = [c for c in reader.fieldnames if c not in _METADATA_COLS]
        X: List[List[float]] = []
        y: List[str] = []
        for row in reader:
            X.append([float(row[c]) for c in feature_names])
            y.append(row.get("label", ""))
    return {"X": X, "y": y, "feature_names": feature_names}


def train_test_split_stratified(
    X: List[List[float]],
    y: List[str],
    test_size: float = 0.2,
    random_seed: int = 42,
    stratify: bool = True,
) -> Tuple[List, List, List, List]:
    """Deterministic, reproducible stratified train/test split (pure Python).

    With ``stratify=True`` each label contributes proportionally to the test
    set, preserving class balance.
    """
    rng = random.Random(random_seed)
    if not stratify:
        idx = list(range(len(y)))
        rng.shuffle(idx)
        n_test = int(len(idx) * test_size)
        test_idx = idx[:n_test]
        train_idx = idx[n_test:]
    else:
        by_label: Dict[str, List[int]] = {}
        for i, label in enumerate(y):
            by_label.setdefault(label, []).append(i)
        train_idx: List[int] = []
        test_idx: List[int] = []
        for label, indices in by_label.items():
            rng.shuffle(indices)
            n_test = int(len(indices) * test_size)
            test_idx.extend(indices[:n_test])
            train_idx.extend(indices[n_test:])
        rng.shuffle(train_idx)
        rng.shuffle(test_idx)
    X_train = [X[i] for i in train_idx]
    y_train = [y[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_test = [y[i] for i in test_idx]
    return X_train, y_train, X_test, y_test


def classification_metrics(y_true: List[str], y_pred: List[str], labels: List[str]) -> Dict[str, object]:
    """Compute accuracy, per-class precision/recall/F1, macro-F1, confusion matrix.

    Pure Python — no scikit-learn required.
    """
    total = len(y_true)
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    accuracy = correct / total if total else 0.0

    cm: Dict[str, Dict[str, int]] = {t: {p: 0 for p in labels} for t in labels}
    for t, p in zip(y_true, y_pred):
        if t in cm and p in cm[t]:
            cm[t][p] += 1

    per_class: Dict[str, Dict[str, float]] = {}
    for l in labels:
        tp = cm[l][l]
        fp = sum(cm[o][l] for o in labels if o != l)
        fn = sum(cm[l][o] for o in labels if o != l)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        per_class[l] = {"precision": precision, "recall": recall, "f1": f1, "support": tp + fn}

    macro_f1 = sum(per_class[l]["f1"] for l in labels) / len(labels) if labels else 0.0
    return {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "per_class": per_class,
        "confusion_matrix": cm,
        "labels": labels,
    }


# ---------------------------------------------------------------------------
# scikit-learn backed training (lazy)
# ---------------------------------------------------------------------------
def build_model(params: Dict) -> "object":
    """Construct a ``RandomForestClassifier`` (lazy import)."""
    from sklearn.ensemble import RandomForestClassifier

    return RandomForestClassifier(
        n_estimators=int(params.get("n_estimators", 200)),
        max_depth=(int(params["max_depth"]) if params.get("max_depth") else None),
        min_samples_leaf=int(params.get("min_samples_leaf", 2)),
        random_state=int(params.get("random_state", 42)),
        n_jobs=-1,
    )


def cross_validate(
    X: List[List[float]], y: List[str], params: Dict, n_splits: int = 5, seed: int = 42
) -> Dict[str, object]:
    """Stratified k-fold cross-validation, returning f1_macro mean/std."""
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    model = build_model(params)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    scores = cross_val_score(model, X, y, cv=skf, scoring="f1_macro")
    return {
        "scoring": "f1_macro",
        "n_splits": n_splits,
        "mean": float(scores.mean()),
        "std": float(scores.std()),
        "folds": [float(s) for s in scores],
    }


def build_param_grid(params: Optional[Dict] = None) -> Dict[str, List]:
    """Default grid-search space around the supplied base params."""
    params = params or {}
    n_est = int(params.get("n_estimators", 200))
    depth = params.get("max_depth", 20)
    depth = int(depth) if depth else 20
    return {
        "n_estimators": [max(50, n_est - 100), n_est, n_est + 100],
        "max_depth": [max(5, depth - 10), depth, depth + 10],
        "min_samples_leaf": [1, 2, 4],
    }


def grid_search(
    X: List[List[float]], y: List[str], param_grid: Dict, n_splits: int = 5, seed: int = 42
) -> Tuple["object", Dict, Dict]:
    """Run ``GridSearchCV`` (f1_macro) and return (best_model, best_params, info)."""
    from sklearn.model_selection import GridSearchCV

    gs = GridSearchCV(
        build_model({"random_state": seed}),
        param_grid,
        cv=StratifiedKFoldSafe(n_splits, seed),
        scoring="f1_macro",
        n_jobs=-1,
    )
    gs.fit(X, y)
    return gs.best_estimator_, dict(gs.best_params_), {"best_score": float(gs.best_score_)}


def StratifiedKFoldSafe(n_splits: int, seed: int):
    from sklearn.model_selection import StratifiedKFold

    return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)


def save_model(model: "object", path: str | Path) -> Path:
    """Persist a trained model with joblib (lazy import)."""
    import joblib

    path = Path(path)
    ensure_dir(path.parent)
    joblib.dump(model, path)
    logger.info("Saved model -> %s", path)
    return path


def load_model(path: str | Path) -> "object":
    """Load a joblib-serialised model (lazy import)."""
    import joblib

    return joblib.load(Path(path))


def predict(model: "object", X: List[List[float]]) -> Tuple[List[str], List[List[float]]]:
    """Return ``(predictions, class_probabilities)`` for a trained model."""
    preds = model.predict(X)
    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    # Align probabilities to a per-class list regardless of internal order.
    return list(preds), [list(p) for p in proba], classes


# ---------------------------------------------------------------------------
# Reporting + orchestration
# ---------------------------------------------------------------------------
def write_training_report(result: Dict[str, object], reports_dir: str | Path) -> tuple[Path, Path]:
    """Write ``training_report.md`` and ``training_report.json``."""
    reports_dir = ensure_dir(reports_dir)
    md = reports_dir / "training_report.md"
    js = reports_dir / "training_report.json"
    lines = [
        "# Training Report — Emergency Gesture Recognition",
        "",
        f"- **Train samples:** {result.get('train_size')}",
        f"- **Test samples:** {result.get('test_size')}",
        f"- **Classes:** {', '.join(result.get('labels', []))}",
        f"- **Model file:** `{result.get('model_path', 'skipped')}`",
        "",
        "## Hyperparameters",
        "",
        "```json",
        json.dumps(result.get("params", {}), indent=2),
        "```",
        "",
    ]
    cv = result.get("cross_validation")
    if cv:
        lines += [
            "## Cross-validation (f1_macro)",
            "",
            f"- **Mean:** {cv['mean']:.4f}  **Std:** {cv['std']:.4f}",
            f"- **Folds:** {cv['folds']}",
            "",
        ]
    gs = result.get("grid_search")
    if gs:
        lines += ["## Grid search", "", f"- **Best params:** `{gs['best_params']}`", f"- **Best score:** {gs['best_score']:.4f}", ""]
    ev = result.get("evaluation")
    if ev:
        lines += [
            "## Evaluation (test set)",
            "",
            f"- **Accuracy:** {ev['accuracy']:.4f}",
            f"- **Macro-F1:** {ev['macro_f1']:.4f}",
            "",
            "| Class | Precision | Recall | F1 | Support |",
            "|-------|----------:|-------:|---:|--------:|",
        ]
        for l in ev["labels"]:
            pc = ev["per_class"][l]
            lines.append(f"| {l} | {pc['precision']:.3f} | {pc['recall']:.3f} | {pc['f1']:.3f} | {pc['support']} |")
        lines.append("")
    if result.get("skipped"):
        lines += ["## Note", "", result.get("note", "Training skipped (dependencies unavailable)."), ""]
    md.write_text("\n".join(lines), encoding="utf-8")
    js.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    logger.info("Wrote training report -> %s and %s", md, js)
    return md, js


def run_training(
    features_csv: Optional[str | Path] = None,
    model_path: Optional[str | Path] = None,
    reports_dir: Optional[str | Path] = None,
    *,
    cfg: Optional[Dict] = None,
) -> Dict[str, object]:
    """End-to-end training: load -> split -> (CV / grid search) -> train -> evaluate -> save.

    Skips gracefully (with ``skipped=True``) when scikit-learn is unavailable.
    """
    cfg = cfg or config.CONFIG
    features_csv = Path(features_csv) if features_csv else PATHS["landmarks_dir"] / "features.csv"
    model_path = Path(model_path) if model_path else PATHS["models_dir"] / cfg["training"]["model_filename"]
    rep_dir = Path(reports_dir) if reports_dir else PATHS["reports_dir"]
    tcfg = cfg["training"]
    dcfg = cfg["dataset"]

    if not features_csv.exists():
        logger.warning("Features CSV not found at %s (run Phase 6 first). Skipping training.", features_csv)
        return {"skipped": True, "note": f"Features CSV not found: {features_csv}"}

    data = load_features_csv(features_csv)
    X, y = data["X"], data["y"]
    labels = sorted(set(y))
    X_tr, y_tr, X_te, y_te = train_test_split_stratified(
        X, y, test_size=float(dcfg["train_test_split"]), random_seed=int(dcfg["random_seed"]), stratify=bool(dcfg["stratify"])
    )
    params = {
        "n_estimators": int(tcfg["n_estimators"]),
        "max_depth": int(tcfg["max_depth"]),
        "min_samples_leaf": int(tcfg["min_samples_leaf"]),
        "random_state": int(dcfg["random_seed"]),
    }
    result: Dict[str, object] = {
        "labels": labels,
        "train_size": len(X_tr),
        "test_size": len(X_te),
        "params": params,
        "model_path": str(model_path),
        "skipped": False,
    }

    try:
        import sklearn  # noqa: F401
    except ImportError:
        note = "scikit-learn not installed; train/evaluate skipped. Install deps to train."
        logger.warning(note)
        result["skipped"] = True
        result["note"] = note
        write_training_report(result, rep_dir)
        return result

    n_splits_cv = int(tcfg["n_splits_cv"])
    if len(X_tr) < 2 or len(X_tr) < n_splits_cv:
        note = (
            f"Too few training samples ({len(X_tr)}) to train reliably; "
            f"need at least max(2, n_splits_cv={n_splits_cv}). Skipping training."
        )
        logger.warning(note)
        result["skipped"] = True
        result["note"] = note
        write_training_report(result, rep_dir)
        return result

    cv = cross_validate(X_tr, y_tr, params, n_splits=n_splits_cv, seed=int(dcfg["random_seed"]))
    result["cross_validation"] = cv
    logger.info("CV f1_macro: %.4f +/- %.4f", cv["mean"], cv["std"])

    if tcfg.get("grid_search"):
        grid, best_params, gs_info = grid_search(
            X_tr, y_tr, build_param_grid(params), n_splits=int(tcfg["n_splits_cv"]), seed=int(dcfg["random_seed"])
        )
        result["grid_search"] = {"best_params": best_params, "best_score": gs_info["best_score"]}
        model = grid
        params = best_params
        result["params"] = params
    else:
        model = build_model(params)
        model.fit(X_tr, y_tr)

    preds, _proba, _classes = predict(model, X_te)
    result["evaluation"] = classification_metrics(y_te, preds, labels)
    logger.info("Test accuracy: %.4f | macro-F1: %.4f", result["evaluation"]["accuracy"], result["evaluation"]["macro_f1"])

    save_model(model, model_path)
    write_training_report(result, rep_dir)
    return result
