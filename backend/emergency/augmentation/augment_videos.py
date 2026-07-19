"""Production-grade batch video data augmentation runner for the Emergency Gesture Recognition dataset.

Supports multi-threaded execution, resuming interrupted runs, quality checks (blur/exposure),
MediaPipe hand tracking validation, and metadata logging.
"""
from __future__ import annotations

import os
import sys
import json
import random
import logging
import argparse
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import cv2
import numpy as np
from tqdm import tqdm

# Add parent directories to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

# Import config and utils
import augmentation_config as cfg
import augmentation_utils as utils

# Setup logging
os.makedirs(str(cfg.LOG_DIR), exist_ok=True)
log_file_path = cfg.LOG_DIR / "augmentation.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("video_augmentation")


def parse_arguments():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="MediSign-AI Video Augmentation Tool")
    parser.add_argument(
        "--sample-only",
        action="store_true",
        help="Augment exactly one video file for validation/review and exit."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing augmented files."
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=cfg.NUM_WORKERS,
        help="Number of concurrent threads to use."
    )
    return parser.parse_args()


def generate_combo_parameters(width: int, height: int, seed: int) -> dict:
    """Generate randomized parameters for enabled augmentations using a fixed seed."""
    rng = np.random.default_rng(seed)
    
    # List of available augmentations
    available = []
    if cfg.ENABLE_BRIGHTNESS: available.append("brightness")
    if cfg.ENABLE_CONTRAST: available.append("contrast")
    if cfg.ENABLE_GAMMA: available.append("gamma")
    if cfg.ENABLE_CLAHE: available.append("clahe")
    if cfg.ENABLE_GAUSSIAN_BLUR: available.append("gaussian_blur")
    if cfg.ENABLE_GAUSSIAN_NOISE: available.append("gaussian_noise")
    if cfg.ENABLE_ISO_NOISE: available.append("iso_noise")
    if cfg.ENABLE_WHITE_BALANCE: available.append("white_balance")
    if cfg.ENABLE_SHADOW: available.append("shadow")
    if cfg.ENABLE_MOTION_BLUR: available.append("motion_blur")
    if cfg.ENABLE_JPEG_COMPRESSION: available.append("jpeg_compression")
    if cfg.ENABLE_ROTATION: available.append("rotation")
    if cfg.ENABLE_ZOOM: available.append("zoom")
    if cfg.ENABLE_TRANSLATION: available.append("translation")
    
    # Randomly select 2 to 4 augmentations to apply in the combination
    num_to_apply = rng.integers(2, 5)
    selected = rng.choice(available, size=min(len(available), num_to_apply), replace=False)
    
    params = {}
    
    for aug in selected:
        if aug == "brightness":
            params["brightness"] = float(rng.uniform(cfg.BRIGHTNESS_RANGE[0], cfg.BRIGHTNESS_RANGE[1]))
        elif aug == "contrast":
            params["contrast"] = float(rng.uniform(cfg.CONTRAST_RANGE[0], cfg.CONTRAST_RANGE[1]))
        elif aug == "gamma":
            params["gamma"] = float(rng.uniform(cfg.GAMMA_RANGE[0], cfg.GAMMA_RANGE[1]))
        elif aug == "clahe":
            params["clahe"] = {
                "clip_limit": float(rng.uniform(1.5, 3.0)),
                "tile_grid_size": [8, 8]
            }
        elif aug == "gaussian_blur":
            kernel = int(rng.choice(cfg.GAUSSIAN_BLUR_KERNELS))
            if kernel % 2 == 0: kernel += 1
            params["gaussian_blur"] = kernel
        elif aug == "gaussian_noise":
            params["gaussian_noise"] = float(rng.uniform(cfg.GAUSSIAN_NOISE_STD[0], cfg.GAUSSIAN_NOISE_STD[1]))
        elif aug == "iso_noise":
            params["iso_noise"] = float(rng.uniform(cfg.ISO_NOISE_LEVEL[0], cfg.ISO_NOISE_LEVEL[1]))
        elif aug == "white_balance":
            # Decide warm or cool
            if rng.random() > 0.5:
                params["white_balance"] = float(rng.uniform(cfg.TEMP_WARM_FACTOR[0], cfg.TEMP_WARM_FACTOR[1]))
            else:
                params["white_balance"] = float(rng.uniform(cfg.TEMP_COOL_FACTOR[0], cfg.TEMP_COOL_FACTOR[1]))
        elif aug == "shadow":
            # Generate random shadow polygon vertices (3 to 4 points)
            num_pts = rng.integers(3, 5)
            pts = []
            for _ in range(num_pts):
                px = int(rng.uniform(0, width))
                py = int(rng.uniform(0, height))
                pts.append([px, py])
            params["shadow"] = {
                "poly": pts,
                "opacity": float(rng.uniform(cfg.SHADOW_OPACITY[0], cfg.SHADOW_OPACITY[1]))
            }
        elif aug == "motion_blur":
            kernel = int(rng.choice(cfg.MOTION_BLUR_KERNELS))
            if kernel % 2 == 0: kernel += 1
            params["motion_blur"] = {
                "kernel_size": kernel,
                "angle": float(rng.uniform(0, 360))
            }
        elif aug == "jpeg_compression":
            params["jpeg_compression"] = int(rng.integers(cfg.JPEG_QUALITY_RANGE[0], cfg.JPEG_QUALITY_RANGE[1] + 1))
        elif aug == "rotation":
            params["rotation"] = float(rng.uniform(cfg.ROTATION_ANGLE_RANGE[0], cfg.ROTATION_ANGLE_RANGE[1]))
        elif aug == "zoom":
            params["zoom"] = float(rng.uniform(cfg.ZOOM_RANGE[0], cfg.ZOOM_RANGE[1]))
        elif aug == "translation":
            max_dx = width * cfg.TRANSLATION_MAX_PCT
            max_dy = height * cfg.TRANSLATION_MAX_PCT
            params["translation"] = {
                "dx": float(rng.uniform(-max_dx, max_dx)),
                "dy": float(rng.uniform(-max_dy, max_dy))
            }
            
    return params


