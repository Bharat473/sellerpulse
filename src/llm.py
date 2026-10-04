"""The only file that talks to the LLM provider. Change the model or provider here."""
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
MODEL = "openai/gpt-oss-120b"  # "openai/gpt-oss-20b" is faster and lighter


def get_llm():
    return ChatGroq(model=MODEL, api_key=os.getenv("GROQ_API_KEY"), temperature=0)
