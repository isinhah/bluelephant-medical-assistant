import streamlit as st

from core.agent import Agent
from services import PatientService


class App:
    def __init__(self):
        self.agent = Agent()
        self.feedback_service = self.agent.feedback_service
        self.patient_service = PatientService()

    def run(self):
        st.set_page_config(page_title="Assistente Médico", page_icon="🩺", layout="wide")
        st.header("🦾 Assistente Inteligente de Agenda Médica")
        st.caption("Estou aqui para te relembrar de seus compromissos e consultas!")

        st.caption(
            "💡 Exemplos de perguntas que você pode fazer:\n"
            "- Quais consultas tenho hoje?\n"
            "- Quais consultas tenho esta semana?\n"
            "- Quais consultas tenho este mês?\n"
        )

        tab_chat, tab_feedback = st.tabs(["💬 Chat com o Assistente", "📊 Dê seu Feedback!"])

        with tab_chat:
            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Olá, como posso te ajudar hoje?"}]

            chat_container = st.container()
            user_input = st.chat_input("Digite sua pergunta:")

            for msg in st.session_state.messages:
                with chat_container:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(user_input)

                response = self.agent.run(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(response)

                st.rerun()

        with tab_feedback:
            st.subheader("Envie seu feedback sobre a última resposta do bot")
            user_feedback = st.text_area("Comentário:")

            if st.button("Enviar feedback"):
                try:
                    self.agent.receive_feedback(user_feedback)
                    st.success("Obrigado pelo feedback! 😁")
                except Exception as e:
                    st.error(f"Não foi possível registrar o feedback: {str(e)}")

            st.markdown("### 🧠 Prompt atual do agente")
            st.code(self.feedback_service.get_current_prompt())

            st.markdown("### 📜 Histórico de versões do prompt")
            for version in self.feedback_service.get_prompt_history():
                with st.expander(f"{version['timestamp']} -- {version['description']}"):
                    st.code(version["prompt"])

        st.markdown("---")
        st.caption(
            "🔗 [GitHub](https://github.com/isinhah/bluelephant-medical-assistant) | "
            "💻 [LinkedIn](https://www.linkedin.com/in/isabel-henrique/)"
        )
        st.caption(
            "📌 Esta aplicação utiliza Google Calendar para retornar eventos. "
            "Todos os dados de pacientes são falsos, via API RandomUser."
        )

if __name__ == "__main__":
    App().run()