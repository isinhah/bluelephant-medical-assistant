import json
import os
from typing import Dict, Any

import regex
from dotenv import load_dotenv
from google import genai

from services import FeedbackService
from services.exceptions import LLMServiceError

load_dotenv()

class LLMService:
    def __init__(self, feedback_service: FeedbackService):
        self.feedback_service = feedback_service
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise LLMServiceError("API Key do Gemini não configurada.")
        self.client = genai.Client(api_key=api_key)

    def classify_schedule_period(self, question: str) -> Dict[str, Any]:
        if not question or not question.strip():
            raise LLMServiceError("Pergunta do usuário vazia.")

        prompt = f"""

                ---
                Você é um assistente médico. Sua tarefa é identificar o período solicitado pelo usuário.

                Retorne SOMENTE o JSON no formato:
                {{
                  "periodo": "hoje" | "amanha" | "semana" | "mes" | "desconhecido",
                  "motivo": "explique brevemente se for desconhecido"
                }}

                Regras:
                - Se o usuário mencionar horários, o dia deve ser informado.
                - "hoje" para qualquer menção de data específica de hoje.
                - "amanha" para qualquer menção a "amanhã", "amanha", "dia seguinte".
                - "semana" para qualquer menção de intervalo de 7 dias ou "esta semana", "próxima semana".
                - "mes" para qualquer menção do mês atual.

                Exemplos:
                
                Usuário: "Quais consultas tenho hoje?"
                Resposta: {{ "periodo": "hoje", "motivo": "" }}
                
                Usuário: "Quais consultas tenho amanhã?"
                Resposta: {{ "periodo": "amanha", "motivo": "" }}

                Usuário: "Quais consultas tenho esta semana?"
                Resposta: {{ "periodo": "semana", "motivo": "" }}

                Usuário: "Quais consultas tenho este mês?"
                Resposta: {{ "periodo": "mes", "motivo": "" }}

                Pergunta do usuário: "{question}"
                """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
        except Exception as e:
            raise LLMServiceError(
                "Erro ao consultar o modelo de linguagem."
            ) from e

        try:
            data = self._extract_json(response.text)
        except LLMServiceError:
            raise
        except Exception as e:
            raise LLMServiceError(
                "Falha inesperada ao processar resposta do modelo."
            ) from e

        if "periodo" not in data:
            raise LLMServiceError(
                "Resposta da LLM não contém o campo 'periodo'."
            )

        return {
            "periodo": data.get("periodo", "desconhecido"),
            "motivo": data.get("motivo", "")
        }

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            match = regex.search(r"\{(?:[^{}]|(?R))*\}", text)
            if not match:
                raise LLMServiceError("Resposta do modelo não contém um JSON válido.")
            data = json.loads(match.group())

            periodo = data.get("periodo", "desconhecido").lower()
            if periodo in ["mês", "mes"]:
                data["periodo"] = "mes"
            elif periodo not in ["hoje", "amanha", "semana", "mes"]:
                data["periodo"] = "desconhecido"

            return data
        except json.JSONDecodeError as e:
            raise LLMServiceError("Erro ao interpretar o JSON retornado pelo modelo.") from e
