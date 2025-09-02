import os
import regex as re
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pdfminer.high_level import extract_text
from app.ocr_utils import ocr_image
from app.model_infer import suggest_reply, detect_hint


ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg"}
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def clean_text(text: str) -> str:
    text = re.sub(r"https?://\S+|www\.\S+", " ", text or "")
    lines = [ln.strip() for ln in (text or "").splitlines()]
    seen = set()
    cleaned = []
    for ln in lines:
        if not ln:
            continue
        key = ln.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(ln)
    return "\n".join(cleaned).strip()

_model = None
def get_model():
    global _model
    if _model is None:
        from app.model_infer import load_model as _load_model
        _model = _load_model()
    return _model

def read_pdf_text(pdf_path: str) -> str:
    import fitz
    doc = fitz.open(pdf_path)
    page_texts = []
    for page in doc:
        native = extract_text(pdf_path, page_numbers=[page.number]) or ""
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_path = f"{pdf_path}.page{page.number}.png"
        pix.save(img_path)
        try:
            ocr = ocr_image(img_path) or ""
        finally:
            try:
                os.remove(img_path)
            except Exception:
                pass
        combined = (native.strip() + "\n" + ocr.strip()).strip()
        if combined:
            page_texts.append(combined)
    full = "\n\n".join(page_texts).strip()
    return clean_text(full)

def read_email_text(file_storage) -> str:
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        raise ValueError("Formato de arquivo não suportado.")
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file_storage.save(path)
    ext = filename.rsplit(".", 1)[1].lower()
    if ext == "txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext == "pdf":
        return read_pdf_text(path)
    if ext in {"png", "jpg", "jpeg"}:
        return ocr_image(path) or ""
    return ""

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    email_text = ""
    email_text_render = ""
    error = None
    if request.method == "POST":
        try:
            model = get_model()
            text_source = None
            file = request.files.get("file")
            if file and file.filename:
                email_text = read_email_text(file)
                text_source = "file"
            else:
                raw_text = (request.form.get("email_text") or "").strip()
                if raw_text:
                    email_text = raw_text
                    text_source = "textarea"
                else:
                    error = "Envie um arquivo .txt/.pdf/.png/.jpg/.jpeg ou cole um texto."
            if not error and not (email_text and email_text.strip()):
                error = "Não foi possível extrair conteúdo de texto do arquivo enviado."
            if not error:
                pred = model.predict([email_text])[0]
                hint = detect_hint(email_text)
                if hint in ("urgent", "status", "attachment", "help"):
                    pred = "Produtivo"
                elif hint in ("promo", "thanks", "greetings"):
                    pred = "Improdutivo"
                reply = suggest_reply(pred, email_text)
                result = {"category": pred, "reply": reply}
                if text_source == "textarea":
                    email_text_render = email_text
                else:
                    email_text_render = ""
        except Exception as e:
            error = str(e)
    return render_template("index.html", result=result, email_text=email_text_render, error=error)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)

