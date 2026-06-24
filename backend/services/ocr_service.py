import numpy as np
import logging

logger = logging.getLogger("ocr_service.ocr")

class OCRService:
    _reader = None

    @classmethod
    def get_reader(cls):
        """Lazy load and cache the EasyOCR reader instance."""
        if cls._reader is None:
            logger.info("Initializing EasyOCR reader for English and Hindi...")
            try:
                import easyocr
                # gpu=True will auto-fallback to CPU if CUDA is not available or torch fails to find GPU
                cls._reader = easyocr.Reader(['en', 'hi'], gpu=True)
                logger.info("EasyOCR reader initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR reader: {e}", exc_info=True)
                raise RuntimeError(f"OCR Reader setup failed: {e}")
        return cls._reader

    def extract_text(self, image: np.ndarray) -> dict:
        """
        Extracts text from a numpy image using EasyOCR.
        Returns:
        {
            "text": str,
            "confidence": float,
            "regions": [
                {
                    "bbox": [[x, y], [x, y], [x, y], [x, y]],
                    "text": str,
                    "confidence": float
                }, ...
            ]
        }
        """
        try:
            if image is None or image.size == 0:
                logger.error("Empty image provided to OCR extraction.")
                return {
                    "text": "",
                    "confidence": 0.0,
                    "regions": []
                }

            reader = self.get_reader()
            logger.info("Performing OCR text extraction...")
            
            # readtext returns: [([[x0,y0], [x1,y1], [x2,y2], [x3,y3]], text, confidence), ...]
            results = reader.readtext(image)
            
            regions = []
            texts = []
            total_confidence = 0.0
            
            for bbox, text, conf in results:
                # Convert bbox elements to list of standard Python integers for JSON serialization
                clean_bbox = [[int(pt[0]), int(pt[1])] for pt in bbox]
                regions.append({
                    "bbox": clean_bbox,
                    "text": text,
                    "confidence": float(conf)
                })
                texts.append(text)
                total_confidence += float(conf)
                
            raw_text = "\n".join(texts)
            avg_confidence = float(total_confidence / len(results)) if results else 0.0
            
            logger.info(f"OCR complete. Extracted {len(results)} lines of text, overall confidence: {avg_confidence:.2f}")
            return {
                "text": raw_text,
                "confidence": avg_confidence,
                "regions": regions
            }
        except Exception as e:
            logger.error(f"Error during OCR execution: {e}", exc_info=True)
            return {
                "text": "",
                "confidence": 0.0,
                "regions": []
            }
