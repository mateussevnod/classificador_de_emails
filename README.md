Uma aplicação web simples (Flask + scikit-learn) que:
- Classifica emails em "Produtivo" ou "Improdutivo" (PT/EN).
- Sugere respostas automáticas baseadas no conteúdo.
- Aceita upload ou texto colado.
- Inclui modelo treinável (TF‑IDF + Logistic Regression) e um dataset de exemplo.


Demo local com Docker
```
docker build -t classificador-emails .
docker run --rm -p 8080:8080 classificador-emails
```
Acesse em: http://localhost:8080


Demo local

1- Instalar dependências:
```
sudo dnf install -y python3.11 python3.11-devel
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
No Fedora:
(para outros sistemas operacionais, usar o gerenciador de pacotes equivalente)
```
sudo dnf install -y tesseract tesseract-langpack-eng tesseract-langpack-por 
```

2- Treinar o modelo:
```
python app/model_train.py
```

3- Rodar a aplicação
```
python app/app.py
```
Acesse em: http://localhost:7860

    
Como funciona (resumo técnico):
- Pré-processamento leve (normalização + remoção de stopwords PT/EN).
- Vetorização `TfidfVectorizer` com n-gramas (1–2).
- Classificador `LogisticRegression`.
- Regras simples para sugerir respostas com base em palavras‑chave (status, help, attachment, urgent, promo, greetings/thanks).
- Parser de PDF com `pdfminer.six`.

OCR de imagens e PDF
- Suporte a .png/.jpg/.jpeg (OCR via Tesseract).
- Para PDFs: tenta extrair texto; se vier pouco texto, faz fallback para OCR renderizando as páginas via PyMuPDF.
- Parser de PDF com `pdfminer.six` (texto nativo) e `PyMuPDF` (OCR por página).
