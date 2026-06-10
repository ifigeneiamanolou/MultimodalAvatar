import os
from openai import OpenAI
from dotenv import load_dotenv

# https://dev.to/abhinowww/how-to-build-a-simple-chatbot-in-python-using-openai-step-by-step-guide-hfg

load_dotenv()
KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(
    api_key = KEY
)

def generate_response(user_input):
    response = client.responses.create(
        model = "gpt-5.5-nano",
        input = user_input
    )
    return response.output_text



def start_chatbot():
    print("Welcome to the avatar, type exit to stop.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("End of the conversation.")
            break

        response = generate_response(user_input)
        print(f"\n Bot : {response} \n")

if __name__ == "__main__":
    start_chatbot()