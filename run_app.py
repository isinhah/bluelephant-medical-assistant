import subprocess

from dotenv import load_dotenv

from services.calendar_service import CalendarService

load_dotenv()

def check_requirements():
    try:
        import streamlit
        import google_auth_oauthlib
        import googleapiclient
        print("✅ Todas as dependências estão instaladas.")
    except ModuleNotFoundError as e:
        print(f"⚠️ Dependência não encontrada: {e.name}")
        print("Execute: pip install -r requirements.txt")
        exit(1)

def run_streamlit():
    print("\n🚀 Iniciando interface Streamlit...")
    print("Abra seu navegador em: http://localhost:8501\n")
    try:
        subprocess.run(["streamlit", "run", "app.py"])
    except FileNotFoundError:
        print("❌ Streamlit não encontrado. Instale com: pip install streamlit")
        exit(1)

def main():
    check_requirements()

    print("🔐 Verificando autenticação do Google Calendar...")
    calendar_service = CalendarService()
    print("✅ Autenticação concluída.")

    run_streamlit()

if __name__ == "__main__":
    main()