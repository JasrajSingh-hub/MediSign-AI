# MediSign-AI Model V2 (Augmented) Validation Report

This report presents a detailed validation analysis of the newly trained Emergency Gesture Recognition Model (V2), which incorporates video data augmentations.

## 1. Executive Performance Metrics
* **Total Validation Samples**: `12665` frames
* **Accuracy**: `97.4497%`
* **Macro F1 Score**: `97.4363%`
* **Mean Inference Latency**: `0.1157 ms` per frame
* **Model Size**: `15545.27 KB`

## 2. Per-Class Detailed Performance

| Class Label | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| `accident` | 97.94% | 98.55% | 98.24% | 2412 |
| `call` | 96.54% | 96.11% | 96.32% | 2030 |
| `doctor` | 96.43% | 99.24% | 97.81% | 1962 |
| `help` | 99.01% | 97.89% | 98.45% | 1946 |
| `hot` | 97.72% | 94.46% | 96.06% | 2130 |
| `pain` | 97.07% | 98.40% | 97.73% | 2185 |

## 3. Confusion Matrix Breakdown
| True \ Pred | `accident` | `call` | `doctor` | `help` | `hot` | `pain` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `accident` | 2377 | 1 | 18 | 12 | 3 | 1 |
| `call` | 7 | 1951 | 28 | 2 | 27 | 15 |
| `doctor` | 2 | 2 | 1947 | 5 | 1 | 5 |
| `help` | 28 | 0 | 12 | 1905 | 1 | 0 |
| `hot` | 6 | 57 | 11 | 0 | 2012 | 44 |
| `pain` | 7 | 10 | 3 | 0 | 15 | 2150 |

## 4. Quality Limitations & Insights
* **Robustness**: The V2 model was trained on video sequences modified with random brightness shifts, translation offsets, CLAHE adjustments, and rotational offsets. This increases generalizability under camera shake and variable room illumination.
* **Tracking Check**: Only augmented videos where MediaPipe HandLandmarker tracked hand landmarks successfully in `>80%` of frames were used for feature extraction, ensuring data integrity.
