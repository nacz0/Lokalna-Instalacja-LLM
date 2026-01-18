import re

class Moderator:
    def __init__(self):
        # Rozszerzona lista zakazanych słów (przykładowa)
        self.banned_words = {
            "violence": ["zabij", "morderstwo", "bomba", "terror", "broń", "pistolet", "ataki"],
            "hacking": ["hack", "exploit", "sql injection", "phishing", "malware", "wirus"],
            "hate": ["nienawiść", "rasizm", "dyskryminacja"],
            "sensitive": ["hasło", "klucz prywatny", "ssn", "pesel"]
        }
        
        # Regex dla danych wrażliwych
        self.pii_patterns = [
            r"\b\d{11}\b", # PESEL (bardzo uproszczony)
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", # Email
            r"\b(?:\+48\s?)?\d{9}\b", # Telefon (PL)
        ]
        
        # Heurystyka jailbreak
        self.jailbreak_patterns = [
            r"ignore all previous instructions",
            r"pomijaj wszystkie poprzednie polecenia",
            r"you are now in developer mode",
            r"jesteś teraz w trybie dewelopera",
            r"stay out of character",
            r"unfiltered",
            r"dan mode"
        ]

    def check_message(self, message: str) -> dict:
        """Przeprowadza dogłębną moderację wiadomości."""
        msg_lower = message.lower()
        
        # 1. Sprawdzanie słów zakazanych
        for category, words in self.banned_words.items():
            for word in words:
                if word in msg_lower:
                    return {"safe": False, "reason": f"Wykryto słowo naruszające zasady ({category}): '{word}'"}
        
        # 2. Sprawdzanie danych wrażliwych (PII)
        for pattern in self.pii_patterns:
            if re.search(pattern, message):
                return {"safe": False, "reason": "Wykryto potencjalne dane osobowe lub wrażliwe."}
                
        # 3. Sprawdzanie prób jailbreaka
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, msg_lower):
                return {"safe": False, "reason": "Wykryto próbę manipulacji modelem (jailbreak)."}
                
        return {"safe": True, "reason": None}

    def get_safe_mode_system_prompt(self) -> str:
        """Zwraca system prompt dla trybu bezpiecznego."""
        return (
            "You are a safe, helpful, and friendly AI assistant. "
            "You strictly follow safety guidelines. Do not generate content related to violence, "
            "illegal acts, or hate speech. Always be polite and professional."
        )
