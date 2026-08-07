from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "isl_trained_model.json"


def _as_float_vector(values: list[float]) -> np.ndarray:
    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1:
        raise ValueError("Expected a flat feature vector.")
    return vector


@dataclass
class ISLTrainedModel:
    active_letters: list[str]
    samples: np.ndarray
    labels: np.ndarray
    k_neighbors: int = 3
    distance_metric: str = "combined"
    similarity_weight: float = 0.7
    test_accuracy: float | None = None

    @classmethod
    def load(cls, path: Path = MODEL_PATH) -> "ISLTrainedModel":
        if not path.exists():
            raise FileNotFoundError(f"ISL model package not found at {path}")

        with path.open("r", encoding="utf-8") as fh:
            payload: dict[str, Any] = json.load(fh)

        samples = payload.get("samples", [])
        if not samples:
            raise ValueError("ISL model package contains no samples.")

        vectors = []
        labels = []
        for sample in samples:
            data = sample.get("data")
            label = sample.get("label")
            if data is None or label is None:
                continue
            vectors.append(_as_float_vector(data))
            labels.append(str(label))

        if not vectors:
            raise ValueError("ISL model package does not contain usable training samples.")

        active_letters = [str(letter) for letter in payload.get("metrics", {}).get("activeClasses", [])]
        if not active_letters:
            active_letters = sorted({label for label in labels})

        hyper = payload.get("hyperparameters", {})
        accuracy_text = payload.get("metrics", {}).get("accuracy")
        try:
            test_accuracy = float(str(accuracy_text).rstrip("%")) / 100.0 if accuracy_text is not None else None
        except ValueError:
            test_accuracy = None

        return cls(
            active_letters=active_letters,
            samples=np.vstack(vectors),
            labels=np.asarray(labels, dtype=object),
            k_neighbors=int(hyper.get("kNeighbors", 3)),
            distance_metric=str(hyper.get("distanceMetric", "combined")),
            similarity_weight=float(hyper.get("similarityWeight", 0.7)),
            test_accuracy=test_accuracy,
        )

    def _distance(self, a: np.ndarray, b: np.ndarray) -> float:
        if self.distance_metric == "combined":
            euclidean = np.linalg.norm(a - b)
            cosine_denom = np.linalg.norm(a) * np.linalg.norm(b)
            cosine = 1.0 if cosine_denom == 0 else float(np.dot(a, b) / cosine_denom)
            cosine_distance = 1.0 - max(-1.0, min(1.0, cosine))
            return self.similarity_weight * euclidean + (1.0 - self.similarity_weight) * cosine_distance
        return float(np.linalg.norm(a - b))

    def predict_one(self, vector: list[float]) -> dict[str, Any]:
        query = _as_float_vector(vector)
        distances = np.asarray([self._distance(query, sample) for sample in self.samples], dtype=np.float64)
        k = max(1, min(self.k_neighbors, len(distances)))
        neighbour_indices = np.argpartition(distances, k - 1)[:k]
        neighbour_pairs = sorted(((float(distances[i]), str(self.labels[i])) for i in neighbour_indices), key=lambda item: item[0])

        scores: dict[str, float] = {}
        for distance, label in neighbour_pairs:
            weight = 1.0 / (distance + 1e-9)
            scores[label] = scores.get(label, 0.0) + weight

        prediction = max(scores.items(), key=lambda item: item[1])[0]
        total_score = sum(scores.values()) or 1.0
        confidence = scores[prediction] / total_score * 100.0
        probabilities = {label: score / total_score for label, score in scores.items()}

        return {
            "letter": prediction,
            "confidence": confidence,
            "probabilities": probabilities,
        }


_MODEL: ISLTrainedModel | None = None


def get_model() -> ISLTrainedModel:
    global _MODEL
    if _MODEL is None:
        _MODEL = ISLTrainedModel.load()
    return _MODEL

