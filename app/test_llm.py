from app.services.llm import generate_answer

prompt = "Explain artificial intelligence in 3 simple lines."

answer = generate_answer(prompt)

print("AI ANSWER:")
print(answer)