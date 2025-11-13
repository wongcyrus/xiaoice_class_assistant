import os
import time
import hashlib
from datetime import datetime
from typing import Tuple

from PIL import Image

from .capture import ScreenCapture
from .ocr import OcrEngine


class MonitorController:
    def __init__(self, output_dir: str, interval: float, capture: ScreenCapture, ocr: OcrEngine):
        self.output_dir = output_dir
        self.interval = max(0.2, float(interval))
        self.capture = capture
        self.ocr = ocr
        self.last_text_hash = None
        os.makedirs(output_dir, exist_ok=True)

    @staticmethod
    def _text_hash(text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def _save_image(self, image: Image.Image) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{ts}.png"
        filepath = os.path.join(self.output_dir, filename)
        image.save(filepath)
        print(f"Saved: {filepath}")
        return filepath

    def process_once(self) -> Tuple[Image.Image, str, bool]:
        screenshot = self.capture.capture()
        text = self.ocr.image_to_text(screenshot)
        current_hash = self._text_hash(text)
        changed = self.last_text_hash != current_hash
        if changed:
            self._save_image(screenshot)
            snippet = (text[:120] + "…") if len(text) > 120 else text
            if snippet:
                print(f"Text changed: {snippet}")
            else:
                print("Text changed: <no text detected>")
            self.last_text_hash = current_hash
        return screenshot, text, changed

    def run_headless(self):
        print("Starting window monitor (headless)… Press Ctrl+C to stop")
        self.capture.ensure_monitor_selected(gui=False)
        if not self.ocr.ensure_tesseract():
            print(
                "Warning: Tesseract not found. OCR will be empty until it's "
                "installed or configured via --tesseract-cmd."
            )
        try:
            while True:
                self.process_once()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
        except Exception as e:
            print(f"\nStopped due to error: {e}")
