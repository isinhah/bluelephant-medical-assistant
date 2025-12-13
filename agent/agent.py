from services.calendar_formatter import format_event_time
from services.calendar_service import CalendarService
from services.llm_service import LLMService
from services.patient_service import PatientService

class Agent:
    def __init__(self):
        self.llm_service = LLMService()
        self.calendar_service = CalendarService()
        self.patient_service = PatientService()

    def run(self, question: str) -> str:
        intent = self.llm_service.classify_schedule_period(question)

        if intent == "semana":
            events = self.calendar_service.events_this_week()
        elif intent == "mes":
            events = self.calendar_service.events_this_month()
        elif intent == "hoje":
            events = self.calendar_service.events_today()
        else:
            return "Não entendi o período."

        patients = self.patient_service.get_fake_patient_data()
        return self._format(events, patients)

    def _format(self, events, patients) -> str:
        result = "------ SEUS EVENTOS ------\n"

        if len(patients) < len(events):
            # Repete o último paciente se houver menos pacientes que eventos
            patients += [patients[-1]] * (len(events) - len(patients))

        for event, patient in zip(events, patients):
            date_str, time_str = format_event_time(event["start"], event["end"])
            result += f"- {event['summary']} em {date_str} às {time_str} | Paciente: {patient['name']}, {patient['email']} ({patient['phone']})\n"

        return result