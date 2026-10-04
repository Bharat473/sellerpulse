"""SellerPulse agent, Week 1: answers from buyer reviews, listings and policy (RAG, Task 10).
Sales and stock figures arrive with tools in Week 2.

Terminal:  uv run python agent.py "Why is my Boho Wall Hanging listing underperforming?"
Browser:   uv run python agent.py            (add --share for a temporary public link)
"""
import sys
from datetime import date
from pathlib import Path

import gradio as gr
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.llm import get_llm
from src.retrieval import retrieve

SELLER_ID = "S001"
SELLER_NAME = "Meera Iyer"
STORE_NAME = "Meera Home Studio"
TODAY = date(2026, 9, 16)  # fixed so "last week" matches the synthetic data window
SYSTEM_PROMPT = Path("src/prompts/system.md").read_text()

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Shop data:\n{context}\n\nQuestion: {question}"),
])
chain = prompt | get_llm() | StrOutputParser()


def get_context(question: str) -> str:
    _, hits = retrieve(question, SELLER_ID)
    if not hits:
        return "(no matching shop data)"
    return "\n\n".join(f"[{doc.metadata['id']}] {doc.page_content}" for doc, _ in hits)


def ask_agent(question: str) -> str:
    if not question.strip():
        return "Please enter a question."
    try:
        return chain.invoke({
            "context": get_context(question),
            "question": question,
            "seller_name": SELLER_NAME,
            "store_name": STORE_NAME,
            "today": TODAY.strftime("%A %d %B %Y"),
        })
    except Exception as err:  # e.g. a stray tool call or a rate limit from Groq
        print(f"Agent error: {err}")
        return "Sorry, I couldn't answer that just now. Please try again in a moment."


def chat(message, history):  # history is shown on screen only; memory arrives in Week 2
    return ask_agent(message)


demo = gr.ChatInterface(
    fn=chat,
    title="SellerPulse",
    description=f"Hi {SELLER_NAME}! Ask about your {STORE_NAME} listings, reviews and Setukart policy. "
                "Each question is answered on its own; sales and stock figures are coming soon.",
    examples=[
        "Why is my Boho Wall Hanging listing underperforming?",
        "Can I offer buyers a free gift for leaving a 5-star review?",
        "How did my sales perform last week?",
        "Draft a reply to this 3-star review: 'Cute but smaller than expected for the price.'",
    ],
)

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] != "--share":
        question = " ".join(args)
        print(f"QUESTION\n{question}\n\nSHOP DATA SENT TO THE LLM\n{get_context(question)}\n")
        print(f"ANSWER\n{ask_agent(question)}")
    else:
        demo.launch(share="--share" in args)
