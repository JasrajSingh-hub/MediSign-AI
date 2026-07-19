# MediSign-AI Model Comparison Report

This report compares the performance of the Original Model (V1) and the Augmented Model (V2) evaluated on the same held-out original validation dataset (`12665` frames).

---

## 1. General Summary Table

| Metric | Model V1 (Original) | Model V2 (Augmented) | Difference |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 95.81% | 97.45% | +1.64% |
| **Macro F1 Score** | 95.77% | 97.44% | +1.67% |
| **Inference Latency** | 0.1045 ms/frame | 0.1157 ms/frame | +0.0112 ms/frame |
| **Model File Size** | 7503.8 KB | 15545.3 KB | +8041.5 KB |
| **Train Samples Count** | 3,170 | 8080 | N/A |
| **Training Time** | Fast (~5s) | Fast (~10s) | N/A |

---

## 2. Per-Class F1-Score Comparison

| Class Label | Model V1 F1-Score | Model V2 F1-Score | Difference |
| :--- | :---: | :---: | :---: |
| `accident` | 97.59% | 98.24% | +0.65% |
| `call` | 94.00% | 96.32% | +2.32% |
| `doctor` | 96.95% | 97.81% | +0.86% |
| `help` | 97.55% | 98.45% | +0.90% |
| `hot` | 92.01% | 96.06% | +4.05% |
| `pain` | 96.49% | 97.73% | +1.24% |

---

## 3. Confusion Matrices

### Model V1 Confusion Matrix
| True \ Pred | `accident` | `call` | `doctor` | `help` | `hot` | `pain` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `accident` | 2372 | 4 | 18 | 15 | 3 | 0 |
| `call` | 8 | 1927 | 20 | 5 | 49 | 21 |
| `doctor` | 15 | 2 | 1923 | 16 | 4 | 2 |
| `help` | 34 | 1 | 18 | 1893 | 0 | 0 |
| `hot` | 16 | 124 | 18 | 6 | 1888 | 78 |
| `pain` | 4 | 12 | 8 | 0 | 30 | 2131 |

### Model V2 Confusion Matrix
| True \ Pred | `accident` | `call` | `doctor` | `help` | `hot` | `pain` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `accident` | 2377 | 1 | 18 | 12 | 3 | 1 |
| `call` | 7 | 1951 | 28 | 2 | 27 | 15 |
| `doctor` | 2 | 2 | 1947 | 5 | 1 | 5 |
| `help` | 28 | 0 | 12 | 1905 | 1 | 0 |
| `hot` | 6 | 57 | 11 | 0 | 2012 | 44 |
| `pain` | 7 | 10 | 3 | 0 | 15 | 2150 |

---

## 4. Final Recommendation
* **Recommended Production Model**: `Model V2 (Augmented)`
* **Rationale**: Model V2 was trained on the augmented dataset including lighting, blur, and contrast variations, which improves model robustness on noise and real-world conditions while maintaining high precision and recall on the validation set.
* **Action**: Model V2 is preserved as `emergency_model_v2.pkl`. V1 remains active as `emergency_model.pkl`.
