# Emergency Gesture Video Data Augmentation Subsystem

This subsystem provides a production-grade, multi-threaded video augmentation pipeline to expand the MediSign-AI Emergency Gesture Recognition video dataset (`SOS/`). It generates realistic lighting, blurring, geometric shifts, and noise variations to improve model generalization.

---

## Folder Structure

```
backend/emergency/augmentation/
├── augmentation_config.py   # Pipeline limits, enabled switches, and parameter ranges
├── augmentation_utils.py    # Frame-level transformations and quality/validation stubs
├── augment_videos.py        # Main execution runner script
├── preview.py               # Side-by-side OpenCV interactive video player
├── README.md                # This documentation file
├── logs/                    # Subsystem execution logs folder
└── reports/                 # Augmentation metrics and summary reports folder
```

---

## 1. Quick Start Commands

### A. Run Interactive Side-by-Side Previewer
Launch the previewer to visually inspect each augmentation on a random dataset video:
```bash
python backend/emergency/augmentation/preview.py
```
* **Controls**:
  * Tap `1` through `16` to switch between different transformations (including Combo 1/2).
  * Tap `R` to select another random video from `SOS/`.
  * Press `Q` or `ESC` to quit.

### B. Run Pipeline Validation (One Video Sample)
Before executing on the entire dataset, run the pipeline on exactly one video to verify container outputs, FPS/resolution matching, and MediaPipe landmark tracking compatibility:
```bash
python backend/emergency/augmentation/augment_videos.py --sample-only
```
* Generates output files inside `SOS_Augmented/` under the corresponding class folder.
* Creates `AUGMENTATION_REPORT.md` in the root workspace directory.

### C. Run Full Dataset Augmentation
When ready, run batch processing on all videos in parallel:
```bash
python backend/emergency/augmentation/augment_videos.py --workers 4
```
* Generates augmented video files and companion `.json` parameters metadata files under `SOS_Augmented/`.
* Excludes corrupted videos and skips already processed clips to allow resuming after interruptions.
* Generates `DATASET_SUMMARY.md` in the root workspace directory upon completion.

---

## 2. Configuration Settings

Open `augmentation_config.py` to modify pipeline behavior:
* **`AUGMENTATIONS_PER_VIDEO`**: Number of randomized variations to generate per input video (default: `3`).
* **`NUM_WORKERS`**: Concurrent thread workers for faster execution (default: `4`).
* **`MIN_DETECTION_RATE`**: The hand landmarks presence constraint. Augmented videos where MediaPipe fails to track hands on less than **80%** of frames are automatically discarded to maintain training validity.
* **`MIN_LAPLACIAN_VAR`**: Minimum Laplacian variance threshold. Excessively blurred videos are discarded.
* **`MIN_EXPOSURE` / `MAX_EXPOSURE`**: Grayscale luma limits to reject extremely dark or washed-out clips.
* **`ENABLE_X` Toggles**: Switch `True/False` to include/exclude specific augmentations from the randomized combo pool.

---

## 3. Supported Transformations

1. **Brightness Adjustment**: Matrix scaling in HSV color space.
2. **Contrast Tuning**: Linear scaling using `convertScaleAbs`.
3. **Gamma Correction**: Non-linear exposure shifting via lookup tables.
4. **CLAHE**: Adaptive local histogram equalization on the LAB color space L channel.
5. **Gaussian Blur**: Standard smoothing blur.
6. **Gaussian Noise**: Additive grayscale zero-mean noise.
7. **ISO Noise**: High ISO grain emulation.
8. **White Balance**: Shift color temperature warm or cool.
9. **Shadow Overlay**: Draw semi-transparent black polygons (blockage simulation).
10. **Motion Blur**: Blur along a specific directional angle.
11. **JPEG Compression**: Lossy compression artifact simulation.
12. **Rotation**: Center rotation with border reflection.
13. **Zoom**: Cropping center portion and resizing.
14. **Translation**: Translation offset shifting with border reflection.
15. **Combinations**: Sequenced pipelines combining multiple geometric, lighting, and noise filters.

---

## 4. Downstream Integration Pipeline

After generating the augmented dataset (`SOS_Augmented/`), re-run the MediSign training scripts using the following command path:

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
