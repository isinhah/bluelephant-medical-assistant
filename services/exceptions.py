class ApplicationError(Exception):
    """Erro base da aplicação."""

class CalendarServiceError(ApplicationError):
    """Erro relacionado ao serviço de calendário."""
    pass

class PatientServiceError(ApplicationError):
    """Erro ao acessar o serviço de pacientes."""
    pass

class LLMServiceError(ApplicationError):
    """Erro ao se comunicar ou interpretar resposta da LLM."""
    pass

class FeedbackValidationError(ApplicationError):
    """Erro de validação de feedback do usuário."""
    pass