def apply_combo_augmentations(frame: np.ndarray, params: dict) -> np.ndarray:
    """Apply a combination of augmentations to a single frame using preset parameters."""
    out = frame.copy()
    
    # Maintain a deterministic ordering for pipeline execution
    order = [
        "zoom", "rotation", "translation",  # Geometric first
        "brightness", "contrast", "gamma", "clahe", "white_balance", "shadow", # Lighting/Color
        "gaussian_blur", "motion_blur",      # Blur
        "gaussian_noise", "iso_noise", "jpeg_compression" # Noises / compression last
    ]
    
    for key in order:
        if key not in params:
            continue
            
        val = params[key]
        if key == "zoom":
            out = utils.apply_zoom(out, val)
        elif key == "rotation":
            out = utils.apply_rotation(out, val)
        elif key == "translation":
            out = utils.apply_translation(out, val["dx"], val["dy"])
        elif key == "brightness":
            out = utils.apply_brightness(out, val)
        elif key == "contrast":
            out = utils.apply_contrast(out, val)
        elif key == "gamma":
            out = utils.apply_gamma(out, val)
        elif key == "clahe":
            out = utils.apply_clahe(out, val["clip_limit"], tuple(val["tile_grid_size"]))
        elif key == "white_balance":
            out = utils.apply_white_balance(out, val)
        elif key == "shadow":
            poly = np.array(val["poly"], dtype=np.int32)
            out = utils.apply_shadow(out, poly, val["opacity"])
        elif key == "gaussian_blur":
            out = utils.apply_gaussian_blur(out, val)
        elif key == "motion_blur":
            out = utils.apply_motion_blur(out, val["kernel_size"], val["angle"])
        elif key == "gaussian_noise":
            out = utils.apply_gaussian_noise(out, val)
        elif key == "iso_noise":
            out = utils.apply_iso_noise(out, val)
        elif key == "jpeg_compression":
            out = utils.apply_jpeg_compression(out, val)
            
    return out


