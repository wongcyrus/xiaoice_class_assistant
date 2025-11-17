#!/usr/bin/env python3
import os
import argparse

from monitor.capture import ScreenCapture
from monitor.ocr import OcrEngine
from monitor.core import MonitorController
from monitor.gui import run_preview


def parse_args():
    parser = argparse.ArgumentParser(
        description="Monitor screen text changes and save screenshots."
    )
    parser.add_argument("--preview", action="store_true", help="Show GUI preview")
    parser.add_argument("--headless", action="store_true", help="Force console mode")
    parser.add_argument(
        "--interval", type=float, default=1.0, help="Capture interval in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--lang", type=str, default=None, help="Tesseract language code (e.g., 'eng', 'chi_sim')"
    )
    parser.add_argument(
        "--output", type=str, default="screenshots", help="Output directory for saved images"
    )
    parser.add_argument(
        "--monitor", type=int, default=None, help="Monitor index to capture (mss index)"
    )
    parser.add_argument(
        "--detect-mode",
        type=str,
        default="ocr",
        choices=["ocr", "image", "both"],
        help="Change detection method: 'ocr' (slow, text-based), 'image' (fast, pixel-based), 'both' (saves if either changes)",
    )
    parser.add_argument(
        "--tesseract-cmd",
        type=str,
        default=(r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe" if os.name == "nt" else None),
        help=(
            "Path to tesseract executable. On Windows, defaults to "
            r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    tesseract_cmd = args.tesseract_cmd
    ocr = OcrEngine(tesseract_cmd=tesseract_cmd, lang=args.lang)
    capture = ScreenCapture(monitor_index=args.monitor)
    controller = MonitorController(
        output_dir=args.output,
        interval=args.interval,
        capture=capture,
        ocr=ocr,
        detect_mode=args.detect_mode,
    )
    use_preview = args.preview or (os.name == "nt" and not args.headless)
    if use_preview:
        run_preview(controller)
    else:
        controller.run_headless()
