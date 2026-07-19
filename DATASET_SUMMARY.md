# MediSign-AI Augmented Dataset Summary

## General Pipeline Statistics
* **Processing Date**: `2026-07-19 13:57:30`
* **Total Processing Time**: `73327.0 seconds`
* **Concurrence Worker Threads**: `10`
* **Original Videos Count**: `624`
* **Augmented Videos Count**: `925`
* **Source Folder Disk Usage**: `2577.30 MB`
* **Augmented Folder Disk Usage**: `6191.55 MB`

## Batch Tasks Breakdown
* **Successfully Generated Variations**: `924`
* **Skipped (Existing / Resume-mode)**: `1`
* **Rejected (Quality/Hands Constraints)**: `947`
* **Processing Failures**: `0`

## Per-Class Distribution statistics
| Class Label | Original Video Count | Augmented Video Count |
| :--- | :---: | :---: |
| `accident` | 104 | 143 |
| `call` | 104 | 166 |
| `doctor` | 104 | 147 |
| `help` | 104 | 100 |
| `hot` | 104 | 178 |
| `pain` | 104 | 191 |

## Rejected Videos Log
| File Location | Rejection Reason |
| :--- | :--- |
| `accident002_02_aug_01.avi` | `Excessive blur (laplacian var 4.5 < limit 15.0)` |
| `accident001_02_aug_03.avi` | `Excessive blur (laplacian var 5.2 < limit 15.0)` |
| `accident001_02_aug_01.avi` | `Excessive blur (laplacian var 14.6 < limit 15.0)` |
| `accident001_02_aug_02.avi` | `Hand detection rate 21.2% below threshold 80.0%` |
| `accident002_01_aug_01.avi` | `Excessive blur (laplacian var 10.6 < limit 15.0)` |
| `accident002_01_aug_02.avi` | `Hand detection rate 75.0% below threshold 80.0%` |
| `accident002_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident002_02_aug_03.avi` | `Excessive blur (laplacian var 14.9 < limit 15.0)` |
| `accident002_02_aug_02.avi` | `Hand detection rate 1.7% below threshold 80.0%` |
| `accident004_01_aug_01.avi` | `Excessive blur (laplacian var 9.2 < limit 15.0)` |
| `accident003_01_aug_01.avi` | `Excessive blur (laplacian var 7.5 < limit 15.0)` |
| `accident003_01_aug_02.avi` | `Excessive blur (laplacian var 10.3 < limit 15.0)` |
| `accident003_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident003_02_aug_01.avi` | `Hand detection rate 1.3% below threshold 80.0%` |
| `accident003_02_aug_02.avi` | `Excessive blur (laplacian var 8.6 < limit 15.0)` |
| `accident004_01_aug_02.avi` | `Excessive blur (laplacian var 13.1 < limit 15.0)` |
| `accident003_02_aug_03.avi` | `Excessive blur (laplacian var 4.5 < limit 15.0)` |
| `accident004_01_aug_03.avi` | `Hand detection rate 13.3% below threshold 80.0%` |
| `accident004_02_aug_01.avi` | `Excessive blur (laplacian var 10.3 < limit 15.0)` |
| `accident005_01_aug_02.avi` | `Excessive blur (laplacian var 8.3 < limit 15.0)` |
| `accident004_02_aug_03.avi` | `Hand detection rate 46.5% below threshold 80.0%` |
| `accident005_02_aug_01.avi` | `Hand detection rate 62.3% below threshold 80.0%` |
| `accident005_02_aug_02.avi` | `Excessive blur (laplacian var 8.1 < limit 15.0)` |
| `accident005_02_aug_03.avi` | `Excessive blur (laplacian var 6.5 < limit 15.0)` |
| `accident005_01_aug_01.avi` | `Hand detection rate 37.7% below threshold 80.0%` |
| `accident004_02_aug_02.avi` | `Hand detection rate 2.8% below threshold 80.0%` |
| `accident007_01_aug_01.avi` | `Excessive blur (laplacian var 2.8 < limit 15.0)` |
| `accident007_02_aug_01.avi` | `Hand detection rate 74.6% below threshold 80.0%` |
| `accident006_02_aug_02.avi` | `Hand detection rate 52.0% below threshold 80.0%` |
| `accident006_02_aug_03.avi` | `Excessive blur (laplacian var 9.5 < limit 15.0)` |
| `accident007_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident008_01_aug_01.avi` | `Excessive blur (laplacian var 5.3 < limit 15.0)` |
| `accident008_02_aug_02.avi` | `Underexposure (mean luma 33.7 < limit 35.0)` |
| `accident008_02_aug_03.avi` | `Hand detection rate 30.1% below threshold 80.0%` |
| `accident009_01_aug_01.avi` | `Hand detection rate 75.6% below threshold 80.0%` |
| `accident009_01_aug_02.avi` | `Hand detection rate 69.5% below threshold 80.0%` |
| `accident009_01_aug_03.avi` | `Underexposure (mean luma 32.8 < limit 35.0)` |
| `accident010_01_aug_02.avi` | `Excessive blur (laplacian var 9.5 < limit 15.0)` |
| `accident009_02_aug_02.avi` | `Excessive blur (laplacian var 8.0 < limit 15.0)` |
| `accident010_01_aug_01.avi` | `Hand detection rate 59.4% below threshold 80.0%` |
| `accident010_02_aug_01.avi` | `Hand detection rate 14.5% below threshold 80.0%` |
| `accident010_01_aug_03.avi` | `Hand detection rate 78.3% below threshold 80.0%` |
| `accident010_02_aug_02.avi` | `Hand detection rate 7.2% below threshold 80.0%` |
| `accident009_02_aug_03.avi` | `Hand detection rate 1.1% below threshold 80.0%` |
| `accident010_02_aug_03.avi` | `Hand detection rate 69.6% below threshold 80.0%` |
| `accident011_02_aug_03.avi` | `Hand detection rate 78.4% below threshold 80.0%` |
| `accident011_01_aug_01.avi` | `Hand detection rate 6.4% below threshold 80.0%` |
| `accident012_02_aug_03.avi` | `Excessive blur (laplacian var 4.4 < limit 15.0)` |
| `accident012_02_aug_02.avi` | `Hand detection rate 25.9% below threshold 80.0%` |
| `accident012_01_aug_03.avi` | `Excessive blur (laplacian var 9.5 < limit 15.0)` |
| `accident012_01_aug_01.avi` | `Hand detection rate 7.2% below threshold 80.0%` |
| `accident013_02_aug_01.avi` | `Hand detection rate 78.9% below threshold 80.0%` |
| `accident013_01_aug_02.avi` | `Hand detection rate 78.8% below threshold 80.0%` |
| `accident014_01_aug_01.avi` | `Hand detection rate 36.8% below threshold 80.0%` |
| `accident013_02_aug_03.avi` | `Hand detection rate 71.8% below threshold 80.0%` |
| `accident014_02_aug_01.avi` | `Hand detection rate 18.2% below threshold 80.0%` |
| `accident014_01_aug_03.avi` | `Hand detection rate 51.3% below threshold 80.0%` |
| `accident014_02_aug_03.avi` | `Excessive blur (laplacian var 13.2 < limit 15.0)` |
| `accident015_01_aug_01.avi` | `Excessive blur (laplacian var 8.8 < limit 15.0)` |
| `accident015_01_aug_02.avi` | `Hand detection rate 42.9% below threshold 80.0%` |
| `accident015_02_aug_03.avi` | `Excessive blur (laplacian var 10.7 < limit 15.0)` |
| `accident016_01_aug_01.avi` | `Hand detection rate 35.2% below threshold 80.0%` |
| `accident016_01_aug_02.avi` | `Hand detection rate 14.1% below threshold 80.0%` |
| `accident016_01_aug_03.avi` | `Hand detection rate 46.5% below threshold 80.0%` |
| `accident016_02_aug_02.avi` | `Hand detection rate 71.1% below threshold 80.0%` |
| `accident016_02_aug_03.avi` | `Excessive blur (laplacian var 4.5 < limit 15.0)` |
| `accident016_02_aug_01.avi` | `Hand detection rate 75.0% below threshold 80.0%` |
| `accident017_01_aug_02.avi` | `Excessive blur (laplacian var 8.7 < limit 15.0)` |
| `accident017_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident017_01_aug_03.avi` | `Hand detection rate 7.8% below threshold 80.0%` |
| `accident017_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident017_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident017_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident018_01_aug_02.avi` | `Hand detection rate 67.6% below threshold 80.0%` |
| `accident018_01_aug_01.avi` | `Hand detection rate 11.8% below threshold 80.0%` |
| `accident018_02_aug_02.avi` | `Excessive blur (laplacian var 3.4 < limit 15.0)` |
| `accident018_02_aug_01.avi` | `Hand detection rate 33.9% below threshold 80.0%` |
| `accident018_01_aug_03.avi` | `Hand detection rate 51.5% below threshold 80.0%` |
| `accident018_02_aug_03.avi` | `Hand detection rate 79.7% below threshold 80.0%` |
| `accident019_01_aug_02.avi` | `Excessive blur (laplacian var 10.2 < limit 15.0)` |
| `accident019_01_aug_01.avi` | `Underexposure (mean luma 20.8 < limit 35.0)` |
| `accident020_01_aug_01.avi` | `Excessive blur (laplacian var 12.1 < limit 15.0)` |
| `accident019_02_aug_02.avi` | `Excessive blur (laplacian var 7.3 < limit 15.0)` |
| `accident020_01_aug_03.avi` | `Excessive blur (laplacian var 10.7 < limit 15.0)` |
| `accident020_01_aug_02.avi` | `Hand detection rate 36.2% below threshold 80.0%` |
| `accident019_02_aug_01.avi` | `Hand detection rate 51.2% below threshold 80.0%` |
| `accident020_02_aug_03.avi` | `Excessive blur (laplacian var 5.3 < limit 15.0)` |
| `accident019_02_aug_03.avi` | `Hand detection rate 52.5% below threshold 80.0%` |
| `accident021_01_aug_03.avi` | `Excessive blur (laplacian var 5.3 < limit 15.0)` |
| `accident021_02_aug_02.avi` | `Excessive blur (laplacian var 5.1 < limit 15.0)` |
| `accident021_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident022_01_aug_02.avi` | `Excessive blur (laplacian var 11.8 < limit 15.0)` |
| `accident022_02_aug_02.avi` | `Excessive blur (laplacian var 9.7 < limit 15.0)` |
| `accident022_02_aug_03.avi` | `Hand detection rate 62.5% below threshold 80.0%` |
| `accident023_02_aug_01.avi` | `Excessive blur (laplacian var 4.3 < limit 15.0)` |
| `accident023_01_aug_03.avi` | `Excessive blur (laplacian var 5.5 < limit 15.0)` |
| `accident024_01_aug_01.avi` | `Excessive blur (laplacian var 4.7 < limit 15.0)` |
| `accident025_01_aug_03.avi` | `Excessive blur (laplacian var 7.4 < limit 15.0)` |
| `accident024_02_aug_02.avi` | `Excessive blur (laplacian var 3.3 < limit 15.0)` |
| `accident025_01_aug_01.avi` | `Hand detection rate 38.2% below threshold 80.0%` |
| `accident025_01_aug_02.avi` | `Hand detection rate 47.3% below threshold 80.0%` |
| `accident025_02_aug_02.avi` | `Excessive blur (laplacian var 5.3 < limit 15.0)` |
| `accident026_01_aug_02.avi` | `Excessive blur (laplacian var 4.3 < limit 15.0)` |
| `accident026_02_aug_01.avi` | `Excessive blur (laplacian var 11.5 < limit 15.0)` |
| `accident026_02_aug_02.avi` | `Excessive blur (laplacian var 4.1 < limit 15.0)` |
| `accident026_02_aug_03.avi` | `Hand detection rate 73.8% below threshold 80.0%` |
| `accident_002_02_aug_02.avi` | `Excessive blur (laplacian var 9.6 < limit 15.0)` |
| `accident_001_01_aug_02.avi` | `Hand detection rate 62.9% below threshold 80.0%` |
| `accident_003_01_aug_01.avi` | `Hand detection rate 46.8% below threshold 80.0%` |
| `accident_002_02_aug_01.avi` | `Hand detection rate 76.7% below threshold 80.0%` |
| `accident_005_01_aug_01.avi` | `Excessive blur (laplacian var 9.1 < limit 15.0)` |
| `accident_003_01_aug_02.avi` | `Hand detection rate 29.9% below threshold 80.0%` |
| `accident_004_02_aug_01.avi` | `Excessive blur (laplacian var 11.9 < limit 15.0)` |
| `accident_004_02_aug_03.avi` | `Hand detection rate 56.3% below threshold 80.0%` |
| `accident_005_01_aug_03.avi` | `Excessive blur (laplacian var 10.5 < limit 15.0)` |
| `accident_004_01_aug_01.avi` | `Hand detection rate 18.3% below threshold 80.0%` |
| `accident_004_02_aug_02.avi` | `Hand detection rate 31.0% below threshold 80.0%` |
| `accident_006_01_aug_02.avi` | `Excessive blur (laplacian var 8.0 < limit 15.0)` |
| `accident_006_02_aug_01.avi` | `Excessive blur (laplacian var 9.2 < limit 15.0)` |
| `accident_006_02_aug_02.avi` | `Excessive blur (laplacian var 11.4 < limit 15.0)` |
| `accident_006_02_aug_03.avi` | `Excessive blur (laplacian var 8.7 < limit 15.0)` |
| `accident_008_01_aug_01.avi` | `Excessive blur (laplacian var 5.1 < limit 15.0)` |
| `accident_007_01_aug_03.avi` | `Hand detection rate 69.2% below threshold 80.0%` |
| `accident_007_02_aug_02.avi` | `Hand detection rate 20.6% below threshold 80.0%` |
| `accident_007_02_aug_03.avi` | `Hand detection rate 41.3% below threshold 80.0%` |
| `accident_009_01_aug_02.avi` | `Excessive blur (laplacian var 13.8 < limit 15.0)` |
| `accident_009_02_aug_02.avi` | `Excessive blur (laplacian var 12.9 < limit 15.0)` |
| `accident_009_02_aug_01.avi` | `Excessive blur (laplacian var 13.5 < limit 15.0)` |
| `accident_009_02_aug_03.avi` | `Excessive blur (laplacian var 12.8 < limit 15.0)` |
| `accident_010_01_aug_02.avi` | `Hand detection rate 3.4% below threshold 80.0%` |
| `accident_010_02_aug_01.avi` | `Excessive blur (laplacian var 10.1 < limit 15.0)` |
| `accident_009_01_aug_03.avi` | `Hand detection rate 9.8% below threshold 80.0%` |
| `accident_011_01_aug_03.avi` | `Excessive blur (laplacian var 10.1 < limit 15.0)` |
| `accident_010_03_aug_02.avi` | `Hand detection rate 68.1% below threshold 80.0%` |
| `accident_011_02_aug_02.avi` | `Hand detection rate 56.8% below threshold 80.0%` |
| `accident_011_02_aug_03.avi` | `Excessive blur (laplacian var 10.4 < limit 15.0)` |
| `accident_012_02_aug_03.avi` | `Hand detection rate 40.7% below threshold 80.0%` |
| `accident_012_01_aug_01.avi` | `Excessive blur (laplacian var 6.8 < limit 15.0)` |
| `accident_012_01_aug_02.avi` | `Excessive blur (laplacian var 8.7 < limit 15.0)` |
| `accident_012_01_aug_03.avi` | `Excessive blur (laplacian var 7.5 < limit 15.0)` |
| `accident_014_02_aug_01.avi` | `Excessive blur (laplacian var 14.7 < limit 15.0)` |
| `accident_014_01_aug_03.avi` | `Excessive blur (laplacian var 10.5 < limit 15.0)` |
| `accident_014_02_aug_02.avi` | `Excessive blur (laplacian var 13.0 < limit 15.0)` |
| `accident_013_01_aug_01.avi` | `Hand detection rate 7.5% below threshold 80.0%` |
| `accident_015_01_aug_02.avi` | `Excessive blur (laplacian var 8.7 < limit 15.0)` |
| `accident_016_01_aug_01.avi` | `Excessive blur (laplacian var 5.9 < limit 15.0)` |
| `accident_017_02_aug_03.avi` | `Hand detection rate 75.0% below threshold 80.0%` |
| `accident_014_01_aug_01.avi` | `Hand detection rate 28.9% below threshold 80.0%` |
| `accident_018_02_aug_01.avi` | `Excessive blur (laplacian var 11.2 < limit 15.0)` |
| `accident_017_02_aug_01.avi` | `Hand detection rate 31.2% below threshold 80.0%` |
| `accident_019_01_aug_02.avi` | `Excessive blur (laplacian var 14.6 < limit 15.0)` |
| `accident_019_02_aug_01.avi` | `Hand detection rate 70.0% below threshold 80.0%` |
| `accident_016_02_aug_01.avi` | `Hand detection rate 47.4% below threshold 80.0%` |
| `accident_017_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident_017_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident_020_02_aug_01.avi` | `Excessive blur (laplacian var 13.1 < limit 15.0)` |
| `accident_016_02_aug_02.avi` | `Hand detection rate 61.8% below threshold 80.0%` |
| `accident_017_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `accident_019_02_aug_03.avi` | `Hand detection rate 67.5% below threshold 80.0%` |
| `accident_021_01_aug_01.avi` | `Hand detection rate 73.1% below threshold 80.0%` |
| `accident_019_02_aug_02.avi` | `Hand detection rate 62.5% below threshold 80.0%` |
| `accident_022_01_aug_02.avi` | `Excessive blur (laplacian var 5.7 < limit 15.0)` |
| `accident_022_02_aug_03.avi` | `Excessive blur (laplacian var 4.9 < limit 15.0)` |
| `accident_024_01_aug_01.avi` | `Excessive blur (laplacian var 3.9 < limit 15.0)` |
| `accident_023_02_aug_03.avi` | `Excessive blur (laplacian var 6.2 < limit 15.0)` |
| `accident_024_01_aug_03.avi` | `Excessive blur (laplacian var 14.2 < limit 15.0)` |
| `accident_024_02_aug_01.avi` | `Excessive blur (laplacian var 7.5 < limit 15.0)` |
| `accident_025_02_aug_03.avi` | `Hand detection rate 64.5% below threshold 80.0%` |
| `accident_025_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `call002_01_aug_01.avi` | `Excessive blur (laplacian var 6.2 < limit 15.0)` |
| `call002_01_aug_02.avi` | `Excessive blur (laplacian var 6.2 < limit 15.0)` |
| `call001_02_aug_03.avi` | `Underexposure (mean luma 28.0 < limit 35.0)` |
| `call003_01_aug_01.avi` | `Hand detection rate 18.8% below threshold 80.0%` |
| `call001_01_aug_01.avi` | `Underexposure (mean luma 20.4 < limit 35.0)` |
| `call003_01_aug_02.avi` | `Excessive blur (laplacian var 6.8 < limit 15.0)` |
| `call003_01_aug_03.avi` | `Excessive blur (laplacian var 7.9 < limit 15.0)` |
| `call003_02_aug_01.avi` | `Excessive blur (laplacian var 6.3 < limit 15.0)` |
| `call003_02_aug_02.avi` | `Excessive blur (laplacian var 3.3 < limit 15.0)` |
| `call003_02_aug_03.avi` | `Hand detection rate 42.3% below threshold 80.0%` |
| `call004_01_aug_03.avi` | `Excessive blur (laplacian var 4.3 < limit 15.0)` |
| `call005_01_aug_01.avi` | `Excessive blur (laplacian var 3.3 < limit 15.0)` |
| `call005_01_aug_02.avi` | `Excessive blur (laplacian var 10.7 < limit 15.0)` |
| `call004_02_aug_03.avi` | `Hand detection rate 18.0% below threshold 80.0%` |
| `call005_01_aug_03.avi` | `Excessive blur (laplacian var 8.6 < limit 15.0)` |
| `call005_02_aug_01.avi` | `Hand detection rate 25.4% below threshold 80.0%` |
| `call005_02_aug_02.avi` | `Hand detection rate 26.8% below threshold 80.0%` |
| `call006_01_aug_01.avi` | `Excessive blur (laplacian var 3.4 < limit 15.0)` |
| `call005_02_aug_03.avi` | `Hand detection rate 25.4% below threshold 80.0%` |
| `call006_01_aug_02.avi` | `Excessive blur (laplacian var 9.7 < limit 15.0)` |
| `call006_01_aug_03.avi` | `Excessive blur (laplacian var 8.0 < limit 15.0)` |
| `call006_02_aug_01.avi` | `Excessive blur (laplacian var 3.0 < limit 15.0)` |
| `call007_01_aug_01.avi` | `Excessive blur (laplacian var 7.8 < limit 15.0)` |
| `call006_02_aug_03.avi` | `Hand detection rate 56.5% below threshold 80.0%` |
| `call007_01_aug_03.avi` | `Excessive blur (laplacian var 14.0 < limit 15.0)` |
| `call007_02_aug_01.avi` | `Hand detection rate 31.2% below threshold 80.0%` |
| `call008_02_aug_02.avi` | `Excessive blur (laplacian var 6.8 < limit 15.0)` |
| `call008_02_aug_01.avi` | `Hand detection rate 76.1% below threshold 80.0%` |
| `call009_01_aug_02.avi` | `Hand detection rate 1.1% below threshold 80.0%` |
| `call009_01_aug_03.avi` | `Excessive blur (laplacian var 6.5 < limit 15.0)` |
| `call009_02_aug_01.avi` | `Hand detection rate 24.4% below threshold 80.0%` |
| `call009_02_aug_03.avi` | `Hand detection rate 1.2% below threshold 80.0%` |
| `call010_01_aug_01.avi` | `Excessive blur (laplacian var 5.9 < limit 15.0)` |
| `call010_01_aug_03.avi` | `Hand detection rate 8.6% below threshold 80.0%` |
| `call009_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `call009_02_aug_02.avi` | `Hand detection rate 2.4% below threshold 80.0%` |
| `call010_02_aug_02.avi` | `Excessive blur (laplacian var 10.0 < limit 15.0)` |
| `call010_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `call011_02_aug_01.avi` | `Excessive blur (laplacian var 4.6 < limit 15.0)` |
| `call011_02_aug_02.avi` | `Excessive blur (laplacian var 11.0 < limit 15.0)` |
| `call012_01_aug_01.avi` | `Excessive blur (laplacian var 4.8 < limit 15.0)` |
| `call011_02_aug_03.avi` | `Excessive blur (laplacian var 11.7 < limit 15.0)` |
| `call011_01_aug_02.avi` | `Hand detection rate 2.4% below threshold 80.0%` |
| `call012_02_aug_02.avi` | `Excessive blur (laplacian var 10.7 < limit 15.0)` |
| `call013_01_aug_01.avi` | `Excessive blur (laplacian var 2.9 < limit 15.0)` |
| `call013_01_aug_03.avi` | `Excessive blur (laplacian var 11.3 < limit 15.0)` |
| `call013_02_aug_02.avi` | `Hand detection rate 46.2% below threshold 80.0%` |
| `call013_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `call014_02_aug_02.avi` | `Excessive blur (laplacian var 6.9 < limit 15.0)` |
| `call014_02_aug_03.avi` | `Hand detection rate 51.3% below threshold 80.0%` |
| `call015_01_aug_02.avi` | `Excessive blur (laplacian var 4.2 < limit 15.0)` |
| `call014_01_aug_03.avi` | `Excessive blur (laplacian var 8.0 < limit 15.0)` |
| `call015_02_aug_01.avi` | `Excessive blur (laplacian var 8.7 < limit 15.0)` |
| `call016_01_aug_02.avi` | `Hand detection rate 1.3% below threshold 80.0%` |
| `call015_02_aug_03.avi` | `Excessive blur (laplacian var 11.4 < limit 15.0)` |
| `call016_02_aug_01.avi` | `Excessive blur (laplacian var 6.0 < limit 15.0)` |
| `call016_02_aug_02.avi` | `Excessive blur (laplacian var 12.9 < limit 15.0)` |
| `call016_02_aug_03.avi` | `Excessive blur (laplacian var 10.4 < limit 15.0)` |
| `call017_01_aug_01.avi` | `Hand detection rate 4.2% below threshold 80.0%` |
| `call017_01_aug_02.avi` | `Hand detection rate 29.2% below threshold 80.0%` |
| `call017_02_aug_01.avi` | `Hand detection rate 1.4% below threshold 80.0%` |
| `call017_01_aug_03.avi` | `Excessive blur (laplacian var 4.2 < limit 15.0)` |
| `call017_02_aug_02.avi` | `Hand detection rate 5.7% below threshold 80.0%` |
| `call017_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `call018_01_aug_02.avi` | `Excessive blur (laplacian var 6.1 < limit 15.0)` |
| `call019_01_aug_01.avi` | `Hand detection rate 54.7% below threshold 80.0%` |
| `call019_01_aug_02.avi` | `Hand detection rate 1.3% below threshold 80.0%` |
| `call019_02_aug_03.avi` | `Hand detection rate 29.4% below threshold 80.0%` |
| `call020_01_aug_02.avi` | `Excessive blur (laplacian var 5.8 < limit 15.0)` |
| `call020_01_aug_03.avi` | `Excessive blur (laplacian var 5.6 < limit 15.0)` |
| `call020_02_aug_03.avi` | `Excessive blur (laplacian var 3.5 < limit 15.0)` |
| `call021_01_aug_03.avi` | `Hand detection rate 52.9% below threshold 80.0%` |
| `call021_02_aug_01.avi` | `Excessive blur (laplacian var 7.2 < limit 15.0)` |
| `call021_02_aug_02.avi` | `Excessive blur (laplacian var 8.4 < limit 15.0)` |
| `call022_01_aug_01.avi` | `Excessive blur (laplacian var 3.9 < limit 15.0)` |
| `call022_01_aug_02.avi` | `Excessive blur (laplacian var 8.8 < limit 15.0)` |
| `call022_01_aug_03.avi` | `Hand detection rate 42.9% below threshold 80.0%` |
| `call022_02_aug_02.avi` | `Hand detection rate 56.4% below threshold 80.0%` |
| `call022_02_aug_03.avi` | `Excessive blur (laplacian var 9.7 < limit 15.0)` |
| `call023_01_aug_03.avi` | `Hand detection rate 52.6% below threshold 80.0%` |
| `call023_02_aug_03.avi` | `Excessive blur (laplacian var 14.7 < limit 15.0)` |
| `call024_01_aug_01.avi` | `Hand detection rate 69.1% below threshold 80.0%` |
| `call024_02_aug_02.avi` | `Excessive blur (laplacian var 3.2 < limit 15.0)` |
| `call024_02_aug_01.avi` | `Hand detection rate 42.4% below threshold 80.0%` |
| `call024_02_aug_03.avi` | `Excessive blur (laplacian var 12.4 < limit 15.0)` |
| `call025_01_aug_01.avi` | `Excessive blur (laplacian var 3.4 < limit 15.0)` |
| `call025_01_aug_02.avi` | `Hand detection rate 16.4% below threshold 80.0%` |
| `call025_01_aug_03.avi` | `Hand detection rate 32.7% below threshold 80.0%` |
| `call025_02_aug_02.avi` | `Excessive blur (laplacian var 3.9 < limit 15.0)` |
| `call025_02_aug_03.avi` | `Excessive blur (laplacian var 3.7 < limit 15.0)` |
| `call026_02_aug_01.avi` | `Excessive blur (laplacian var 7.8 < limit 15.0)` |
| `call_001_01_aug_03.avi` | `Hand detection rate 72.7% below threshold 80.0%` |
| `call026_02_aug_03.avi` | `Hand detection rate 58.4% below threshold 80.0%` |
| `call_001_02_aug_02.avi` | `Excessive blur (laplacian var 6.7 < limit 15.0)` |
| `call_002_01_aug_02.avi` | `Excessive blur (laplacian var 5.5 < limit 15.0)` |
| `call_002_01_aug_03.avi` | `Excessive blur (laplacian var 13.1 < limit 15.0)` |
| `call_002_02_aug_02.avi` | `Excessive blur (laplacian var 3.4 < limit 15.0)` |
| `call_002_02_aug_03.avi` | `Excessive blur (laplacian var 7.0 < limit 15.0)` |
| `call_003_02_aug_01.avi` | `Excessive blur (laplacian var 5.4 < limit 15.0)` |
| `call_004_01_aug_02.avi` | `Hand detection rate 65.2% below threshold 80.0%` |
| `call_003_02_aug_02.avi` | `Excessive blur (laplacian var 14.2 < limit 15.0)` |
| `call_004_01_aug_01.avi` | `Excessive blur (laplacian var 8.4 < limit 15.0)` |
| `call_004_01_aug_03.avi` | `Excessive blur (laplacian var 13.8 < limit 15.0)` |
| `call_004_02_aug_01.avi` | `Excessive blur (laplacian var 7.3 < limit 15.0)` |
| `call_004_02_aug_02.avi` | `Excessive blur (laplacian var 6.2 < limit 15.0)` |
| `call_005_02_aug_01.avi` | `Excessive blur (laplacian var 14.5 < limit 15.0)` |
| `call_006_02_aug_02.avi` | `Excessive blur (laplacian var 5.2 < limit 15.0)` |
| `call_006_02_aug_01.avi` | `Excessive blur (laplacian var 11.7 < limit 15.0)` |
| `call_007_01_aug_02.avi` | `Excessive blur (laplacian var 6.8 < limit 15.0)` |
| `call_009_01_aug_01.avi` | `Hand detection rate 30.8% below threshold 80.0%` |
| `call_009_02_aug_01.avi` | `Excessive blur (laplacian var 11.4 < limit 15.0)` |
| `call_010_01_aug_02.avi` | `Excessive blur (laplacian var 10.3 < limit 15.0)` |
| `call_009_02_aug_03.avi` | `Hand detection rate 20.7% below threshold 80.0%` |
| `call_011_01_aug_01.avi` | `Hand detection rate 16.9% below threshold 80.0%` |
| `call_012_01_aug_03.avi` | `Excessive blur (laplacian var 5.1 < limit 15.0)` |
| `call_012_02_aug_02.avi` | `Excessive blur (laplacian var 9.9 < limit 15.0)` |
| `call_013_01_aug_02.avi` | `Excessive blur (laplacian var 11.2 < limit 15.0)` |
| `call_011_02_aug_03.avi` | `Hand detection rate 9.1% below threshold 80.0%` |
| `call_013_02_aug_03.avi` | `Excessive blur (laplacian var 10.9 < limit 15.0)` |
| `call_014_01_aug_01.avi` | `Excessive blur (laplacian var 9.3 < limit 15.0)` |
| `call_011_01_aug_02.avi` | `Hand detection rate 15.7% below threshold 80.0%` |
| `call_012_01_aug_02.avi` | `Hand detection rate 35.4% below threshold 80.0%` |
| `call_014_02_aug_02.avi` | `Excessive blur (laplacian var 9.2 < limit 15.0)` |
| `call_014_02_aug_01.avi` | `Excessive blur (laplacian var 14.5 < limit 15.0)` |
| `call_015_02_aug_03.avi` | `Excessive blur (laplacian var 4.2 < limit 15.0)` |
| `call_016_01_aug_02.avi` | `Excessive blur (laplacian var 8.5 < limit 15.0)` |
| `call_016_02_aug_02.avi` | `Excessive blur (laplacian var 4.9 < limit 15.0)` |
| `call_017_01_aug_02.avi` | `Hand detection rate 15.3% below threshold 80.0%` |
| `call_017_02_aug_01.avi` | `Excessive blur (laplacian var 7.3 < limit 15.0)` |
| `call_017_02_aug_03.avi` | `Hand detection rate 4.3% below threshold 80.0%` |
| `call_013_01_aug_01.avi` | `Hand detection rate 16.0% below threshold 80.0%` |
| `call_015_01_aug_02.avi` | `Hand detection rate 11.3% below threshold 80.0%` |
| `call_018_01_aug_03.avi` | `Excessive blur (laplacian var 8.7 < limit 15.0)` |
| `call_019_01_aug_01.avi` | `Excessive blur (laplacian var 5.5 < limit 15.0)` |
| `call_019_01_aug_02.avi` | `Excessive blur (laplacian var 9.8 < limit 15.0)` |
| `call_017_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `call_017_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `call_019_02_aug_01.avi` | `Excessive blur (laplacian var 10.3 < limit 15.0)` |
| `call_017_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `call_021_01_aug_02.avi` | `Excessive blur (laplacian var 11.7 < limit 15.0)` |
| `call_021_01_aug_03.avi` | `Excessive blur (laplacian var 13.4 < limit 15.0)` |
| `call_021_02_aug_03.avi` | `Hand detection rate 24.7% below threshold 80.0%` |
| `call_023_02_aug_02.avi` | `Excessive blur (laplacian var 7.3 < limit 15.0)` |
| `call_024_02_aug_01.avi` | `Excessive blur (laplacian var 7.1 < limit 15.0)` |
| `call_025_02_aug_03.avi` | `Excessive blur (laplacian var 8.3 < limit 15.0)` |
| `call_026_02_aug_01.avi` | `Excessive blur (laplacian var 14.3 < limit 15.0)` |
| `doctor001_01_aug_02.avi` | `Excessive blur (laplacian var 3.3 < limit 15.0)` |
| `doctor001_02_aug_01.avi` | `Excessive blur (laplacian var 4.3 < limit 15.0)` |
| `doctor001_01_aug_03.avi` | `Hand detection rate 14.3% below threshold 80.0%` |
| `doctor002_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor002_01_aug_01.avi` | `Hand detection rate 9.7% below threshold 80.0%` |
| `doctor001_02_aug_03.avi` | `Hand detection rate 52.9% below threshold 80.0%` |
| `doctor002_02_aug_01.avi` | `Excessive blur (laplacian var 14.6 < limit 15.0)` |
| `doctor003_02_aug_01.avi` | `Excessive blur (laplacian var 4.7 < limit 15.0)` |
| `doctor004_01_aug_01.avi` | `Hand detection rate 1.5% below threshold 80.0%` |
| `doctor003_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor004_01_aug_02.avi` | `Hand detection rate 1.5% below threshold 80.0%` |
| `doctor003_01_aug_01.avi` | `Hand detection rate 72.0% below threshold 80.0%` |
| `doctor003_02_aug_03.avi` | `Underexposure (mean luma 33.0 < limit 35.0)` |
| `doctor004_01_aug_03.avi` | `Hand detection rate 7.4% below threshold 80.0%` |
| `doctor003_01_aug_03.avi` | `Hand detection rate 31.4% below threshold 80.0%` |
| `doctor003_01_aug_02.avi` | `Hand detection rate 4.2% below threshold 80.0%` |
| `doctor004_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor004_02_aug_02.avi` | `Hand detection rate 12.5% below threshold 80.0%` |
| `doctor005_02_aug_01.avi` | `Hand detection rate 26.0% below threshold 80.0%` |
| `doctor004_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor005_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor006_01_aug_01.avi` | `Hand detection rate 5.1% below threshold 80.0%` |
| `doctor006_01_aug_02.avi` | `Hand detection rate 65.8% below threshold 80.0%` |
| `doctor006_01_aug_03.avi` | `Hand detection rate 25.3% below threshold 80.0%` |
| `doctor006_02_aug_03.avi` | `Hand detection rate 15.5% below threshold 80.0%` |
| `doctor007_01_aug_02.avi` | `Hand detection rate 68.9% below threshold 80.0%` |
| `doctor007_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor007_02_aug_02.avi` | `Excessive blur (laplacian var 10.0 < limit 15.0)` |
| `doctor008_02_aug_01.avi` | `Excessive blur (laplacian var 8.7 < limit 15.0)` |
| `doctor007_02_aug_03.avi` | `Excessive blur (laplacian var 11.6 < limit 15.0)` |
| `doctor008_01_aug_01.avi` | `Hand detection rate 72.3% below threshold 80.0%` |
| `doctor008_02_aug_02.avi` | `Excessive blur (laplacian var 11.7 < limit 15.0)` |
| `doctor008_01_aug_03.avi` | `Hand detection rate 0.8% below threshold 80.0%` |
| `doctor009_01_aug_01.avi` | `Excessive blur (laplacian var 2.5 < limit 15.0)` |
| `doctor009_01_aug_02.avi` | `Excessive blur (laplacian var 11.0 < limit 15.0)` |
| `doctor009_01_aug_03.avi` | `Excessive blur (laplacian var 9.0 < limit 15.0)` |
| `doctor009_02_aug_01.avi` | `Excessive blur (laplacian var 12.1 < limit 15.0)` |
| `doctor009_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor010_02_aug_01.avi` | `Excessive blur (laplacian var 14.1 < limit 15.0)` |
| `doctor009_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor010_02_aug_02.avi` | `Excessive blur (laplacian var 7.8 < limit 15.0)` |
| `doctor010_01_aug_01.avi` | `Hand detection rate 25.5% below threshold 80.0%` |
| `doctor010_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor010_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor010_02_aug_03.avi` | `Hand detection rate 7.6% below threshold 80.0%` |
| `doctor011_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor011_01_aug_02.avi` | `Hand detection rate 22.7% below threshold 80.0%` |
| `doctor011_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor012_01_aug_03.avi` | `Hand detection rate 10.5% below threshold 80.0%` |
| `doctor012_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor012_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor011_02_aug_02.avi` | `Hand detection rate 26.4% below threshold 80.0%` |
| `doctor012_02_aug_01.avi` | `Excessive blur (laplacian var 4.3 < limit 15.0)` |
| `doctor012_02_aug_02.avi` | `Excessive blur (laplacian var 11.0 < limit 15.0)` |
| `doctor012_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor013_01_aug_01.avi` | `Excessive blur (laplacian var 7.3 < limit 15.0)` |
| `doctor013_02_aug_02.avi` | `Excessive blur (laplacian var 3.9 < limit 15.0)` |
| `doctor013_01_aug_03.avi` | `Hand detection rate 60.8% below threshold 80.0%` |
| `doctor014_01_aug_01.avi` | `Hand detection rate 7.3% below threshold 80.0%` |
| `doctor014_01_aug_03.avi` | `Hand detection rate 26.4% below threshold 80.0%` |
| `doctor014_02_aug_01.avi` | `Excessive blur (laplacian var 4.1 < limit 15.0)` |
| `doctor014_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor014_02_aug_02.avi` | `Excessive blur (laplacian var 7.6 < limit 15.0)` |
| `doctor014_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor015_01_aug_03.avi` | `Excessive blur (laplacian var 6.2 < limit 15.0)` |
| `doctor015_01_aug_02.avi` | `Hand detection rate 23.7% below threshold 80.0%` |
| `doctor015_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor015_02_aug_01.avi` | `Excessive blur (laplacian var 10.9 < limit 15.0)` |
| `doctor016_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor016_01_aug_01.avi` | `Hand detection rate 20.5% below threshold 80.0%` |
| `doctor016_01_aug_03.avi` | `Excessive blur (laplacian var 9.3 < limit 15.0)` |
| `doctor016_02_aug_02.avi` | `Hand detection rate 55.1% below threshold 80.0%` |
| `doctor017_01_aug_02.avi` | `Excessive blur (laplacian var 8.0 < limit 15.0)` |
| `doctor016_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor016_02_aug_01.avi` | `Hand detection rate 4.5% below threshold 80.0%` |
| `doctor017_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor017_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor017_01_aug_03.avi` | `Underexposure (mean luma 18.1 < limit 35.0)` |
| `doctor017_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor017_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor018_01_aug_03.avi` | `Excessive blur (laplacian var 5.5 < limit 15.0)` |
| `doctor018_01_aug_01.avi` | `Hand detection rate 72.4% below threshold 80.0%` |
| `doctor019_01_aug_01.avi` | `Hand detection rate 74.0% below threshold 80.0%` |
| `doctor019_01_aug_02.avi` | `Excessive blur (laplacian var 6.4 < limit 15.0)` |
| `doctor019_01_aug_03.avi` | `Excessive blur (laplacian var 13.5 < limit 15.0)` |
| `doctor020_01_aug_01.avi` | `Hand detection rate 1.4% below threshold 80.0%` |
| `doctor020_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor020_01_aug_03.avi` | `Excessive blur (laplacian var 4.4 < limit 15.0)` |
| `doctor021_01_aug_01.avi` | `Hand detection rate 57.6% below threshold 80.0%` |
| `doctor020_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor020_02_aug_03.avi` | `Hand detection rate 35.7% below threshold 80.0%` |
| `doctor021_02_aug_01.avi` | `Excessive blur (laplacian var 13.8 < limit 15.0)` |
| `doctor021_02_aug_02.avi` | `Excessive blur (laplacian var 11.9 < limit 15.0)` |
| `doctor022_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor022_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor022_02_aug_02.avi` | `Hand detection rate 2.2% below threshold 80.0%` |
| `doctor022_01_aug_02.avi` | `Hand detection rate 2.6% below threshold 80.0%` |
| `doctor023_01_aug_01.avi` | `Excessive blur (laplacian var 13.0 < limit 15.0)` |
| `doctor022_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor023_01_aug_03.avi` | `Hand detection rate 73.0% below threshold 80.0%` |
| `doctor022_01_aug_03.avi` | `Hand detection rate 2.6% below threshold 80.0%` |
| `doctor023_01_aug_02.avi` | `Hand detection rate 2.2% below threshold 80.0%` |
| `doctor023_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor023_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor023_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor024_01_aug_01.avi` | `Excessive blur (laplacian var 13.2 < limit 15.0)` |
| `doctor024_02_aug_02.avi` | `Excessive blur (laplacian var 6.5 < limit 15.0)` |
| `doctor025_01_aug_01.avi` | `Excessive blur (laplacian var 9.1 < limit 15.0)` |
| `doctor025_01_aug_02.avi` | `Excessive blur (laplacian var 8.9 < limit 15.0)` |
| `doctor025_01_aug_03.avi` | `Excessive blur (laplacian var 4.6 < limit 15.0)` |
| `doctor025_02_aug_03.avi` | `Hand detection rate 10.2% below threshold 80.0%` |
| `doctor026_02_aug_01.avi` | `Excessive blur (laplacian var 14.9 < limit 15.0)` |
| `doctor026_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor026_01_aug_02.avi` | `Excessive blur (laplacian var 11.2 < limit 15.0)` |
| `doctor026_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor026_01_aug_03.avi` | `Hand detection rate 2.1% below threshold 80.0%` |
| `doctor026_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor_001_01_aug_03.avi` | `Excessive blur (laplacian var 6.3 < limit 15.0)` |
| `doctor_002_01_aug_01.avi` | `Excessive blur (laplacian var 10.5 < limit 15.0)` |
| `doctor_002_01_aug_03.avi` | `Excessive blur (laplacian var 6.5 < limit 15.0)` |
| `doctor_001_02_aug_03.avi` | `Excessive blur (laplacian var 8.6 < limit 15.0)` |
| `doctor_003_02_aug_02.avi` | `Excessive blur (laplacian var 14.0 < limit 15.0)` |
| `doctor_004_02_aug_02.avi` | `Excessive blur (laplacian var 7.8 < limit 15.0)` |
| `doctor_003_01_aug_01.avi` | `Hand detection rate 63.6% below threshold 80.0%` |
| `doctor_006_02_aug_02.avi` | `Excessive blur (laplacian var 12.2 < limit 15.0)` |
| `doctor_009_02_aug_01.avi` | `Excessive blur (laplacian var 13.1 < limit 15.0)` |
| `doctor_003_01_aug_03.avi` | `Hand detection rate 10.2% below threshold 80.0%` |
| `doctor_007_01_aug_01.avi` | `Hand detection rate 19.8% below threshold 80.0%` |
| `doctor_007_01_aug_02.avi` | `Hand detection rate 22.6% below threshold 80.0%` |
| `doctor_010_01_aug_03.avi` | `Excessive blur (laplacian var 4.2 < limit 15.0)` |
| `doctor_010_02_aug_02.avi` | `Excessive blur (laplacian var 6.8 < limit 15.0)` |
| `doctor_007_02_aug_02.avi` | `Hand detection rate 25.0% below threshold 80.0%` |
| `doctor_011_01_aug_01.avi` | `Hand detection rate 77.3% below threshold 80.0%` |
| `doctor_009_01_aug_02.avi` | `Hand detection rate 47.8% below threshold 80.0%` |
| `doctor_009_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor_007_01_aug_03.avi` | `Hand detection rate 67.9% below threshold 80.0%` |
| `doctor_007_02_aug_03.avi` | `Hand detection rate 34.1% below threshold 80.0%` |
| `doctor_011_01_aug_02.avi` | `Hand detection rate 1.0% below threshold 80.0%` |
| `doctor_012_002_aug_03.avi` | `Excessive blur (laplacian var 10.8 < limit 15.0)` |
| `doctor_013_01_aug_01.avi` | `Excessive blur (laplacian var 14.5 < limit 15.0)` |
| `doctor_013_02_aug_02.avi` | `Excessive blur (laplacian var 8.0 < limit 15.0)` |
| `doctor_014_01_aug_03.avi` | `Excessive blur (laplacian var 9.0 < limit 15.0)` |
| `doctor_013_02_aug_01.avi` | `Hand detection rate 30.5% below threshold 80.0%` |
| `doctor_014_02_aug_02.avi` | `Hand detection rate 10.1% below threshold 80.0%` |
| `doctor_014_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor_014_02_aug_01.avi` | `Hand detection rate 39.3% below threshold 80.0%` |
| `doctor_016_02_aug_03.avi` | `Excessive blur (laplacian var 9.6 < limit 15.0)` |
| `doctor_017_01_aug_02.avi` | `Excessive blur (laplacian var 8.8 < limit 15.0)` |
| `doctor_017_01_aug_03.avi` | `Hand detection rate 16.2% below threshold 80.0%` |
| `doctor_018_02_aug_01.avi` | `Excessive blur (laplacian var 10.5 < limit 15.0)` |
| `doctor_018_02_aug_03.avi` | `Excessive blur (laplacian var 9.5 < limit 15.0)` |
| `doctor_017_01_aug_01.avi` | `Hand detection rate 62.5% below threshold 80.0%` |
| `doctor_017_02_aug_01.avi` | `Hand detection rate 65.3% below threshold 80.0%` |
| `doctor_020_01_aug_02.avi` | `Excessive blur (laplacian var 11.1 < limit 15.0)` |
| `doctor_017_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `doctor_018_01_aug_02.avi` | `Hand detection rate 4.6% below threshold 80.0%` |
| `doctor_019_01_aug_02.avi` | `Hand detection rate 75.0% below threshold 80.0%` |
| `doctor_020_02_aug_03.avi` | `Excessive blur (laplacian var 5.3 < limit 15.0)` |
| `doctor_021_02_aug_02.avi` | `Excessive blur (laplacian var 10.3 < limit 15.0)` |
| `doctor_022_02_aug_02.avi` | `Excessive blur (laplacian var 11.8 < limit 15.0)` |
| `doctor_022_01_aug_01.avi` | `Excessive blur (laplacian var 6.4 < limit 15.0)` |
| `doctor_023_01_aug_01.avi` | `Excessive blur (laplacian var 7.4 < limit 15.0)` |
| `doctor_021_02_aug_03.avi` | `Hand detection rate 77.6% below threshold 80.0%` |
| `doctor_022_01_aug_03.avi` | `Hand detection rate 57.8% below threshold 80.0%` |
| `doctor_025_02_aug_02.avi` | `Excessive blur (laplacian var 7.3 < limit 15.0)` |
| `help001_01_aug_03.avi` | `Excessive blur (laplacian var 4.0 < limit 15.0)` |
| `help002_01_aug_01.avi` | `Hand detection rate 27.3% below threshold 80.0%` |
| `help003_01_aug_01.avi` | `Excessive blur (laplacian var 8.2 < limit 15.0)` |
| `help001_02_aug_01.avi` | `Hand detection rate 16.9% below threshold 80.0%` |
| `help002_02_aug_02.avi` | `Hand detection rate 1.4% below threshold 80.0%` |
| `help001_02_aug_02.avi` | `Hand detection rate 9.0% below threshold 80.0%` |
| `help003_02_aug_02.avi` | `Excessive blur (laplacian var 11.0 < limit 15.0)` |
| `help002_02_aug_01.avi` | `Hand detection rate 12.7% below threshold 80.0%` |
| `help003_02_aug_01.avi` | `Hand detection rate 12.8% below threshold 80.0%` |
| `help002_02_aug_03.avi` | `Hand detection rate 7.0% below threshold 80.0%` |
| `help003_02_aug_03.avi` | `Excessive blur (laplacian var 4.3 < limit 15.0)` |
| `help003_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help003_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help004_01_aug_01.avi` | `Excessive blur (laplacian var 6.0 < limit 15.0)` |
| `help004_01_aug_03.avi` | `Hand detection rate 5.3% below threshold 80.0%` |
| `help004_01_aug_02.avi` | `Excessive blur (laplacian var 14.0 < limit 15.0)` |
| `help004_02_aug_01.avi` | `Excessive blur (laplacian var 9.6 < limit 15.0)` |
| `help004_02_aug_02.avi` | `Excessive blur (laplacian var 13.7 < limit 15.0)` |
| `help004_02_aug_03.avi` | `Excessive blur (laplacian var 5.1 < limit 15.0)` |
| `help005_01_aug_03.avi` | `Excessive blur (laplacian var 12.4 < limit 15.0)` |
| `help005_01_aug_01.avi` | `Hand detection rate 2.9% below threshold 80.0%` |
| `help005_01_aug_02.avi` | `Hand detection rate 5.7% below threshold 80.0%` |
| `help005_02_aug_01.avi` | `Hand detection rate 14.9% below threshold 80.0%` |
| `help005_02_aug_02.avi` | `Hand detection rate 5.4% below threshold 80.0%` |
| `help006_01_aug_01.avi` | `Hand detection rate 68.3% below threshold 80.0%` |
| `help005_02_aug_03.avi` | `Hand detection rate 13.5% below threshold 80.0%` |
| `help006_01_aug_03.avi` | `Hand detection rate 4.9% below threshold 80.0%` |
| `help006_02_aug_03.avi` | `Hand detection rate 1.3% below threshold 80.0%` |
| `help006_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help007_01_aug_03.avi` | `Hand detection rate 2.6% below threshold 80.0%` |
| `help007_02_aug_02.avi` | `Excessive blur (laplacian var 3.3 < limit 15.0)` |
| `help007_02_aug_03.avi` | `Hand detection rate 46.1% below threshold 80.0%` |
| `help008_01_aug_01.avi` | `Hand detection rate 3.7% below threshold 80.0%` |
| `help008_01_aug_02.avi` | `Excessive blur (laplacian var 12.0 < limit 15.0)` |
| `help008_02_aug_02.avi` | `Excessive blur (laplacian var 14.2 < limit 15.0)` |
| `help008_02_aug_03.avi` | `Hand detection rate 25.3% below threshold 80.0%` |
| `help009_01_aug_01.avi` | `Excessive blur (laplacian var 6.0 < limit 15.0)` |
| `help008_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help009_01_aug_03.avi` | `Hand detection rate 4.9% below threshold 80.0%` |
| `help009_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help009_02_aug_01.avi` | `Hand detection rate 30.9% below threshold 80.0%` |
| `help009_02_aug_02.avi` | `Excessive blur (laplacian var 5.5 < limit 15.0)` |
| `help009_02_aug_03.avi` | `Hand detection rate 33.3% below threshold 80.0%` |
| `help010_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help010_01_aug_02.avi` | `Hand detection rate 2.8% below threshold 80.0%` |
| `help010_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help010_02_aug_02.avi` | `Hand detection rate 40.5% below threshold 80.0%` |
| `help010_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help010_02_aug_03.avi` | `Hand detection rate 45.6% below threshold 80.0%` |
| `help011_01_aug_01.avi` | `Hand detection rate 22.2% below threshold 80.0%` |
| `help011_01_aug_02.avi` | `Hand detection rate 3.7% below threshold 80.0%` |
| `help011_02_aug_02.avi` | `Hand detection rate 47.1% below threshold 80.0%` |
| `help011_01_aug_03.avi` | `Hand detection rate 30.9% below threshold 80.0%` |
| `help011_02_aug_01.avi` | `Hand detection rate 3.5% below threshold 80.0%` |
| `help012_01_aug_01.avi` | `Hand detection rate 4.9% below threshold 80.0%` |
| `help012_01_aug_02.avi` | `Excessive blur (laplacian var 10.8 < limit 15.0)` |
| `help012_02_aug_01.avi` | `Excessive blur (laplacian var 5.5 < limit 15.0)` |
| `help012_01_aug_03.avi` | `Hand detection rate 6.2% below threshold 80.0%` |
| `help012_02_aug_02.avi` | `Excessive blur (laplacian var 12.5 < limit 15.0)` |
| `help012_02_aug_03.avi` | `Excessive blur (laplacian var 8.6 < limit 15.0)` |
| `help013_01_aug_02.avi` | `Hand detection rate 28.9% below threshold 80.0%` |
| `help013_01_aug_03.avi` | `Excessive blur (laplacian var 14.2 < limit 15.0)` |
| `help013_02_aug_01.avi` | `Hand detection rate 1.0% below threshold 80.0%` |
| `help014_01_aug_02.avi` | `Excessive blur (laplacian var 13.1 < limit 15.0)` |
| `help014_01_aug_01.avi` | `Hand detection rate 15.9% below threshold 80.0%` |
| `help014_02_aug_02.avi` | `Hand detection rate 44.6% below threshold 80.0%` |
| `help014_02_aug_03.avi` | `Hand detection rate 63.5% below threshold 80.0%` |
| `help015_01_aug_01.avi` | `Hand detection rate 6.0% below threshold 80.0%` |
| `help015_02_aug_03.avi` | `Excessive blur (laplacian var 4.2 < limit 15.0)` |
| `help015_01_aug_02.avi` | `Excessive blur (laplacian var 7.3 < limit 15.0)` |
| `help015_02_aug_01.avi` | `Hand detection rate 51.4% below threshold 80.0%` |
| `help015_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help016_01_aug_02.avi` | `Excessive blur (laplacian var 3.7 < limit 15.0)` |
| `help016_01_aug_01.avi` | `Hand detection rate 18.4% below threshold 80.0%` |
| `help016_02_aug_02.avi` | `Hand detection rate 48.5% below threshold 80.0%` |
| `help016_01_aug_03.avi` | `Hand detection rate 1.1% below threshold 80.0%` |
| `help016_02_aug_01.avi` | `Hand detection rate 7.4% below threshold 80.0%` |
| `help016_02_aug_03.avi` | `Excessive blur (laplacian var 4.5 < limit 15.0)` |
| `help017_02_aug_01.avi` | `Hand detection rate 4.6% below threshold 80.0%` |
| `help017_01_aug_01.avi` | `Hand detection rate 38.7% below threshold 80.0%` |
| `help017_01_aug_02.avi` | `Hand detection rate 37.3% below threshold 80.0%` |
| `help017_01_aug_03.avi` | `Hand detection rate 44.0% below threshold 80.0%` |
| `help017_02_aug_02.avi` | `Hand detection rate 3.1% below threshold 80.0%` |
| `help017_02_aug_03.avi` | `Hand detection rate 12.3% below threshold 80.0%` |
| `help018_01_aug_02.avi` | `Excessive blur (laplacian var 5.0 < limit 15.0)` |
| `help018_01_aug_03.avi` | `Excessive blur (laplacian var 3.4 < limit 15.0)` |
| `help019_01_aug_01.avi` | `Hand detection rate 1.3% below threshold 80.0%` |
| `help018_02_aug_01.avi` | `Hand detection rate 11.5% below threshold 80.0%` |
| `help019_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help018_02_aug_02.avi` | `Hand detection rate 78.2% below threshold 80.0%` |
| `help019_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help019_01_aug_03.avi` | `Hand detection rate 33.3% below threshold 80.0%` |
| `help019_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help018_02_aug_03.avi` | `Hand detection rate 34.6% below threshold 80.0%` |
| `help019_02_aug_03.avi` | `Hand detection rate 4.2% below threshold 80.0%` |
| `help021_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help021_02_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help020_02_aug_02.avi` | `Hand detection rate 78.3% below threshold 80.0%` |
| `help020_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help020_02_aug_03.avi` | `Hand detection rate 16.9% below threshold 80.0%` |
| `help021_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help021_02_aug_03.avi` | `Hand detection rate 42.2% below threshold 80.0%` |
| `help021_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help021_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help020_01_aug_03.avi` | `Hand detection rate 2.4% below threshold 80.0%` |
| `help022_01_aug_03.avi` | `Hand detection rate 3.8% below threshold 80.0%` |
| `help022_01_aug_02.avi` | `Hand detection rate 24.4% below threshold 80.0%` |
| `help022_02_aug_02.avi` | `Excessive blur (laplacian var 9.9 < limit 15.0)` |
| `help022_02_aug_01.avi` | `Hand detection rate 30.7% below threshold 80.0%` |
| `help023_01_aug_01.avi` | `Hand detection rate 36.7% below threshold 80.0%` |
| `help023_01_aug_03.avi` | `Excessive blur (laplacian var 10.1 < limit 15.0)` |
| `help022_02_aug_03.avi` | `Hand detection rate 6.7% below threshold 80.0%` |
| `help023_02_aug_01.avi` | `Excessive blur (laplacian var 11.8 < limit 15.0)` |
| `help023_02_aug_02.avi` | `Excessive blur (laplacian var 7.1 < limit 15.0)` |
| `help024_01_aug_01.avi` | `Hand detection rate 17.1% below threshold 80.0%` |
| `help024_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help024_01_aug_02.avi` | `Hand detection rate 19.7% below threshold 80.0%` |
| `help023_02_aug_03.avi` | `Hand detection rate 22.9% below threshold 80.0%` |
| `help024_02_aug_03.avi` | `Hand detection rate 52.2% below threshold 80.0%` |
| `help025_01_aug_01.avi` | `Excessive blur (laplacian var 12.3 < limit 15.0)` |
| `help025_01_aug_02.avi` | `Hand detection rate 50.0% below threshold 80.0%` |
| `help025_01_aug_03.avi` | `Excessive blur (laplacian var 6.4 < limit 15.0)` |
| `help024_01_aug_03.avi` | `Hand detection rate 7.9% below threshold 80.0%` |
| `help025_02_aug_02.avi` | `Excessive blur (laplacian var 6.1 < limit 15.0)` |
| `help025_02_aug_03.avi` | `Excessive blur (laplacian var 12.4 < limit 15.0)` |
| `help026_01_aug_01.avi` | `Hand detection rate 4.2% below threshold 80.0%` |
| `help026_02_aug_03.avi` | `Hand detection rate 49.4% below threshold 80.0%` |
| `help_001_01_aug_03.avi` | `Excessive blur (laplacian var 10.5 < limit 15.0)` |
| `help026_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help026_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help026_01_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help_001_02_aug_03.avi` | `Excessive blur (laplacian var 8.4 < limit 15.0)` |
| `help_002_02_aug_01.avi` | `Excessive blur (laplacian var 10.4 < limit 15.0)` |
| `help_003_01_aug_02.avi` | `Hand detection rate 72.4% below threshold 80.0%` |
| `help_003_02_aug_03.avi` | `Hand detection rate 73.1% below threshold 80.0%` |
| `help_004_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help_004_02_aug_03.avi` | `Hand detection rate 49.1% below threshold 80.0%` |
| `help_004_01_aug_01.avi` | `Excessive blur (laplacian var 13.7 < limit 15.0)` |
| `help_005_01_aug_02.avi` | `Excessive blur (laplacian var 10.5 < limit 15.0)` |
| `help_005_01_aug_01.avi` | `Hand detection rate 38.7% below threshold 80.0%` |
| `help_005_02_aug_02.avi` | `Excessive blur (laplacian var 6.1 < limit 15.0)` |
| `help_005_02_aug_03.avi` | `Excessive blur (laplacian var 9.3 < limit 15.0)` |
| `help_006_01_aug_03.avi` | `Excessive blur (laplacian var 9.7 < limit 15.0)` |
| `help_006_01_aug_02.avi` | `Excessive blur (laplacian var 12.0 < limit 15.0)` |
| `help_006_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help_008_02_aug_01.avi` | `Excessive blur (laplacian var 4.7 < limit 15.0)` |
| `help_007_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help_009_01_aug_02.avi` | `Hand detection rate 32.1% below threshold 80.0%` |
| `help_009_01_aug_01.avi` | `Excessive blur (laplacian var 7.0 < limit 15.0)` |
| `help_007_02_aug_03.avi` | `Hand detection rate 3.9% below threshold 80.0%` |
| `help_009_02_aug_02.avi` | `Hand detection rate 25.9% below threshold 80.0%` |
| `help_009_02_aug_01.avi` | `Hand detection rate 79.0% below threshold 80.0%` |
| `help_009_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help_010_01_aug_03.avi` | `Excessive blur (laplacian var 12.0 < limit 15.0)` |
| `help_011_01_aug_02.avi` | `Hand detection rate 56.8% below threshold 80.0%` |
| `help_011_02_aug_01.avi` | `Hand detection rate 15.3% below threshold 80.0%` |
| `help_011_02_aug_02.avi` | `Excessive blur (laplacian var 14.6 < limit 15.0)` |
| `help_012_01_aug_02.avi` | `Hand detection rate 42.0% below threshold 80.0%` |
| `help_010_01_aug_02.avi` | `Hand detection rate 1.4% below threshold 80.0%` |
| `help_012_02_aug_01.avi` | `Excessive blur (laplacian var 11.8 < limit 15.0)` |
| `help_013_01_aug_02.avi` | `Hand detection rate 77.6% below threshold 80.0%` |
| `help_010_02_aug_01.avi` | `Hand detection rate 3.8% below threshold 80.0%` |
| `help_014_01_aug_03.avi` | `Excessive blur (laplacian var 4.4 < limit 15.0)` |
| `help_012_02_aug_02.avi` | `Hand detection rate 2.5% below threshold 80.0%` |
| `help_013_01_aug_01.avi` | `Hand detection rate 31.6% below threshold 80.0%` |
| `help_015_01_aug_01.avi` | `Hand detection rate 79.5% below threshold 80.0%` |
| `help_012_01_aug_03.avi` | `Hand detection rate 9.9% below threshold 80.0%` |
| `help_016_01_aug_01.avi` | `Excessive blur (laplacian var 14.9 < limit 15.0)` |
| `help_014_01_aug_02.avi` | `Hand detection rate 58.0% below threshold 80.0%` |
| `help_014_02_aug_02.avi` | `Hand detection rate 24.3% below threshold 80.0%` |
| `help_016_02_aug_02.avi` | `Excessive blur (laplacian var 14.8 < limit 15.0)` |
| `help_017_01_aug_02.avi` | `Hand detection rate 5.3% below threshold 80.0%` |
| `help_017_01_aug_01.avi` | `Hand detection rate 9.3% below threshold 80.0%` |
| `help_017_02_aug_03.avi` | `Hand detection rate 70.8% below threshold 80.0%` |
| `help_018_01_aug_02.avi` | `Excessive blur (laplacian var 14.4 < limit 15.0)` |
| `help_016_02_aug_03.avi` | `Hand detection rate 79.4% below threshold 80.0%` |
| `help_017_02_aug_01.avi` | `Hand detection rate 58.5% below threshold 80.0%` |
| `help_017_02_aug_02.avi` | `Hand detection rate 18.5% below threshold 80.0%` |
| `help_016_02_aug_01.avi` | `Hand detection rate 7.4% below threshold 80.0%` |
| `help_016_01_aug_03.avi` | `Hand detection rate 43.7% below threshold 80.0%` |
| `help_018_02_aug_03.avi` | `Excessive blur (laplacian var 5.8 < limit 15.0)` |
| `help_017_01_aug_03.avi` | `Hand detection rate 1.3% below threshold 80.0%` |
| `help_019_01_aug_02.avi` | `Excessive blur (laplacian var 13.0 < limit 15.0)` |
| `help_019_02_aug_01.avi` | `Excessive blur (laplacian var 7.0 < limit 15.0)` |
| `help_019_02_aug_03.avi` | `Hand detection rate 63.9% below threshold 80.0%` |
| `help_019_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help_020_01_aug_02.avi` | `Excessive blur (laplacian var 9.6 < limit 15.0)` |
| `help_019_02_aug_02.avi` | `Hand detection rate 66.7% below threshold 80.0%` |
| `help_021_01_aug_01.avi` | `Excessive blur (laplacian var 7.2 < limit 15.0)` |
| `help_021_01_aug_03.avi` | `Excessive blur (laplacian var 14.4 < limit 15.0)` |
| `help_021_02_aug_03.avi` | `Hand detection rate 27.7% below threshold 80.0%` |
| `help_021_02_aug_02.avi` | `Hand detection rate 57.8% below threshold 80.0%` |
| `help_022_01_aug_02.avi` | `Excessive blur (laplacian var 4.4 < limit 15.0)` |
| `help_022_02_aug_02.avi` | `Excessive blur (laplacian var 13.5 < limit 15.0)` |
| `help_021_01_aug_02.avi` | `Hand detection rate 33.7% below threshold 80.0%` |
| `help_022_02_aug_03.avi` | `Excessive blur (laplacian var 13.3 < limit 15.0)` |
| `help_022_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help_023_01_aug_02.avi` | `Excessive blur (laplacian var 8.1 < limit 15.0)` |
| `help_022_01_aug_03.avi` | `Hand detection rate 11.5% below threshold 80.0%` |
| `help_023_01_aug_03.avi` | `Excessive blur (laplacian var 5.2 < limit 15.0)` |
| `help_023_02_aug_01.avi` | `Hand detection rate 53.0% below threshold 80.0%` |
| `help_023_02_aug_02.avi` | `Hand detection rate 77.1% below threshold 80.0%` |
| `help_021_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `help_024_02_aug_02.avi` | `Excessive blur (laplacian var 11.2 < limit 15.0)` |
| `help_023_01_aug_01.avi` | `Hand detection rate 12.7% below threshold 80.0%` |
| `help_024_01_aug_02.avi` | `Hand detection rate 67.1% below threshold 80.0%` |
| `help_024_02_aug_03.avi` | `Hand detection rate 34.3% below threshold 80.0%` |
| `help_025_02_aug_01.avi` | `Hand detection rate 59.0% below threshold 80.0%` |
| `help_025_02_aug_03.avi` | `Excessive blur (laplacian var 6.4 < limit 15.0)` |
| `help_026_02_aug_03.avi` | `Excessive blur (laplacian var 14.5 < limit 15.0)` |
| `hot001_02_aug_01.avi` | `Hand detection rate 72.6% below threshold 80.0%` |
| `help_026_02_aug_02.avi` | `Hand detection rate 8.2% below threshold 80.0%` |
| `help_026_01_aug_02.avi` | `Hand detection rate 4.2% below threshold 80.0%` |
| `hot002_01_aug_01.avi` | `Excessive blur (laplacian var 2.9 < limit 15.0)` |
| `hot002_01_aug_03.avi` | `Excessive blur (laplacian var 8.4 < limit 15.0)` |
| `hot002_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `hot002_02_aug_02.avi` | `Excessive blur (laplacian var 11.2 < limit 15.0)` |
| `hot002_02_aug_03.avi` | `Excessive blur (laplacian var 10.2 < limit 15.0)` |
| `hot003_02_aug_01.avi` | `Excessive blur (laplacian var 6.9 < limit 15.0)` |
| `hot003_02_aug_02.avi` | `Excessive blur (laplacian var 10.6 < limit 15.0)` |
| `hot003_01_aug_02.avi` | `Hand detection rate 54.4% below threshold 80.0%` |
| `hot003_02_aug_03.avi` | `Hand detection rate 69.7% below threshold 80.0%` |
| `hot004_01_aug_03.avi` | `Excessive blur (laplacian var 4.6 < limit 15.0)` |
| `hot004_02_aug_01.avi` | `Excessive blur (laplacian var 9.3 < limit 15.0)` |
| `hot005_01_aug_01.avi` | `Excessive blur (laplacian var 4.0 < limit 15.0)` |
| `hot005_01_aug_02.avi` | `Hand detection rate 73.4% below threshold 80.0%` |
| `hot005_01_aug_03.avi` | `Excessive blur (laplacian var 8.5 < limit 15.0)` |
| `hot005_02_aug_02.avi` | `Excessive blur (laplacian var 13.5 < limit 15.0)` |
| `hot005_02_aug_03.avi` | `Hand detection rate 64.2% below threshold 80.0%` |
| `hot006_01_aug_02.avi` | `Excessive blur (laplacian var 5.4 < limit 15.0)` |
| `hot007_01_aug_01.avi` | `Hand detection rate 40.5% below threshold 80.0%` |
| `hot007_01_aug_03.avi` | `Excessive blur (laplacian var 2.5 < limit 15.0)` |
| `hot007_01_aug_02.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `hot007_02_aug_01.avi` | `Hand detection rate 54.5% below threshold 80.0%` |
| `hot008_01_aug_01.avi` | `Excessive blur (laplacian var 4.4 < limit 15.0)` |
| `hot008_01_aug_03.avi` | `Excessive blur (laplacian var 4.9 < limit 15.0)` |
| `hot008_02_aug_02.avi` | `Underexposure (mean luma 32.7 < limit 35.0)` |
| `hot009_01_aug_02.avi` | `Hand detection rate 9.9% below threshold 80.0%` |
| `hot009_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `hot010_01_aug_02.avi` | `Excessive blur (laplacian var 8.1 < limit 15.0)` |
| `hot009_02_aug_03.avi` | `Hand detection rate 79.1% below threshold 80.0%` |
| `hot010_02_aug_02.avi` | `Excessive blur (laplacian var 4.6 < limit 15.0)` |
| `hot011_01_aug_01.avi` | `Excessive blur (laplacian var 8.6 < limit 15.0)` |
| `hot011_01_aug_03.avi` | `Excessive blur (laplacian var 3.1 < limit 15.0)` |
| `hot011_02_aug_01.avi` | `Excessive blur (laplacian var 7.0 < limit 15.0)` |
| `hot010_02_aug_03.avi` | `Hand detection rate 32.4% below threshold 80.0%` |
| `hot012_02_aug_02.avi` | `Excessive blur (laplacian var 4.7 < limit 15.0)` |
| `hot012_02_aug_03.avi` | `Excessive blur (laplacian var 5.7 < limit 15.0)` |
| `hot012_02_aug_01.avi` | `Hand detection rate 75.6% below threshold 80.0%` |
| `hot013_01_aug_01.avi` | `Excessive blur (laplacian var 10.4 < limit 15.0)` |
| `hot013_02_aug_01.avi` | `Hand detection rate 42.4% below threshold 80.0%` |
| `hot013_02_aug_02.avi` | `Hand detection rate 45.9% below threshold 80.0%` |
| `hot014_01_aug_01.avi` | `Hand detection rate 54.1% below threshold 80.0%` |
| `hot014_01_aug_02.avi` | `Hand detection rate 58.1% below threshold 80.0%` |
| `hot014_01_aug_03.avi` | `Hand detection rate 4.1% below threshold 80.0%` |
| `hot014_02_aug_03.avi` | `Hand detection rate 41.4% below threshold 80.0%` |
| `hot014_02_aug_02.avi` | `Hand detection rate 74.3% below threshold 80.0%` |
| `hot015_01_aug_01.avi` | `Excessive blur (laplacian var 4.7 < limit 15.0)` |
| `hot015_01_aug_02.avi` | `Excessive blur (laplacian var 3.7 < limit 15.0)` |
| `hot015_01_aug_03.avi` | `Excessive blur (laplacian var 8.8 < limit 15.0)` |
| `hot015_02_aug_02.avi` | `Excessive blur (laplacian var 3.6 < limit 15.0)` |
| `hot016_01_aug_02.avi` | `Hand detection rate 61.8% below threshold 80.0%` |
| `hot016_01_aug_01.avi` | `Excessive blur (laplacian var 6.5 < limit 15.0)` |
| `hot016_01_aug_03.avi` | `Hand detection rate 76.3% below threshold 80.0%` |
| `hot016_02_aug_02.avi` | `Excessive blur (laplacian var 4.6 < limit 15.0)` |
| `hot016_02_aug_01.avi` | `Hand detection rate 68.4% below threshold 80.0%` |
| `hot016_02_aug_03.avi` | `Hand detection rate 70.9% below threshold 80.0%` |
| `hot017_01_aug_02.avi` | `Excessive blur (laplacian var 12.6 < limit 15.0)` |
| `hot017_01_aug_03.avi` | `Hand detection rate 5.3% below threshold 80.0%` |
| `hot017_01_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `hot017_02_aug_03.avi` | `Hand detection rate 21.1% below threshold 80.0%` |
| `hot017_02_aug_02.avi` | `Hand detection rate 21.1% below threshold 80.0%` |
| `hot017_02_aug_01.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `hot018_01_aug_01.avi` | `Hand detection rate 37.0% below threshold 80.0%` |
| `hot018_01_aug_02.avi` | `Hand detection rate 38.3% below threshold 80.0%` |
| `hot019_01_aug_01.avi` | `Hand detection rate 26.4% below threshold 80.0%` |
| `hot018_02_aug_03.avi` | `Hand detection rate 45.0% below threshold 80.0%` |
| `hot019_01_aug_03.avi` | `Hand detection rate 65.9% below threshold 80.0%` |
| `hot019_02_aug_02.avi` | `Hand detection rate 63.4% below threshold 80.0%` |
| `hot019_02_aug_03.avi` | `Excessive blur (laplacian var 3.2 < limit 15.0)` |
| `hot020_01_aug_03.avi` | `Excessive blur (laplacian var 5.8 < limit 15.0)` |
| `hot020_02_aug_02.avi` | `Hand detection rate 52.6% below threshold 80.0%` |
| `hot020_02_aug_03.avi` | `Excessive blur (laplacian var 6.1 < limit 15.0)` |
| `hot021_01_aug_02.avi` | `Excessive blur (laplacian var 7.5 < limit 15.0)` |
| `hot021_01_aug_01.avi` | `Hand detection rate 70.3% below threshold 80.0%` |
| `hot021_01_aug_03.avi` | `Hand detection rate 73.4% below threshold 80.0%` |
| `hot021_02_aug_01.avi` | `Hand detection rate 75.8% below threshold 80.0%` |
| `hot021_02_aug_02.avi` | `Excessive blur (laplacian var 8.5 < limit 15.0)` |
| `hot021_02_aug_03.avi` | `Hand detection rate 48.5% below threshold 80.0%` |
| `hot022_02_aug_02.avi` | `Excessive blur (laplacian var 4.7 < limit 15.0)` |
| `hot022_01_aug_03.avi` | `Excessive blur (laplacian var 3.9 < limit 15.0)` |
| `hot022_01_aug_01.avi` | `Hand detection rate 65.9% below threshold 80.0%` |
| `hot022_01_aug_02.avi` | `Hand detection rate 49.5% below threshold 80.0%` |
| `hot023_01_aug_02.avi` | `Excessive blur (laplacian var 12.1 < limit 15.0)` |
| `hot022_02_aug_03.avi` | `Hand detection rate 7.7% below threshold 80.0%` |
| `hot023_02_aug_01.avi` | `Excessive blur (laplacian var 4.1 < limit 15.0)` |
| `hot024_01_aug_01.avi` | `Excessive blur (laplacian var 14.3 < limit 15.0)` |
| `hot023_02_aug_02.avi` | `Excessive blur (laplacian var 11.6 < limit 15.0)` |
| `hot024_02_aug_02.avi` | `Excessive blur (laplacian var 5.8 < limit 15.0)` |
| `hot024_01_aug_02.avi` | `Excessive blur (laplacian var 7.4 < limit 15.0)` |
| `hot024_02_aug_03.avi` | `Hand detection rate 76.6% below threshold 80.0%` |
| `hot025_02_aug_03.avi` | `Excessive blur (laplacian var 7.4 < limit 15.0)` |
| `hot025_02_aug_01.avi` | `Hand detection rate 67.6% below threshold 80.0%` |
| `hot026_01_aug_03.avi` | `Excessive blur (laplacian var 9.8 < limit 15.0)` |
| `hot_001_02_aug_01.avi` | `Excessive blur (laplacian var 6.9 < limit 15.0)` |
| `hot026_02_aug_02.avi` | `Hand detection rate 59.2% below threshold 80.0%` |
| `hot_003_01_aug_03.avi` | `Excessive blur (laplacian var 3.2 < limit 15.0)` |
| `hot_003_02_aug_03.avi` | `Hand detection rate 78.9% below threshold 80.0%` |
| `hot_005_01_aug_03.avi` | `Excessive blur (laplacian var 6.1 < limit 15.0)` |
| `hot_005_02_aug_01.avi` | `Excessive blur (laplacian var 13.0 < limit 15.0)` |
| `hot_003_02_aug_02.avi` | `Hand detection rate 39.5% below threshold 80.0%` |
| `hot_006_02_aug_01.avi` | `Excessive blur (laplacian var 9.1 < limit 15.0)` |
| `hot_006_02_aug_03.avi` | `Excessive blur (laplacian var 12.0 < limit 15.0)` |
| `hot_005_02_aug_03.avi` | `Hand detection rate 74.6% below threshold 80.0%` |
| `hot_006_01_aug_01.avi` | `Hand detection rate 31.0% below threshold 80.0%` |
| `hot_008_02_aug_03.avi` | `Excessive blur (laplacian var 7.9 < limit 15.0)` |
| `hot_009_02_aug_01.avi` | `Excessive blur (laplacian var 7.4 < limit 15.0)` |
| `hot_009_02_aug_03.avi` | `Excessive blur (laplacian var 14.3 < limit 15.0)` |
| `hot_009_02_aug_02.avi` | `Hand detection rate 73.3% below threshold 80.0%` |
| `hot_012_01_aug_01.avi` | `Excessive blur (laplacian var 7.4 < limit 15.0)` |
| `hot_010_02_aug_02.avi` | `Hand detection rate 73.0% below threshold 80.0%` |
| `hot_013_02_aug_02.avi` | `Excessive blur (laplacian var 9.4 < limit 15.0)` |
| `hot_014_01_aug_01.avi` | `Hand detection rate 68.9% below threshold 80.0%` |
| `hot_013_02_aug_03.avi` | `Excessive blur (laplacian var 12.6 < limit 15.0)` |
| `hot_015_01_aug_02.avi` | `Excessive blur (laplacian var 10.9 < limit 15.0)` |
| `hot_015_02_aug_03.avi` | `Hand detection rate 79.3% below threshold 80.0%` |
| `hot_014_01_aug_02.avi` | `Hand detection rate 21.6% below threshold 80.0%` |
| `hot_016_02_aug_01.avi` | `Excessive blur (laplacian var 11.0 < limit 15.0)` |
| `hot_017_01_aug_03.avi` | `Excessive blur (laplacian var 8.7 < limit 15.0)` |
| `hot_018_01_aug_01.avi` | `Excessive blur (laplacian var 9.8 < limit 15.0)` |
| `hot_018_01_aug_02.avi` | `Excessive blur (laplacian var 5.1 < limit 15.0)` |
| `hot_018_02_aug_03.avi` | `Excessive blur (laplacian var 6.5 < limit 15.0)` |
| `hot_020_01_aug_02.avi` | `Excessive blur (laplacian var 14.4 < limit 15.0)` |
| `hot_017_01_aug_01.avi` | `Hand detection rate 7.9% below threshold 80.0%` |
| `hot_019_01_aug_01.avi` | `Hand detection rate 6.6% below threshold 80.0%` |
| `hot_019_02_aug_01.avi` | `Hand detection rate 47.6% below threshold 80.0%` |
| `hot_021_01_aug_01.avi` | `Excessive blur (laplacian var 8.1 < limit 15.0)` |
| `hot_021_01_aug_03.avi` | `Excessive blur (laplacian var 13.0 < limit 15.0)` |
| `hot_021_02_aug_01.avi` | `Excessive blur (laplacian var 12.7 < limit 15.0)` |
| `hot_022_01_aug_01.avi` | `Excessive blur (laplacian var 7.4 < limit 15.0)` |
| `hot_022_02_aug_01.avi` | `Excessive blur (laplacian var 4.5 < limit 15.0)` |
| `hot_023_01_aug_03.avi` | `Excessive blur (laplacian var 5.6 < limit 15.0)` |
| `hot_023_02_aug_01.avi` | `Excessive blur (laplacian var 5.6 < limit 15.0)` |
| `hot_021_02_aug_02.avi` | `Hand detection rate 1.5% below threshold 80.0%` |
| `hot_022_01_aug_02.avi` | `Hand detection rate 67.0% below threshold 80.0%` |
| `hot_026_01_aug_02.avi` | `Excessive blur (laplacian var 7.7 < limit 15.0)` |
| `pain001_01_aug_02.avi` | `Excessive blur (laplacian var 12.8 < limit 15.0)` |
| `pain001_02_aug_01.avi` | `Excessive blur (laplacian var 5.2 < limit 15.0)` |
| `pain001_02_aug_02.avi` | `Excessive blur (laplacian var 7.1 < limit 15.0)` |
| `pain001_01_aug_03.avi` | `Excessive blur (laplacian var 11.9 < limit 15.0)` |
| `pain001_02_aug_03.avi` | `Excessive blur (laplacian var 13.0 < limit 15.0)` |
| `pain002_01_aug_03.avi` | `Excessive blur (laplacian var 5.0 < limit 15.0)` |
| `pain002_02_aug_03.avi` | `Excessive blur (laplacian var 2.9 < limit 15.0)` |
| `pain003_01_aug_01.avi` | `Excessive blur (laplacian var 7.5 < limit 15.0)` |
| `pain003_01_aug_02.avi` | `Hand detection rate 73.7% below threshold 80.0%` |
| `pain003_02_aug_01.avi` | `Excessive blur (laplacian var 5.4 < limit 15.0)` |
| `pain003_01_aug_03.avi` | `Hand detection rate 73.7% below threshold 80.0%` |
| `pain004_01_aug_01.avi` | `Excessive blur (laplacian var 14.6 < limit 15.0)` |
| `pain004_01_aug_02.avi` | `Hand detection rate 61.5% below threshold 80.0%` |
| `pain003_02_aug_02.avi` | `Hand detection rate 8.9% below threshold 80.0%` |
| `pain003_02_aug_03.avi` | `Hand detection rate 36.7% below threshold 80.0%` |
| `pain004_02_aug_02.avi` | `Excessive blur (laplacian var 7.7 < limit 15.0)` |
| `pain005_01_aug_02.avi` | `Hand detection rate 61.3% below threshold 80.0%` |
| `pain006_01_aug_01.avi` | `Excessive blur (laplacian var 7.4 < limit 15.0)` |
| `pain006_01_aug_03.avi` | `Hand detection rate 11.1% below threshold 80.0%` |
| `pain007_01_aug_02.avi` | `Excessive blur (laplacian var 4.3 < limit 15.0)` |
| `pain007_01_aug_03.avi` | `Excessive blur (laplacian var 6.8 < limit 15.0)` |
| `pain007_02_aug_03.avi` | `Excessive blur (laplacian var 14.7 < limit 15.0)` |
| `pain007_01_aug_01.avi` | `Hand detection rate 18.4% below threshold 80.0%` |
| `pain008_01_aug_02.avi` | `Excessive blur (laplacian var 3.6 < limit 15.0)` |
| `pain008_02_aug_02.avi` | `Excessive blur (laplacian var 4.6 < limit 15.0)` |
| `pain009_02_aug_01.avi` | `Excessive blur (laplacian var 11.4 < limit 15.0)` |
| `pain009_01_aug_01.avi` | `Hand detection rate 1.1% below threshold 80.0%` |
| `pain009_01_aug_02.avi` | `Excessive blur (laplacian var 9.4 < limit 15.0)` |
| `pain009_01_aug_03.avi` | `Excessive blur (laplacian var 3.1 < limit 15.0)` |
| `pain009_02_aug_03.avi` | `Hand detection rate 0.0% below threshold 80.0%` |
| `pain009_02_aug_02.avi` | `Hand detection rate 3.9% below threshold 80.0%` |
| `pain010_01_aug_03.avi` | `Hand detection rate 39.2% below threshold 80.0%` |
| `pain010_02_aug_01.avi` | `Excessive blur (laplacian var 4.6 < limit 15.0)` |
| `pain010_02_aug_02.avi` | `Excessive blur (laplacian var 6.0 < limit 15.0)` |
| `pain010_02_aug_03.avi` | `Excessive blur (laplacian var 4.8 < limit 15.0)` |
| `pain011_02_aug_01.avi` | `Excessive blur (laplacian var 7.8 < limit 15.0)` |
| `pain011_01_aug_01.avi` | `Hand detection rate 33.3% below threshold 80.0%` |
| `pain011_02_aug_02.avi` | `Hand detection rate 14.8% below threshold 80.0%` |
| `pain012_02_aug_01.avi` | `Excessive blur (laplacian var 5.8 < limit 15.0)` |
| `pain012_01_aug_03.avi` | `Hand detection rate 75.6% below threshold 80.0%` |
| `pain012_02_aug_03.avi` | `Excessive blur (laplacian var 11.7 < limit 15.0)` |
| `pain013_01_aug_02.avi` | `Excessive blur (laplacian var 4.0 < limit 15.0)` |
| `pain013_02_aug_01.avi` | `Excessive blur (laplacian var 6.2 < limit 15.0)` |
| `pain013_02_aug_02.avi` | `Hand detection rate 61.7% below threshold 80.0%` |
| `pain014_02_aug_01.avi` | `Hand detection rate 48.1% below threshold 80.0%` |
| `pain014_02_aug_03.avi` | `Excessive blur (laplacian var 5.9 < limit 15.0)` |
| `pain015_01_aug_02.avi` | `Excessive blur (laplacian var 10.2 < limit 15.0)` |
| `pain016_01_aug_02.avi` | `Excessive blur (laplacian var 6.3 < limit 15.0)` |
| `pain016_02_aug_01.avi` | `Hand detection rate 14.3% below threshold 80.0%` |
| `pain016_02_aug_03.avi` | `Hand detection rate 18.2% below threshold 80.0%` |
| `pain016_02_aug_02.avi` | `Hand detection rate 32.5% below threshold 80.0%` |
| `pain017_01_aug_01.avi` | `Hand detection rate 76.2% below threshold 80.0%` |
| `pain017_02_aug_01.avi` | `Excessive blur (laplacian var 4.4 < limit 15.0)` |
| `pain017_01_aug_03.avi` | `Excessive blur (laplacian var 13.2 < limit 15.0)` |
| `pain017_02_aug_02.avi` | `Excessive blur (laplacian var 8.8 < limit 15.0)` |
| `pain017_02_aug_03.avi` | `Hand detection rate 60.5% below threshold 80.0%` |
| `pain018_02_aug_02.avi` | `Excessive blur (laplacian var 8.1 < limit 15.0)` |
| `pain019_01_aug_02.avi` | `Hand detection rate 9.1% below threshold 80.0%` |
| `pain019_01_aug_03.avi` | `Excessive blur (laplacian var 5.1 < limit 15.0)` |
| `pain019_02_aug_02.avi` | `Hand detection rate 6.4% below threshold 80.0%` |
| `pain019_02_aug_03.avi` | `Hand detection rate 69.2% below threshold 80.0%` |
| `pain020_01_aug_02.avi` | `Excessive blur (laplacian var 6.7 < limit 15.0)` |
| `pain020_01_aug_03.avi` | `Excessive blur (laplacian var 4.5 < limit 15.0)` |
| `pain020_02_aug_01.avi` | `Excessive blur (laplacian var 5.7 < limit 15.0)` |
| `pain020_02_aug_02.avi` | `Excessive blur (laplacian var 6.3 < limit 15.0)` |
| `pain021_01_aug_01.avi` | `Excessive blur (laplacian var 5.3 < limit 15.0)` |
| `pain021_01_aug_02.avi` | `Excessive blur (laplacian var 9.8 < limit 15.0)` |
| `pain021_01_aug_03.avi` | `Excessive blur (laplacian var 4.3 < limit 15.0)` |
| `pain021_02_aug_01.avi` | `Hand detection rate 9.9% below threshold 80.0%` |
| `pain021_02_aug_02.avi` | `Excessive blur (laplacian var 3.4 < limit 15.0)` |
| `pain022_02_aug_03.avi` | `Excessive blur (laplacian var 4.1 < limit 15.0)` |
| `pain022_02_aug_02.avi` | `Hand detection rate 74.4% below threshold 80.0%` |
| `pain022_02_aug_01.avi` | `Hand detection rate 48.7% below threshold 80.0%` |
| `pain022_01_aug_01.avi` | `Underexposure (mean luma 31.0 < limit 35.0)` |
| `pain023_02_aug_03.avi` | `Hand detection rate 65.3% below threshold 80.0%` |
| `pain024_01_aug_02.avi` | `Excessive blur (laplacian var 4.8 < limit 15.0)` |
| `pain025_01_aug_01.avi` | `Excessive blur (laplacian var 11.3 < limit 15.0)` |
| `pain025_01_aug_03.avi` | `Excessive blur (laplacian var 5.4 < limit 15.0)` |
| `pain026_01_aug_03.avi` | `Excessive blur (laplacian var 11.2 < limit 15.0)` |
| `pain026_02_aug_01.avi` | `Excessive blur (laplacian var 4.7 < limit 15.0)` |
| `pain026_02_aug_03.avi` | `Excessive blur (laplacian var 6.7 < limit 15.0)` |
| `pain_001_01_aug_02.avi` | `Excessive blur (laplacian var 2.6 < limit 15.0)` |
| `pain_001_02_aug_03.avi` | `Excessive blur (laplacian var 14.6 < limit 15.0)` |
| `pain_001_02_aug_02.avi` | `Excessive blur (laplacian var 9.0 < limit 15.0)` |
| `pain_001_01_aug_03.avi` | `Excessive blur (laplacian var 7.6 < limit 15.0)` |
| `pain_002_01_aug_02.avi` | `Excessive blur (laplacian var 5.8 < limit 15.0)` |
| `pain_002_02_aug_01.avi` | `Excessive blur (laplacian var 10.3 < limit 15.0)` |
| `pain_003_01_aug_03.avi` | `Excessive blur (laplacian var 12.9 < limit 15.0)` |
| `pain_003_02_aug_02.avi` | `Excessive blur (laplacian var 8.3 < limit 15.0)` |
| `pain_004_01_aug_01.avi` | `Excessive blur (laplacian var 4.7 < limit 15.0)` |
| `pain_005_02_aug_02.avi` | `Excessive blur (laplacian var 10.0 < limit 15.0)` |
| `pain_006_02_aug_01.avi` | `Excessive blur (laplacian var 11.5 < limit 15.0)` |
| `pain_007_02_aug_02.avi` | `Excessive blur (laplacian var 8.9 < limit 15.0)` |
| `pain_008_01_aug_01.avi` | `Excessive blur (laplacian var 10.6 < limit 15.0)` |
| `pain_008_02_aug_03.avi` | `Excessive blur (laplacian var 7.4 < limit 15.0)` |
| `pain_009_01_aug_01.avi` | `Excessive blur (laplacian var 9.8 < limit 15.0)` |
| `pain_009_01_aug_02.avi` | `Hand detection rate 8.0% below threshold 80.0%` |
| `pain_009_02_aug_01.avi` | `Hand detection rate 37.7% below threshold 80.0%` |
| `pain_009_01_aug_03.avi` | `Hand detection rate 20.5% below threshold 80.0%` |
| `pain_009_02_aug_03.avi` | `Excessive blur (laplacian var 13.2 < limit 15.0)` |
| `pain_012_01_aug_03.avi` | `Excessive blur (laplacian var 4.9 < limit 15.0)` |
| `pain_014_02_aug_03.avi` | `Excessive blur (laplacian var 11.0 < limit 15.0)` |
| `pain_015_01_aug_01.avi` | `Excessive blur (laplacian var 14.7 < limit 15.0)` |
| `pain_015_01_aug_03.avi` | `Excessive blur (laplacian var 10.4 < limit 15.0)` |
| `pain_015_02_aug_02.avi` | `Excessive blur (laplacian var 3.9 < limit 15.0)` |
| `pain_010_01_aug_02.avi` | `Hand detection rate 11.4% below threshold 80.0%` |
| `pain_017_01_aug_01.avi` | `Excessive blur (laplacian var 12.9 < limit 15.0)` |
| `pain_017_01_aug_02.avi` | `Excessive blur (laplacian var 12.2 < limit 15.0)` |
| `pain_018_01_aug_01.avi` | `Excessive blur (laplacian var 7.5 < limit 15.0)` |
| `pain_018_02_aug_03.avi` | `Excessive blur (laplacian var 5.2 < limit 15.0)` |
| `pain_019_01_aug_02.avi` | `Excessive blur (laplacian var 13.0 < limit 15.0)` |
| `pain_017_01_aug_03.avi` | `Hand detection rate 71.2% below threshold 80.0%` |
| `pain_020_02_aug_01.avi` | `Excessive blur (laplacian var 14.2 < limit 15.0)` |
| `pain_022_02_aug_03.avi` | `Excessive blur (laplacian var 5.8 < limit 15.0)` |
| `pain_023_02_aug_03.avi` | `Hand detection rate 12.0% below threshold 80.0%` |
| `pain_024_01_aug_02.avi` | `Excessive blur (laplacian var 9.0 < limit 15.0)` |
| `pain_024_02_aug_02.avi` | `Excessive blur (laplacian var 5.3 < limit 15.0)` |
| `pain_025_02_aug_03.avi` | `Excessive blur (laplacian var 9.6 < limit 15.0)` |
| `pain_026_01_aug_02.avi` | `Excessive blur (laplacian var 11.6 < limit 15.0)` |
| `pain_026_01_aug_03.avi` | `Excessive blur (laplacian var 11.0 < limit 15.0)` |
| `pain_026_02_aug_03.avi` | `Excessive blur (laplacian var 3.6 < limit 15.0)` |

## Downstream Training Integration Guide

To re-train the Emergency model using the newly augmented dataset, run the following pipeline sequence:

```bash
# 1. Extract frames from augmented folders
python -m scripts.extract_frames --dataset SOS_Augmented

# 2. Extract landmark skeletal data
python -m scripts.process_images
python -m scripts.extract_landmarks

# 3. Engineer features & Train model
python -m scripts.feature_engineering
python -m scripts.train
```