def process_video_variation(
    video_path: Path,
    output_dir: Path,
    variation_idx: int,
    overwrite: bool,
    validator: utils.HandDetectorValidator | None
) -> dict:
    """Process a single augmented variation for a video.
    
    Returns:
        dict: Execution status, metrics, and parameters details.
    """
    label = video_path.parent.name
    video_stem = video_path.stem
    output_filename = f"{video_stem}_aug_{variation_idx:02d}.avi"
    output_path = output_dir / label / output_filename
    metadata_path = output_path.with_suffix(".json")
    
    # Generate seed based on name hash + variation index
    seed = abs(hash(f"{video_stem}_{variation_idx}")) % (2**32)
    
    summary = {
        "original_video": str(video_path),
        "augmented_video": str(output_path),
        "label": label,
        "seed": seed,
        "status": "pending",
        "reason": "",
        "metrics": {},
        "params": {}
    }
    
    # Resume check
    if not overwrite and output_path.exists() and metadata_path.exists():
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                saved_meta = json.load(f)
                summary["status"] = "skipped"
                summary["metrics"] = saved_meta.get("metrics", {})
                summary["params"] = saved_meta.get("applied_augmentations", {})
                return summary
        except Exception:
            pass  # re-process if json is corrupt
            
    # Open source capture
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        cap.release()
        summary["status"] = "failed"
        summary["reason"] = "Could not open source video container"
        return summary
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if frame_count <= 0 or fps <= 0:
        cap.release()
        summary["status"] = "failed"
        summary["reason"] = f"Invalid container properties (frames={frame_count}, fps={fps})"
        return summary

    # Output sizing
    out_width, out_height = width, height
    if cfg.TARGET_SIZE:
        out_width, out_height = cfg.TARGET_SIZE

    # Generate random parameters (held constant for the entire video clip)
    params = generate_combo_parameters(out_width, out_height, seed)
    summary["params"] = params
    
    # Ensure destination label folder exists
    os.makedirs(str(output_path.parent), exist_ok=True)
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*cfg.OUTPUT_CODEC)
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (out_width, out_height))
    
    if not writer.isOpened():
        cap.release()
        writer.release()
        summary["status"] = "failed"
        summary["reason"] = f"Could not initialize output VideoWriter on path {output_path}"
        return summary
        
    # Process frames
    total_blur = 0.0
    total_exposure = 0.0
    hands_detected = 0
    frames_written = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Resize if required
            if cfg.TARGET_SIZE and (width != out_width or height != out_height):
                frame = cv2.resize(frame, (out_width, out_height), interpolation=cv2.INTER_LINEAR)
                
            # Apply augmentations
            aug_frame = apply_combo_augmentations(frame, params)
            
            # Evaluate blur & exposure metrics
            blur, exposure = utils.compute_quality_metrics(aug_frame)
            total_blur += blur
            total_exposure += exposure
            
            # MediaPipe Hand detection validation
            if validator is not None:
                if validator.has_hand(aug_frame):
                    hands_detected += 1
            
            # Write to disk
            writer.write(aug_frame)
            frames_written += 1
    except Exception as exc:
        cap.release()
        writer.release()
        if output_path.exists():
            output_path.unlink()
        summary["status"] = "failed"
        summary["reason"] = f"Runtime processing exception: {exc}"
        return summary
        
    cap.release()
    writer.release()
    
    if frames_written == 0:
        if output_path.exists():
            output_path.unlink()
        summary["status"] = "failed"
        summary["reason"] = "Processed 0 frames from source"
        return summary
        
    # Compute averages
    avg_blur = total_blur / frames_written
    avg_exposure = total_exposure / frames_written
    hand_detection_rate = hands_detected / frames_written if validator is not None else 1.0
    
    summary["metrics"] = {
        "blur_laplacian_var": avg_blur,
        "exposure_mean_luma": avg_exposure,
        "hand_detection_rate": hand_detection_rate,
        "frames_processed": frames_written
    }
    
    # --- Quality Constraints Checks ---
    rejection_reason = ""
    
    # 1. Blur Check
    if avg_blur < cfg.MIN_LAPLACIAN_VAR:
        rejection_reason = f"Excessive blur (laplacian var {avg_blur:.1f} < limit {cfg.MIN_LAPLACIAN_VAR})"
    
    # 2. Exposure Check
    elif avg_exposure < cfg.MIN_EXPOSURE:
        rejection_reason = f"Underexposure (mean luma {avg_exposure:.1f} < limit {cfg.MIN_EXPOSURE})"
    elif avg_exposure > cfg.MAX_EXPOSURE:
        rejection_reason = f"Overexposure (mean luma {avg_exposure:.1f} > limit {cfg.MAX_EXPOSURE})"
        
    # 3. MediaPipe Hands Check
    elif validator is not None and hand_detection_rate < cfg.MIN_DETECTION_RATE:
        rejection_reason = f"Hand detection rate {hand_detection_rate * 100:.1f}% below threshold {cfg.MIN_DETECTION_RATE * 100:.1f}%"
        
    # Rejection actions
    if rejection_reason:
        if output_path.exists():
            output_path.unlink()
        summary["status"] = "rejected"
        summary["reason"] = rejection_reason
        logger.info("[REJECT] Rejected augmented video %s: %s", output_filename, rejection_reason)
    else:
        # Save companion JSON metadata
        meta_payload = {
            "original_video": str(video_path.name),
            "augmented_video": str(output_filename),
            "label": label,
            "random_seed": seed,
            "applied_augmentations": params,
            "metrics": summary["metrics"]
        }
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta_payload, f, indent=2)
            
        summary["status"] = "completed"
        logger.info("[OK] Created augmented video %s (blur=%.1f, exp=%.1f, mp_rate=%.1f%%)",
                    output_filename, avg_blur, avg_exposure, hand_detection_rate * 100)
        
    return summary


