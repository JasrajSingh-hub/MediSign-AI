# MediSign-AI Augmentation Verification Report

Generated automatically after running validation checks on a single video sample.

## Sample Execution Summary
* **Source Video**: `C:\Users\kamle\OneDrive\Desktop\MediSign-AI\SOS\pain\pain001_01.avi`
* **Target Video**: `C:\Users\kamle\OneDrive\Desktop\MediSign-AI\SOS_Augmented\pain\pain001_01_aug_01.avi`
* **Class Label**: `pain`
* **Random Seed**: `4042283014`
* **Status**: `completed`
* **Processing Time**: `3.42 seconds`
* **Reason / Message**: `N/A`

## Verification Criteria Checks

### 1. OpenCV Container Readability
* **Output exists on disk**: `True`
* **Can be decoded by OpenCV**: `True`
* **Target Resolution**: `600 x 500`

### 2. Codec and Parameter Consistency
* **Output Codec**: `MJPG`
* **Output FPS**: `30.0`
* **Output Frame Count**: `88` (Expected matching source frame count)

### 3. Applied Random Parameters (Seed: `4042283014`)
```json
{
  "translation": {
    "dx": -16.46707257578436,
    "dy": 38.582784670539354
  },
  "clahe": {
    "clip_limit": 1.6760164614194615,
    "tile_grid_size": [
      8,
      8
    ]
  },
  "zoom": 1.0144780447355313,
  "gamma": 1.1695845649408332
}
```

### 4. Evaluated Frame Quality & Hand Tracking Metrics
* **Average Blur (Laplacian variance)**: `40.47` (Limit: `> 15.0`)
* **Average Exposure (mean luma)**: `97.01` (Limits: `35.0 - 220.0`)
* **MediaPipe Hand Detection Rate**: `100.0%` (Limit: `> 80.0%`)

### 5. Final Determination
* **Verdict**: **APPROVED**
