from unittest.mock import patch, Mock

import pytest
from requests.exceptions import RequestException, Timeout

from services.exceptions import PatientServiceError
from services.patient_service import PatientService


@pytest.fixture
def patient_service():
    return PatientService()

@patch("services.patient_service.requests.get")
def test_get_fake_patient_data_success(mock_get, patient_service):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "results": [
            {
                "name": {"first": "João", "last": "Silva"},
                "email": "joao.silva@example.com",
                "phone": "1234-5678"
            }
        ]
    }
    mock_get.return_value = mock_response

    result = patient_service.get_fake_patient_data()
    assert result["name"] == "João Silva"
    assert result["email"] == "joao.silva@example.com"
    assert result["phone"] == "1234-5678"

@patch("services.patient_service.requests.get", side_effect=Timeout)
def test_get_fake_patient_data_timeout(mock_get, patient_service):
    with pytest.raises(PatientServiceError, match="O serviço de pacientes demorou para responder."):
        patient_service.get_fake_patient_data()

@patch("services.patient_service.requests.get", side_effect=RequestException)
def test_get_fake_patient_data_request_exception(mock_get, patient_service):
    with pytest.raises(PatientServiceError, match="Erro ao consultar o serviço de pacientes."):
        patient_service.get_fake_patient_data()

@patch("services.patient_service.requests.get")
def test_get_fake_patient_data_invalid_json(mock_get, patient_service):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    # JSON sem a chave "results"
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    with pytest.raises(PatientServiceError, match="Resposta inválida do serviço de pacientes."):
        patient_service.get_fake_patient_data()