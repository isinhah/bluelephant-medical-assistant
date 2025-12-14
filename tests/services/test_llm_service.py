from unittest.mock import Mock, patch

import pytest

from services.exceptions import LLMServiceError
from services.feedback_service import FeedbackService
from services.llm_service import LLMService


@pytest.fixture
def feedback_service():
    return FeedbackService()

@pytest.fixture
def llm_service(feedback_service):
    return LLMService(feedback_service)

def test_init_without_api_key(monkeypatch, feedback_service):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(LLMServiceError, match="API Key do Gemini não configurada."):
        LLMService(feedback_service)

def test_classify_schedule_period_empty_question(llm_service):
    with pytest.raises(LLMServiceError, match="Pergunta do usuário vazia."):
        llm_service.classify_schedule_period("  ")

@patch("services.llm_service.genai.Client")
def test_classify_schedule_period_success(mock_genai_client_class, feedback_service):
    mock_client = Mock()
    mock_response = Mock()
    mock_response.text = '{"periodo": "hoje", "motivo": ""}'
    mock_client.models.generate_content.return_value = mock_response
    mock_genai_client_class.return_value = mock_client

    service = LLMService(feedback_service)
    service.client = mock_client

    result = service.classify_schedule_period("Quais consultas tenho hoje?")
    assert result["periodo"] == "hoje"
    assert result["motivo"] == ""

@patch("services.llm_service.genai.Client")
def test_classify_schedule_period_invalid_json(mock_genai_client_class, feedback_service):
    mock_client = Mock()
    mock_response = Mock()
    mock_response.text = 'Resposta inválida sem JSON'
    mock_client.models.generate_content.return_value = mock_response
    mock_genai_client_class.return_value = mock_client

    service = LLMService(feedback_service)
    service.client = mock_client

    with pytest.raises(LLMServiceError, match="Resposta do modelo não contém um JSON válido."):
        service.classify_schedule_period("Quais consultas tenho hoje?")