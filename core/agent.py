from services import FeedbackService, LLMService, CalendarService, PatientService
from utils.calendar_formatter import format_event_time
from services.exceptions import FeedbackValidationError, LLMServiceError, PatientServiceError, ApplicationError

from vectorstore.faiss_store import VectorStore

class Agent:
    def __init__(self):
        self.feedback_service = FeedbackService()
        self.llm_service = LLMService(self.feedback_service)

        self.calendar_service = CalendarService()
        self.patient_service = PatientService()
        self.vector_store = VectorStore()

    def is_greeting(self, text: str) -> bool:
        greetings = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "hey", "hello"]
        return text.lower().strip() in greetings

    def run(self, question: str) -> str:
        if self.is_greeting(question):
            return (
                "Oi! Como posso te ajudar?\n\n"
                "Você pode me perguntar sobre suas consultas ou eventos, por exemplo:\n"
                "- Quais consultas tenho hoje?\n"
                "- Quais consultas tenho amanhã?\n"
                "- Quais consultas tenho esta semana?\n"
                "- Quais consultas tenho este mês?"
            )

        try:
            result = self.llm_service.classify_schedule_period(question)
            intent = result.get("periodo", "desconhecido").lower()
            motivo = result.get("motivo", "")

            if intent in ["mês", "mes"]:
                intent = "mes"
            elif intent in ["amanhã", "amanha"]:
                intent = "amanha"
            elif intent not in ["hoje", "amanha", "semana", "mes"]:
                intent = "desconhecido"

            if intent == "hoje":
                events = self.calendar_service.events_today()
            elif intent == "amanha":
                events = self.calendar_service.events_tomorrow()
            elif intent == "semana":
                events = self.calendar_service.events_this_week()
            elif intent == "mes":
                events = self.calendar_service.events_this_month()
            else:
                return (
                    "Desculpe, não consegui entender. "
                    f"{motivo}. "
                    "Você pode informar se deseja as consultas de hoje, amanhã, desta semana ou deste mês?"
                )

            if not events:
                return self._no_events_message(intent)

            patients = [self.patient_service.get_fake_patient_data() for _ in events]

            return self.format(events, patients)


        except LLMServiceError as e:
            msg = str(e).lower()
            if "api key" in msg or "quota" in msg:
                return "Erro: sua API Key está inválida ou acabou o limite de requisições."
            return "Não consegui entender sua solicitação agora. Tente reformular a pergunta."
        except PatientServiceError:
            return "Não foi possível obter os dados do paciente no momento. Tente novamente mais tarde."

    def _no_events_message(self, intent: str) -> str:
        period_map = {"hoje": "hoje", "semana": "esta semana", "mes": "este mês"}
        periodo_texto = period_map.get(intent, "o período informado")
        return f"Não encontrei consultas para {periodo_texto}. Deseja verificar outro período ou uma data diferente?"

    def receive_feedback(self, feedback: str):
        try:
            self.feedback_service.apply_feedback(feedback)
            return {"status": "ok"}
        except FeedbackValidationError as e:
            return {"status": "error", "message": str(e)}
        except ApplicationError:
            return {
                "status": "error",
                "message": "Não foi possível processar o feedback no momento."
            }

    def format(self, events, patients) -> str:
        result = "Encontrei estas consultas para você:\n"

        # Repete o último paciente se houver menos pacientes que eventos
        if len(patients) < len(events):
            patients += [patients[-1]] * (len(events) - len(patients))

        for event, patient in zip(events, patients):
            date_str, time_str = format_event_time(event["start"], event["end"])

            consult_type = self.vector_store.query_consult_type(event["summary"])
            if not consult_type:
                consult_type = "Tipo de consulta não identificado"

            result += (
                "-----------------------------  \n"
                f"Data: {date_str}  \n"
                f"Nome do evento: {event['summary']}  \n"
                f"Tipo: {consult_type}  \n"
                f"Horário: {time_str}  \n"
                f"Paciente: {patient['name']}  \n"
                f"Email do paciente: {patient['email']}  \n"
                f"Telefone do paciente: {patient['phone']}  \n"
                "-----------------------------  \n"
            )

        return result