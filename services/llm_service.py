import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class LLMService:

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def classify_schedule_period(self, question: str) -> str:
        """
        Classifica a pergunta do usuário em 'semana', 'mes' ou 'hoje', incluindo horários.
        Retorna 'desconhecido' se não for possível identificar.
        """

        prompt = f"""
        Você é um assistente médico virtual. 
        Classifique a pergunta do usuário em um destes períodos: semana, mes ou hoje.
        Responda apenas com uma palavra: 'semana', 'mes' ou 'hoje'.

        Exemplos:
        - "Quais consultas tenho esta semana?" -> semana
        - "Quais consultas tenho hoje?" -> hoje
        - "Quero saber minhas consultas de janeiro a dezembro" -> mes
        - "Liste minhas consultas de 1 a 7 de março" -> semana
        - "Quero minhas consultas de 09:00 até 12:00 de 15/12" -> hoje
        - "Quero minhas consultas de 14:00 até 16:00 de 20/12" -> hoje

        Observação: se o usuário informar horários, é necessário que o dia seja citado. Se não houver dia, retorne 'desconhecido'.

        Pergunta: "{question}"
        """

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        schedule_period = response.text.strip().lower()

        if schedule_period not in ["semana", "mes", "hoje"]:
            return "desconhecido"

        return schedule_period