def main():
    """Main execution loop."""
    args = parse_arguments()
    
    logger.info("=== Phase 3: Video Data Augmentation Subsystem ===")
    logger.info("Input directory: %s", cfg.INPUT_DIR)
    logger.info("Output directory: %s", cfg.OUTPUT_DIR)
    
    if not cfg.INPUT_DIR.exists():
        logger.error("Input directory %s does not exist. Exit.", cfg.INPUT_DIR)
        sys.exit(1)
        
    # Find all videos in input directory
    valid_exts = {".avi", ".mp4", ".mov", ".mkv", ".wmv"}
    video_files = []
    
    # Read class label folders
    label_folders = [d for d in cfg.INPUT_DIR.iterdir() if d.is_dir()]
    
    for folder in label_folders:
        for f in folder.iterdir():
            if f.is_file() and f.suffix.lower() in valid_exts:
                video_files.append(f)
                
    if not video_files:
        logger.error("No valid video files found in %s.", cfg.INPUT_DIR)
        sys.exit(1)
        
    logger.info("Found %d original videos across %d classes.", len(video_files), len(label_folders))
    
    # Initialize MediaPipe validator if task file is available
    validator = None
    if cfg.LANDMARKER_PATH.exists():
        logger.info("Initializing MediaPipe HandLandmarker from %s", cfg.LANDMARKER_PATH)
        try:
            validator = utils.HandDetectorValidator(cfg.LANDMARKER_PATH)
            logger.info("MediaPipe HandLandmarker loaded successfully.")
        except Exception as exc:
            logger.warning("Could not initialize MediaPipe HandLandmarker: %s. Hand validation is disabled.", exc)
    else:
        logger.warning("MediaPipe task file not found at %s. Hand validation is disabled.", cfg.LANDMARKER_PATH)

    # CLI Sample Mode Override
    if args.sample_only:
        logger.info("--- RUNNING IN SAMPLE-ONLY VERIFICATION MODE ---")
        # Choose a random video
        sample_video = random.choice(video_files)
        logger.info("Selected sample video for validation: %s", sample_video)
        
        # Run a single variation
        t_start = time.time()
        res = process_video_variation(sample_video, cfg.OUTPUT_DIR, 1, overwrite=True, validator=validator)
        t_duration = time.time() - t_start
        
        # Shutdown validator
        if validator:
            validator.close()
            
        # Write validation report
        os.makedirs(str(cfg.REPORT_DIR), exist_ok=True)
        report_path = cfg.BASE_DIR / "AUGMENTATION_REPORT.md"
        
        report_content = f"""# MediSign-AI Augmentation Verification Report

Generated automatically after running validation checks on a single video sample.

## Sample Execution Summary
* **Source Video**: `{res['original_video']}`
* **Target Video**: `{res['augmented_video']}`
* **Class Label**: `{res['label']}`
* **Random Seed**: `{res['seed']}`
* **Status**: `{res['status']}`
* **Processing Time**: `{t_duration:.2f} seconds`
* **Reason / Message**: `{res['reason'] or 'N/A'}`

## Verification Criteria Checks
"""
        
        if res["status"] == "completed" or res["status"] == "rejected":
            out_file = Path(res["augmented_video"])
            
            # Read properties of augmented file if it was created
            fps, frames, width, height, readable = 0.0, 0, 0, 0, False
            if out_file.exists():
                test_cap = cv2.VideoCapture(str(out_file))
                if test_cap.isOpened():
                    readable = True
                    fps = test_cap.get(cv2.CAP_PROP_FPS)
                    frames = int(test_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    width = int(test_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(test_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                test_cap.release()
                
            metrics = res.get("metrics", {})
            applied_params = res.get("params", {})
            
            report_content += f"""
### 1. OpenCV Container Readability
* **Output exists on disk**: `{out_file.exists()}`
* **Can be decoded by OpenCV**: `{readable}`
* **Target Resolution**: `{width} x {height}`

### 2. Codec and Parameter Consistency
* **Output Codec**: `{cfg.OUTPUT_CODEC}`
* **Output FPS**: `{fps}`
* **Output Frame Count**: `{frames}` (Expected matching source frame count)

### 3. Applied Random Parameters (Seed: `{res['seed']}`)
```json
{json.dumps(applied_params, indent=2)}
```

### 4. Evaluated Frame Quality & Hand Tracking Metrics
* **Average Blur (Laplacian variance)**: `{metrics.get('blur_laplacian_var', 0.0):.2f}` (Limit: `> {cfg.MIN_LAPLACIAN_VAR}`)
* **Average Exposure (mean luma)**: `{metrics.get('exposure_mean_luma', 0.0):.2f}` (Limits: `{cfg.MIN_EXPOSURE} - {cfg.MAX_EXPOSURE}`)
* **MediaPipe Hand Detection Rate**: `{metrics.get('hand_detection_rate', 0.0) * 100:.1f}%` (Limit: `> {cfg.MIN_DETECTION_RATE * 100:.1f}%`)

### 5. Final Determination
* **Verdict**: **{"APPROVED" if res['status'] == "completed" else "REJECTED"}**
"""
        else:
            report_content += f"""
### Processing Failure
* The pipeline encountered a container opening or writing crash.
* Error details: `{res['reason']}`
"""
            
        report_path.write_text(report_content, encoding="utf-8")
        logger.info("Sample augmentation verification completed. Written report to: %s", report_path)
        print("\n=======================================================")
        print("SAMPLE RUN VERDICT:", "APPROVED" if res['status'] == "completed" else "REJECTED")
        print("Written report to root directory: AUGMENTATION_REPORT.md")
        print("=======================================================\n")
        return

    # --- FULL DATASET PROCESSING MODE ---
    logger.info("Starting batch processing of full dataset.")
    
    # Prep tasks plan
    tasks = []
    for vp in video_files:
        for i in range(1, cfg.AUGMENTATIONS_PER_VIDEO + 1):
            tasks.append((vp, i))
            
    logger.info("Total augmentation tasks scheduled: %d variations.", len(tasks))
    
    # Stats trackers
    completed_cnt = 0
    skipped_cnt = 0
    rejected_cnt = 0
    failed_cnt = 0
    rejections_log = {}
    
    t_start_all = time.time()
    
    # Process pool
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                process_video_variation, vp, cfg.OUTPUT_DIR, idx, args.overwrite, validator
            ): (vp, idx) for vp, idx in tasks
        }
        
        # Display progress bar
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Augmenting Dataset", unit="video"):
            vp, idx = futures[fut]
            try:
                res = fut.result()
                status = res["status"]
                if status == "completed":
                    completed_cnt += 1
                elif status == "skipped":
                    skipped_cnt += 1
                elif status == "rejected":
                    rejected_cnt += 1
                    rejections_log[res["augmented_video"]] = res["reason"]
                elif status == "failed":
                    failed_cnt += 1
                    rejections_log[res["augmented_video"]] = res["reason"]
            except Exception as exc:
                failed_cnt += 1
                logger.error("Future execution threw an exception for %s variation %d: %s", vp.name, idx, exc)

    # Shutdown validator
    if validator:
        validator.close()
        
    duration = time.time() - t_start_all
    logger.info("Batch processing finished in %.1f seconds.", duration)
    
    # Compute output sizes and disk space
    def get_dir_size(directory: Path) -> float:
        total = 0
        if not directory.exists():
            return 0.0
        for path, dirs, files in os.walk(str(directory)):
            for f in files:
                fp = os.path.join(path, f)
                total += os.path.getsize(fp)
        return total / (1024 * 1024) # MB
        
    src_size = get_dir_size(cfg.INPUT_DIR)
    dest_size = get_dir_size(cfg.OUTPUT_DIR)
    
    # Class stats
    out_video_files = []
    if cfg.OUTPUT_DIR.exists():
        for d in cfg.OUTPUT_DIR.iterdir():
            if d.is_dir():
                for f in d.iterdir():
                    if f.is_file() and f.suffix.lower() == ".avi":
                        out_video_files.append(f)
                        
    # Generate DATASET_SUMMARY.md
    summary_path = cfg.BASE_DIR / "DATASET_SUMMARY.md"
    
    summary_content = f"""# MediSign-AI Augmented Dataset Summary

## General Pipeline Statistics
* **Processing Date**: `{time.strftime("%Y-%m-%d %H:%M:%S")}`
* **Total Processing Time**: `{duration:.1f} seconds`
* **Concurrence Worker Threads**: `{args.workers}`
* **Original Videos Count**: `{len(video_files)}`
* **Augmented Videos Count**: `{len(out_video_files)}`
* **Source Folder Disk Usage**: `{src_size:.2f} MB`
* **Augmented Folder Disk Usage**: `{dest_size:.2f} MB`

## Batch Tasks Breakdown
* **Successfully Generated Variations**: `{completed_cnt}`
* **Skipped (Existing / Resume-mode)**: `{skipped_cnt}`
* **Rejected (Quality/Hands Constraints)**: `{rejected_cnt}`
* **Processing Failures**: `{failed_cnt}`

## Per-Class Distribution statistics
| Class Label | Original Video Count | Augmented Video Count |
| :--- | :---: | :---: |
"""
    for folder in label_folders:
        label = folder.name
        orig_cnt = len([f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in valid_exts])
        
        aug_cnt = 0
        aug_label_dir = cfg.OUTPUT_DIR / label
        if aug_label_dir.exists():
            aug_cnt = len([f for f in aug_label_dir.iterdir() if f.is_file() and f.suffix.lower() == ".avi"])
            
        summary_content += f"| `{label}` | {orig_cnt} | {aug_cnt} |\n"
        
    summary_content += "\n## Rejected Videos Log\n"
    if rejections_log:
        summary_content += "| File Location | Rejection Reason |\n| :--- | :--- |\n"
        for path, reason in rejections_log.items():
            summary_content += f"| `{Path(path).name}` | `{reason}` |\n"
    else:
        summary_content += "*No videos were rejected during this run.*\n"
        
    summary_content += """
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
"""
    summary_path.write_text(summary_content, encoding="utf-8")
    logger.info("Summary report generated successfully at: %s", summary_path)


if __name__ == "__main__":
    main()
