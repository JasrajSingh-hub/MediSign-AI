import cv2
import numpy as np
import logging

logger = logging.getLogger("ocr_service.scanner")

class DocumentScannerService:
    @staticmethod
    def detect_document(image: np.ndarray) -> dict:
        """
        Detects a document boundary (largest 4-corner contour) in the image.
        Returns a dict: {
            "detected": bool,
            "points": np.ndarray or None,  # Shape (4, 2)
            "contour": np.ndarray or None
        }
        """
        try:
            if image is None or image.size == 0:
                logger.error("Empty image provided to detect_document")
                return {"detected": False, "points": None, "contour": None}

            # 1. Grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()

            # 2. Gaussian Blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # 3. Canny Edge Detection
            # We use OTSU's thresholding to compute Canny thresholds adaptively
            high_thresh, _ = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            low_thresh = 0.5 * high_thresh
            edged = cv2.Canny(blurred, low_thresh, high_thresh)

            # Dilate to join broken edges
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated = cv2.dilate(edged, kernel, iterations=1)

            # 4. Find Contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            # Sort contours by area in descending order
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

            for c in contours:
                # Approximate the contour
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)

                # A document contour should have 4 corners
                if len(approx) == 4 and cv2.isContourConvex(approx):
                    logger.info("Found a 4-point rectangle contour for document detection.")
                    # Reshape approx from (4, 1, 2) to (4, 2)
                    pts = approx.reshape(4, 2)
                    return {
                        "detected": True,
                        "points": pts,
                        "contour": c
                    }

            # Fallback if no 4-corner contour is large enough
            # We try to use the largest contour's bounding box as points if it covers > 10% of image area
            if contours:
                largest = contours[0]
                area = cv2.contourArea(largest)
                img_area = image.shape[0] * image.shape[1]
                if area > 0.1 * img_area:
                    x, y, w, h = cv2.boundingRect(largest)
                    pts = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], dtype="float32")
                    logger.info("No convex 4-point contour found. Falling back to largest bounding box.")
                    return {
                        "detected": True,
                        "points": pts,
                        "contour": largest
                    }

            logger.warning("No significant document contours detected.")
            return {"detected": False, "points": None, "contour": None}

        except Exception as e:
            logger.error(f"Error during document detection: {e}", exc_info=True)
            return {"detected": False, "points": None, "contour": None}

    @staticmethod
    def order_points(pts: np.ndarray) -> np.ndarray:
        """
        Orders coordinates in a clockwise manner: Top-Left, Top-Right, Bottom-Right, Bottom-Left.
        Input shape: (4, 2)
        """
        rect = np.zeros((4, 2), dtype="float32")
        
        # Top-left has smallest sum, bottom-right has largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        
        # Top-right has smallest diff, bottom-left has largest diff
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        
        return rect

    def correct_perspective(self, image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """
        Applies four-point perspective transform to get a top-down view of the document.
        """
        try:
            if pts is None or len(pts) != 4:
                logger.warning("Invalid points for perspective transform. Returning original image.")
                return image

            rect = self.order_points(pts)
            (tl, tr, br, bl) = rect

            # Compute width of new image
            width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            max_width = max(int(width_a), int(width_b))

            # Compute height of new image
            height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            max_height = max(int(height_a), int(height_b))

            # Guard against tiny dimensions
            if max_width < 10 or max_height < 10:
                logger.warning("Dimension of prospective crop too small. Returning original image.")
                return image

            # Construct destination points
            dst = np.array([
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1]
            ], dtype="float32")

            # Perspective transform matrix
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(image, M, (max_width, max_height))
            logger.info("Successfully corrected perspective.")
            return warped

        except Exception as e:
            logger.error(f"Error during perspective correction: {e}")
            return image

    @staticmethod
    def crop_document(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """
        Crops document using minimal bounding rectangle around points.
        """
        try:
            if pts is None or len(pts) == 0:
                return image
            
            x, y, w, h = cv2.boundingRect(np.array(pts, dtype=np.int32))
            if w > 10 and h > 10:
                cropped = image[y:y+h, x:x+w]
                logger.info("Successfully cropped document.")
                return cropped
            return image
        except Exception as e:
            logger.error(f"Error during cropping: {e}")
            return image

    @staticmethod
    def enhance_document(image: np.ndarray) -> np.ndarray:
        """
        Applies image enhancement pipeline:
        1. Grayscale
        2. Bilateral Filter (Noise removal, keeps edges sharp)
        3. CLAHE (Contrast enhancement)
        4. Sharpening (High contrast text definition)
        """
        try:
            if image is None or image.size == 0:
                return image

            # 1. Grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()

            # 2. Noise removal using Bilateral Filter
            # Keeps edges of letters sharp while smoothing out paper texture
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)

            # 3. CLAHE Contrast Limited Adaptive Histogram Equalization
            # Enhances local contrast to make faint ink text readable
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)

            # 4. Sharpening filter using unsharp masking kernel
            # Kernel enhances high-frequency boundaries (text contours)
            kernel = np.array([[0, -1, 0], 
                              [-1, 5, -1], 
                              [0, -1, 0]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)

            logger.info("Successfully enhanced document image.")
            return sharpened

        except Exception as e:
            logger.error(f"Error during image enhancement: {e}")
            return image
