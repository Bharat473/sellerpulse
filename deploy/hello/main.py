"""Hello-world chatbot to practise deploying on Railway (step 5a). Not SellerPulse: no data, one model call.

Local test from the repo root:
  APP_PASSWORD=test uv run --env-file .env python deploy/hello/main.py
"""
import os

import gradio as gr
from langchain_groq import ChatGroq  # reads GROQ_API_KEY from the environment

LLM = ChatGroq(model="openai/gpt-oss-20b", temperature=0, max_tokens=1000)  # works on your account


def reply(message, history):
    return LLM.invoke([("system", "You are a friendly test bot. Answer in one or two sentences."),
                       ("human", message)]).content


gr.ChatInterface(fn=reply, title="Hello from Railway").launch(
    server_name="0.0.0.0",                              # listen on all interfaces, not only this machine
    server_port=int(os.environ.get("PORT", 7860)),      # Railway tells the app which port to use
    auth=("demo", os.environ["APP_PASSWORD"]),          # login: user "demo" + password from a Railway variable
)
