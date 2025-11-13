from typing import Optional

import pytesseract


class OcrEngine:
    def __init__(self, tesseract_cmd: Optional[str] = None, lang: Optional[str] = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.lang = lang
        self._ok: Optional[bool] = None
        self._msg: str = ""

    def ensure_tesseract(self) -> bool:
        if self._ok is not None:
            return self._ok
        try:
            _ = pytesseract.get_tesseract_version()
            self._ok = True
            self._msg = "Tesseract OK"
        except (
            getattr(pytesseract, "TesseractNotFoundError", OSError),
            FileNotFoundError,
        ):
            self._ok = False
            self._msg = "Tesseract not found. Install it or set --tesseract-cmd."
        except (RuntimeError, OSError, ValueError) as e:
            self._ok = False
            self._msg = f"Tesseract error: {e}"
        return self._ok

    @property
    def status_message(self) -> str:
        return self._msg

    def image_to_text(self, image) -> str:
        if not self.ensure_tesseract():
            return ""
        try:
            kwargs = {"lang": self.lang} if self.lang else {}
            return pytesseract.image_to_string(image, **kwargs).strip()
        except (
            getattr(pytesseract, "TesseractError", Exception),
            OSError,
            RuntimeError,
        ):
            return ""
