import os
import joblib
import regex as re
from typing import Optional

NLP_RULES = {
    "hints": {
        "urgent": [
            re.compile(r"\burgente\b", re.I),
            re.compile(r"\burgent\b", re.I),
            re.compile(r"^\s*URGENTE\s*$", re.I | re.M),
        ],
        "promo": [
            re.compile(r"\b(desinscrever|unsubscribe|descadastre|pare de receber)\b", re.I),
            re.compile(r"\b(oferta|promo(ção|\b)|desconto|compre|aproveite|benefícios?)\b", re.I),
            re.compile(r"\b(cr[eé]dito|peça agora|pedir cart[aã]o|solicite agora)\b", re.I),
            re.compile(r"\b(clique aqui|bot[aã]o|aproveitar agora|peça j[aá])\b", re.I),
        ],

        "status": [
            re.compile(r"\bstatus\b", re.I),
            re.compile(r"\batualiza(?:ç|c)ões?\b", re.I),
            re.compile(r"\batualiza(?:r|ndo|ção)\b", re.I),
            re.compile(r"\bandamento\b", re.I),
            re.compile(r"\bprevis(?:ão|ao|ões)\b", re.I),
            re.compile(r"\bprazo[s]?\b", re.I),
        ],

        "attachment": [
            re.compile(r"\banexos?\b", re.I),
            re.compile(r"\bsegue(?:m)?\s+em\s+anexo\b", re.I),
            re.compile(r"\bem\s+anexo\b", re.I),
            re.compile(r"\banexei\b|\banexando\b", re.I),
        ],

        "help": [
            re.compile(r"\b(preciso|necessito)\s+de\s+ajuda\b", re.I),
            re.compile(r"\bestou\s+com\s+(um\s+)?problema?s?\b", re.I),
            re.compile(r"\bestou\s+com\s+dificuldades?\b", re.I),
            re.compile(r"\bsuporte(\s+t[eé]cnico)?\b|\bhelp\b|\bsupport\b", re.I),
            re.compile(r"\bpoderiam?\s+ajudar\b|\bpreciso\s+de\s+suporte\b", re.I),
        ],

        "thanks": [
            re.compile(r"\bobrigad[oa]s?\b", re.I),
            re.compile(r"\bagradeciment[oa]s?\b|\bagrade[çc]o\b|\bagradeceria\b", re.I),
            re.compile(r"\bvaleu\b", re.I),
            re.compile(r"\bgrat[oa]\b", re.I),
        ],

        "greetings": [
            re.compile(r"\b(feliz\s+natal|boas\s+festas|feliz\s+ano\s+novo)\b", re.I),
            re.compile(r"\bparab[eé]ns\b", re.I),
        ],
    },
    "priority": ["urgent", "promo", "status", "attachment", "help", "thanks", "greetings"],
}

here = os.path.dirname(__file__)
root = os.path.abspath(os.path.join(here, ".."))
MODEL_PATH = os.path.join(root, "app", "model", "pipeline.joblib")

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not found. Run: python app/model_train.py")
    return joblib.load(MODEL_PATH)

def _strip_urls(text: str) -> str:
    return re.sub(r"https?://\S+|www\.\S+", " ", text or "")

def detect_hint(text: str) -> Optional[str]:
    t = (_strip_urls(text) or "").lower()
    for key in NLP_RULES["priority"]:
        for pattern in NLP_RULES["hints"].get(key, []):
            if pattern.search(t):
                return key
    return None

def suggest_reply(category: str, email_text: str) -> str:
    hint = detect_hint(email_text) or ""
    if hint == "urgent":
        category = "Produtivo"
        return (
            "Recebemos sua mensagem marcada como URGENTE. "
            "Priorizaremos o atendimento e retornaremos o contato o mais breve possível. "
        )
    if hint == "promo":
        category = "Improdutivo"
        return "E-mail promocional. Nenhuma ação é necessária."
    if hint in ("thanks", "greetings"):
        category = "Improdutivo"
        return "Mensagem de cortesia! Nenhuma ação é necessária."
    if category == "Improdutivo":
        return "Mensagem improdutiva, sem necessidade de resposta."

    if category == "Produtivo":
        if hint == "help":
            return (
                "Olá! Recebemos sua solicitação de suporte. "
                "Nossa equipe está verificando e entraremos em contato em breve."
            )
        if hint == "status":
            return (
                "Olá! Recebemos sua solicitação de status. "
                "Nossa equipe está verificando e retornaremos com uma atualização em breve."
            )
        if hint == "attachment":
            return (
                "Olá! Confirmamos o recebimento do anexo. "
                "Vamos validar o conteúdo e retornamos com os próximos passos em breve."
        )
        return (
            "Olá! Sua mensagem foi recebida. "
            "Em breve retornaremos com uma resposta."
        )
