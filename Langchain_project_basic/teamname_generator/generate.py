from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

def generator_team_name(game_name, language):
    llm = OpenAI(temperature=0.8)

    prompt_template_name = PromptTemplate(
        input_variables=["game_name", 'language'],
        template="I have an Esports Team that plays in {game_name} competitions. I want a cool name for it. Give me 5 recommended names for my team in {language}."
    )

    sequence = prompt_template_name | llm
    response = sequence.invoke({"game_name": game_name, "language": language})

    return response

if __name__ == "__main__":
    team_names = generator_team_name("Valorant", "english")
    print(team_names)
