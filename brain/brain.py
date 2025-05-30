from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
# from pydantic import SecretStr

from dotenv import load_dotenv  
import os

load_dotenv()

OPENAI_API_KEY = str(os.getenv("OPENAI_API_KEY"))

# Define the prompt template
prompt = PromptTemplate(
    input_variables=["candidate_response"],
    template=(
        "You are an AI interviewer. Based on the candidate's response:\n\n"
        "\"{candidate_response}\"\n\n"
        "Ask a relevant follow-up question."
    ),
)

# Initialize the language model
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    timeout=None,
    max_retries=2,
    api_key=OPENAI_API_KEY
)

# Set up the output parser
output_parser = StrOutputParser()

# Create the chain using RunnableSequence
chain = RunnableSequence(prompt, llm, output_parser)

# Example candidate response
candidate_input = {
    # "candidate_response": "I have five years of experience in software development, primarily working with Python and JavaScript."
}

# Invoke the chain
# follow_up_question = chain.invoke(candidate_input)

def askGPT(transcription):
    candidate_input['candidate_response'] = transcription
    response = chain.invoke(candidate_input)
    return response







