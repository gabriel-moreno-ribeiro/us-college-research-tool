"""
Perfil do aluno — usado para filtrar e ordenar o relatório por relevância,
e para aplicar corretamente a lente de "quais dados se aplicam ao meu caso".

Contexto internacional é primeira classe: um aplicante brasileiro morando no
Brasil não é elegível a federal aid nem tem os mesmos números de custo ou
earnings que o Scorecard reporta. Sem essa informação, a ferramenta apresenta
números irrelevantes como se fossem o que o aluno vai pagar.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

PROFILE_PATH = Path(__file__).parent.parent / "data" / "student_profile.json"

CITIZENSHIP_STATUSES = {"us_citizen", "us_permanent_resident", "international"}


@dataclass
class StudentProfile:
    name: str = ""
    interests: list[str] = field(default_factory=list)
    goal: str = "research"  # "research" | "industry" | "entrepreneurship"

    # International-lens fields — critical for correct data interpretation
    citizenship_status: str = "us_citizen"  # us_citizen | us_permanent_resident | international
    country_of_residence: str = "US"  # ISO 3166 alpha-2 or plain country name
    requires_financial_aid: bool = False

    def __post_init__(self) -> None:
        if self.citizenship_status not in CITIZENSHIP_STATUSES:
            raise ValueError(
                f"citizenship_status must be one of {CITIZENSHIP_STATUSES}, "
                f"got {self.citizenship_status!r}"
            )

    def is_international(self) -> bool:
        """Convenience: is this student ineligible for US federal aid and
        subject to F-1 (or similar) visa constraints?"""
        return self.citizenship_status == "international"

    def interest_keywords(self) -> set[str]:
        """Extrai keywords normalizadas das áreas de interesse."""
        words: set[str] = set()
        for interest in self.interests:
            normalized = interest.lower().replace("-", " ")
            for word in normalized.split():
                if len(word) > 2:
                    words.add(word)
            words.add(normalized)
        return words

    def to_dict(self) -> dict:
        return asdict(self)


def load_saved_profile() -> StudentProfile | None:
    """Load the persisted profile from data/student_profile.json, if present."""
    if not PROFILE_PATH.exists():
        return None
    try:
        with open(PROFILE_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    # Only keep known fields (forward compatibility)
    known = {"name", "interests", "goal", "citizenship_status",
             "country_of_residence", "requires_financial_aid"}
    filtered = {k: v for k, v in data.items() if k in known}
    try:
        return StudentProfile(**filtered)
    except (TypeError, ValueError):
        return None


def save_profile(profile: StudentProfile) -> Path:
    """Persist a profile to data/student_profile.json. Overwrites any existing."""
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)
    return PROFILE_PATH


# Known abbreviations/synonyms for common CS areas
_SYNONYMS: dict[str, list[str]] = {
    "hci": ["human-computer interaction", "human computer interaction", "chi", "user interface", "user experience", "ubiquitous computing", "human factors"],
    "human-computer interaction": ["hci", "chi", "user interface", "ubiquitous computing", "human factors", "interactive systems"],
    "machine learning": ["ml", "deep learning", "neural network", "artificial intelligence"],
    "artificial intelligence": ["ai", "machine learning", "deep learning", "neural network"],
    "distributed systems": ["distributed computing", "cloud computing", "parallel computing"],
    "systems": ["operating systems", "distributed systems", "computer architecture"],
    "nlp": ["natural language processing", "computational linguistics", "language model"],
    "natural language processing": ["nlp", "computational linguistics", "language model"],
    "computer vision": ["image recognition", "object detection", "visual computing"],
    "robotics": ["autonomous systems", "robot", "manipulation", "motion planning"],
    "security": ["cybersecurity", "cryptography", "privacy", "network security"],
    "entrepreneurship": ["startup", "founder", "venture", "innovation"],
    # New — added because Northwestern deep-dive uncovered gaps
    "embedded systems": ["embedded", "iot", "internet of things", "sensor", "microcontroller",
                         "wearable", "batteryless", "ubiquitous", "firmware"],
    "computer architecture": ["architecture", "processor", "microarchitecture", "cpu",
                              "gpu", "cache", "vlsi", "chip", "silicon"],
    "hardware": ["fpga", "asic", "vlsi", "circuit", "chip", "silicon", "processor"],
}


def compute_relevance_score(
    professor_text: str,
    profile: StudentProfile,
) -> float:
    """
    Score de relevância baseado em overlap de palavras-chave + sinônimos.
    Retorna um float entre 0 e 1.
    """
    if not profile.interests:
        return 0.0

    text_lower = professor_text.lower().replace("-", " ")
    text_words = set(re.split(r'\W+', text_lower))

    points = 0.0
    max_points = 0.0

    for interest in profile.interests:
        interest_norm = interest.lower().replace("-", " ")
        max_points += 5.0

        # Full phrase match (strongest signal)
        if interest_norm in text_lower:
            points += 5.0
            continue

        # Check synonyms
        synonyms = _SYNONYMS.get(interest_norm, [])
        synonym_match = False
        for syn in synonyms:
            if syn in text_lower or syn in text_words:
                points += 4.0
                synonym_match = True
                break

        if synonym_match:
            continue

        # Individual word matches
        interest_words = [w for w in interest_norm.split() if len(w) > 2]
        if interest_words:
            word_hits = sum(1 for w in interest_words if w in text_words)
            points += (word_hits / len(interest_words)) * 3.0

    return min(points / max(max_points, 1.0), 1.0)
