from datetime import datetime

def format_event_time(start, end):
    """
    Formata data e horário do evento do Google Calendar
    de forma padronizada.
    """

    # Evento com horário definido
    if "dateTime" in start and "dateTime" in end:
        start_dt = datetime.fromisoformat(start["dateTime"])
        end_dt = datetime.fromisoformat(end["dateTime"])

        date_str = start_dt.strftime("%d/%m/%Y")
        time_str = f"{start_dt.strftime('%H:%M')} às {end_dt.strftime('%H:%M')}"

    # Evento de dia inteiro
    else:
        start_date = datetime.fromisoformat(start["date"])

        date_str = start_date.strftime("%d/%m/%Y")
        time_str = "00:00 às 23:59 (dia inteiro)"

    return date_str, time_str