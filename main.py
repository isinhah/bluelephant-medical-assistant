from agent.agent import Agent

if __name__ == "__main__":
    agent = Agent()

    questions = [
        "Quais consultas tenho esta semana?",
        "Quero saber minhas consultas de janeiro a dezembro",
        "Quero minhas consultas de 09:00 até 12:00 de 15/12"
    ]

    for question in questions:
        print(f"Pergunta: {question}")
        print(agent.run(question))
        print("-" * 50)