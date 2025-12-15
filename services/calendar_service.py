import datetime
import os
import shutil

import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

GOOGLE_CALENDAR_SCOPE = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        """Inicializa o serviço de calendário e autentica o usuário."""
        self.service = self._authenticate()

    def _authenticate(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')
        CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

        user_credentials = None

        os.makedirs(BASE_DIR, exist_ok=True)

        if os.path.exists(TOKEN_PATH) and os.path.isdir(TOKEN_PATH):
            print(f"⚠️ '{TOKEN_PATH}' é um diretório inválido. Removendo automaticamente...")
            shutil.rmtree(TOKEN_PATH)

        if os.path.isfile(TOKEN_PATH):
            try:
                user_credentials = Credentials.from_authorized_user_file(
                    TOKEN_PATH,
                    GOOGLE_CALENDAR_SCOPE
                )
            except Exception:
                print("⚠️ Token existente inválido ou corrompido. Recriando...")
                user_credentials = None

        if not user_credentials or not user_credentials.valid:
            if user_credentials and user_credentials.expired and user_credentials.refresh_token:
                user_credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH,
                    GOOGLE_CALENDAR_SCOPE
                )

                print("🔐  É necessária uma autenticação inicial. \nClique no link abaixo para conceder acesso ao Google Calendar da sua conta:")
                user_credentials = flow.run_local_server(
                    port=0,
                    open_browser=False
                )

            with open(TOKEN_PATH, "w", encoding="utf-8") as token:
                token.write(user_credentials.to_json())

        return build("calendar", "v3", credentials=user_credentials)

    # =========================
    # LEITURA DE EVENTOS
    # =========================
    def events_today(self):
        today = datetime.datetime.now(pytz.UTC)
        start = datetime.datetime.combine(today.date(), datetime.time(0, 0, 0, 0, tzinfo=today.tzinfo))
        end = datetime.datetime.combine(today.date(), datetime.time(23, 59, 59, 0, tzinfo=today.tzinfo))
        return self._get_events(start, end)

    def events_tomorrow(self):
        import datetime
        import pytz

        today = datetime.datetime.now(pytz.UTC)
        tomorrow_date = today.date() + datetime.timedelta(days=1)

        start = datetime.datetime.combine(tomorrow_date, datetime.time(0, 0, 0, 0, tzinfo=today.tzinfo))
        end = datetime.datetime.combine(tomorrow_date, datetime.time(23, 59, 59, 0, tzinfo=today.tzinfo))

        return self._get_events(start, end)

    def events_this_week(self):
        today = datetime.datetime.now(pytz.UTC)
        end = today + datetime.timedelta(days=7)
        return self._get_events(today, end)

    def events_this_month(self):
        today = datetime.datetime.now(pytz.UTC)
        end = today + datetime.timedelta(days=30)
        return self._get_events(today, end)

    def events_between(self, start, end):
        return self._get_events(start, end)

    def _get_events(self, start, end):
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        return events