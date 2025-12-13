from agent.agent import Agent

if __name__ == "__main__":
    agent = Agent()

    questions = [
        "Quais consultas tenho esta semana?"
    ]

    for question in questions:
        print(f"Pergunta: {question}")
        print(agent.run(question))
        print("-" * 50)