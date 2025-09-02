import regex as re

_PT_STOP = {
    "a","o","os","as","de","da","do","das","dos","e","é","ser","que","em","um","uma","para","por","com","na","no","nas","nos",
    "ao","à","às","aos","se","sua","seu","suas","seus","não","sim","já","hoje","ontem","amanhã","mas","ou","também","foi","era",
    "está","estao","estavam","pode","podem","preciso","precisa","precisamos","precisam","favor","obrigado","obrigada","bom","boa",
    "dia","tarde","noite","olá","ola"
}

_EN_STOP = {
    "the","a","an","and","or","is","are","am","was","were","be","been","being","to","of","in","on","for","with","as","at","by",
    "this","that","these","those","i","you","he","she","it","we","they","me","my","your","our","their","from","hi","hello",
    "thanks","thank","please","good","morning","afternoon","evening","today","yesterday","tomorrow"
}

def normalize(text: str) -> str:
    if not text:
        return ""
    t = text.lower()
    t = re.sub(r"\p{Z}+", " ", t)
    t = re.sub(r"[\p{P}\p{S}]+", " ", t)
    t = re.sub(r"\d{2,}", " ", t)
    tokens = [w for w in t.split() if w not in _PT_STOP and w not in _EN_STOP]
    return " ".join(tokens)
