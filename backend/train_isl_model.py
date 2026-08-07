from __future__ import annotations

import ast
import csv
import json
import random
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = Path(r"C:\Users\jasuj\Downloads\new_dta(1 without p ).csv")
DEFAULT_OUTPUT = BASE_DIR / "models" / "isl_trained_model.json"
RANDOM_SEED = 42


@dataclass
class TrainedPackage:
    modelName: str
    exportedAt: str
    activeDatasetName: str
    metrics: dict
    hyperparameters: dict
    samples: list[dict]


def read_dataset(csv_path: Path) -> list[dict]:
    rows: list[dict] = []
    with csv_path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            label = str(row["label"]).strip()
            data = ast.literal_eval(row["data"])
            rows.append({
                "id": row.get("id") or f"sample-{len(rows) + 1}",
                "label": label,
                "data": [float(value) for value in data],
            })
    return rows


def combined_distance(a: np.ndarray, b: np.ndarray, similarity_weight: float = 0.7) -> float:
    euclidean = float(np.linalg.norm(a - b))
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    cosine = 1.0 if denominator == 0 else float(np.dot(a, b) / denominator)
    cosine_distance = 1.0 - max(-1.0, min(1.0, cosine))
    return similarity_weight * euclidean + (1.0 - similarity_weight) * cosine_distance


def predict_knn(samples: list[dict], query: np.ndarray, k: int = 3, similarity_weight: float = 0.7) -> str:
    vectors = np.asarray([sample["data"] for sample in samples], dtype=np.float64)
    labels = [sample["label"] for sample in samples]
    distances = np.asarray([combined_distance(query, vector, similarity_weight) for vector in vectors], dtype=np.float64)
    k = max(1, min(k, len(distances)))
    neighbour_indices = np.argpartition(distances, k - 1)[:k]
    counts: Counter[str] = Counter(labels[index] for index in neighbour_indices)
    return counts.most_common(1)[0][0]


def evaluate(samples: list[dict], k: int = 3, similarity_weight: float = 0.7, holdout_ratio: float = 0.2) -> float:
    rng = random.Random(RANDOM_SEED)
    shuffled = samples[:]
    rng.shuffle(shuffled)
    split_index = max(1, int(len(shuffled) * (1.0 - holdout_ratio)))
    train_samples = shuffled[:split_index]
    test_samples = shuffled[split_index:]
    if not test_samples:
        return 1.0

    correct = 0
    for sample in test_samples:
        prediction = predict_knn(train_samples, np.asarray(sample["data"], dtype=np.float64), k=k, similarity_weight=similarity_weight)
        correct += int(prediction == sample["label"])
    return correct / len(test_samples)


def build_package(samples: list[dict], dataset_name: str) -> TrainedPackage:
    labels = [sample["label"] for sample in samples]
    active_classes = sorted(set(labels))
    k_neighbors = 3
    similarity_weight = 0.7
    accuracy = evaluate(samples, k=k_neighbors, similarity_weight=similarity_weight)
    return TrainedPackage(
        modelName="ISL Landmark Classifier Model",
        exportedAt=datetime.now(timezone.utc).isoformat(),
        activeDatasetName=dataset_name,
        metrics={
            "totalSamples": len(samples),
            "activeSamples": len(samples),
            "accuracy": f"{accuracy * 100:.1f}%",
            "activeClasses": active_classes,
        },
        hyperparameters={
            "kNeighbors": k_neighbors,
            "distanceMetric": "combined",
            "similarityWeight": similarity_weight,
            "outlierFiltering": False,
            "singleHandOptimization": True,
        },
        samples=samples,
    )


def main() -> None:
    csv_path = DEFAULT_INPUT
    output_path = DEFAULT_OUTPUT
    samples = read_dataset(csv_path)
    package = build_package(samples, dataset_name=csv_path.stem)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(asdict(package), fh, indent=2)
    print(f"Wrote {output_path}")
    print(f"Samples: {len(samples)}")
    print(f"Accuracy: {package.metrics['accuracy']}")


if __name__ == "__main__":
    main()

