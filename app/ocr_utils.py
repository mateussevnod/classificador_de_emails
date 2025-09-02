import io
from typing import List
from PIL import Image
import pytesseract
import fitz

def ocr_image(image_path: str, lang: str = "por+eng", psm: int = 6) -> str:
    try:
        config = f"--psm {psm}"
        with Image.open(image_path) as img:
            text = pytesseract.image_to_string(img, lang=lang, config=config)
            return (text or "").strip()
    except Exception:
        return ""

def _ocr_pixmap(pix: "fitz.Pixmap", lang: str = "por+eng", psm: int = 6) -> str:
    try:
        png_bytes = pix.tobytes("png")
        with Image.open(io.BytesIO(png_bytes)) as img:
            config = f"--psm {psm}"
            text = pytesseract.image_to_string(img, lang=lang, config=config)
            return (text or "").strip()
    except Exception:
        return ""

def ocr_pdf_to_text(pdf_path: str, lang: str = "por+eng", zoom: float = 2.0, psm: int = 6) -> str:
    try:
        with fitz.open(pdf_path) as doc:
            chunks: List[str] = []
            matrix = fitz.Matrix(zoom, zoom)
            for page in doc:
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                page_text = _ocr_pixmap(pix, lang=lang, psm=psm)
                if page_text:
                    chunks.append(page_text)
            return "\n\n".join(chunks).strip()
    except Exception:
        return ""

