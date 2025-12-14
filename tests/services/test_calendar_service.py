import datetime
import pytest
import pytz

from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError

from services.calendar_service import CalendarService
from services.exceptions import CalendarServiceError

@patch("services.calendar_service.CalendarService._authenticate")
def test_calendar_service_init_success(mock_authenticate):
    mock_authenticate.return_value = MagicMock()

    service = CalendarService()

    assert service.service is not None
    mock_authenticate.assert_called_once()

@patch("services.calendar_service.CalendarService._authenticate")
def test_calendar_service_init_failure(mock_authenticate):
    mock_authenticate.side_effect = Exception("Auth error")

    with pytest.raises(CalendarServiceError):
        CalendarService()

def test_get_events_success():
    service = CalendarService.__new__(CalendarService)

    mock_events = {
        "items": [
            {"summary": "Consulta Cardiologia"},
            {"summary": "Consulta Dermatologia"}
        ]
    }

    mock_execute = MagicMock(return_value=mock_events)
    mock_list = MagicMock(return_value=MagicMock(execute=mock_execute))
    service.service = MagicMock(events=MagicMock(return_value=MagicMock(list=mock_list)))

    start = datetime.datetime.now(pytz.UTC)
    end = start + datetime.timedelta(days=1)

    events = service._get_events(start, end)

    assert len(events) == 2
    assert events[0]["summary"] == "Consulta Cardiologia"

def test_get_events_http_error():
    service = CalendarService.__new__(CalendarService)

    http_error = HttpError(resp=MagicMock(status=500), content=b"Error")

    mock_execute = MagicMock(side_effect=http_error)
    mock_list = MagicMock(return_value=MagicMock(execute=mock_execute))
    service.service = MagicMock(events=MagicMock(return_value=MagicMock(list=mock_list)))

    start = datetime.datetime.now(pytz.UTC)
    end = start + datetime.timedelta(days=1)

    with pytest.raises(CalendarServiceError):
        service._get_events(start, end)
