from unittest.mock import MagicMock

import pytest

from core.agent import Agent
from services.exceptions import PatientServiceError, LLMServiceError


@pytest.fixture
def agent():
    agent = Agent()
    agent.llm_service.classify_schedule_period = MagicMock()
    agent.patient_service.get_fake_patient_data = MagicMock()
    agent.vector_store.query_consult_type = MagicMock()
    return agent


def mock_event(summary="Consulta Teste"):
    return {
        "summary": summary,
        "start": {"dateTime": "2025-12-14T10:00:00-03:00"},
        "end": {"dateTime": "2025-12-14T11:00:00-03:00"}
    }

def test_agent_returns_formatted_events(agent):
    agent.llm_service.classify_schedule_period.return_value = {"periodo": "semana", "motivo": ""}
    agent.calendar_service.events_this_week = MagicMock(return_value=[mock_event()])

    agent.patient_service.get_fake_patient_data.return_value = {
        "name": "João Silva",
        "email": "joao@example.com",
        "phone": "11999999999"
    }

    agent.vector_store.query_consult_type.return_value = "Consulta médica"

    result = agent.run("Quais consultas tenho esta semana?")

    assert "Nome do evento: Consulta Teste" in result
    assert "Paciente: João Silva" in result
    assert "Tipo: Consulta médica" in result


def test_agent_no_events_returns_message(agent):
    agent.llm_service.classify_schedule_period.return_value = {"periodo": "hoje", "motivo": ""}
    agent.calendar_service.events_today = MagicMock(return_value=[])

    result = agent.run("Quais consultas tenho hoje?")

    assert "Não encontrei consultas para hoje" in result


def test_agent_handle_patient_service_error(agent):
    agent.llm_service.classify_schedule_period.return_value = {"periodo": "semana", "motivo": ""}
    agent.calendar_service.events_this_week = MagicMock(return_value=[mock_event()])
    agent.patient_service.get_fake_patient_data.side_effect = PatientServiceError("Erro no serviço de pacientes")

    result = agent.run("Quais consultas tenho esta semana?")

    assert "Não foi possível obter os dados do paciente no momento" in result


def test_agent_handle_llm_service_error(agent):
    agent.llm_service.classify_schedule_period.side_effect = LLMServiceError("Erro LLM")

    result = agent.run("Quais consultas tenho esta semana?")

    assert "Não consegui entender sua solicitação agora" in result


def test_agent_unknown_period_returns_default_message(agent):
    agent.llm_service.classify_schedule_period.return_value = {"periodo": "desconhecido", "motivo": "não entendi"}

    result = agent.run("Pergunta estranha")

    assert "Desculpe, não consegui entender" in result
    assert "não entendi" in result
