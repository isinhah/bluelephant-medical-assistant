import re as regex
from datetime import datetime
from typing import List, Dict

from services.exceptions import FeedbackValidationError

class FeedbackService:
    MIN_LENGTH = 5
    MAX_LENGTH = 300

    BLOCKED_PATTERNS = [
        r"ignore.*instru",
        r"desconsidere.*sistema",
        r"mude o prompt",
        r"altere o prompt",
        r"system prompt",
        r"prompt do sistema",
        r"execute código",
        r"apague",
        r"delete"
    ]

    def __init__(self):
        self.current_version = 1
        self.feedbacks: List[Dict] = []

        self.current_prompt = (
            "Você é um assistente médico virtual. "
            "Seja claro, educado e objetivo."
        )

        self.prompt_versions: List[Dict] = []

        self._save_prompt_version("v1 - prompt inicial")

    # =========================
    # GUARDRAILS
    # =========================
    def _validate_feedback(self, feedback: str):
        if not feedback or not feedback.strip():
            raise FeedbackValidationError("O feedback não pode estar vazio.")

        feedback = feedback.strip()

        if len(feedback) < self.MIN_LENGTH:
            raise FeedbackValidationError(
                f"O feedback deve ter pelo menos {self.MIN_LENGTH} caracteres."
            )

        if len(feedback) > self.MAX_LENGTH:
            raise FeedbackValidationError(
                f"O feedback deve ter no máximo {self.MAX_LENGTH} caracteres."
            )

        for pattern in self.BLOCKED_PATTERNS:
            if regex.search(pattern, feedback.lower()):
                raise FeedbackValidationError(
                    "Esse feedback contém instruções não permitidas."
                )

    # =========================
    # FEEDBACK
    # =========================
    def apply_feedback(self, feedback: str):
        self._validate_feedback(feedback)

        feedback = feedback.lower()

        if regex.search(r"\bcurt[oa]s?\b", feedback):
            self.update_prompt(
                new_instruction="Responda de forma mais curta e direta.",
                description="v2 - respostas mais curtas"
            )

        if regex.search(r"\beducad[oa]s?\b", feedback):
            self.update_prompt(
                new_instruction="Use sempre um tom educado e acolhedor.",
                description="v3 - tom mais humano"
            )

    # =========================
    # VERSIONAMENTO DO PROMPT
    # =========================
    def _save_prompt_version(self, description: str):
        self.prompt_versions.append({
            "version": f"v{self.current_version}",
            "description": description,
            "prompt": self.current_prompt,
            "timestamp": datetime.now().isoformat()
        })

    def update_prompt(self, new_instruction: str, description: str):
        self.current_version += 1

        self.current_prompt += f"\n{new_instruction}"

        self._save_prompt_version(description)

    # =========================
    # FUNÇÕES PARA UI
    # =========================
    def get_current_prompt(self) -> str:
        return self.current_prompt

    def get_prompt_history(self) -> List[Dict]:
        return self.prompt_versions