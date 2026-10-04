"""SellerPulse agent, Week 1: system prompt only. Reviews and policy arrive with RAG
(Tasks 7-10); sales and stock figures arrive with tools (Week 2)."""
from datetime import date
from pathlib import Path

import gradio as gr
from langchain_core.prompts import ChatPromptTemplate

from src.llm import get_llm

SELLER_NAME = "Meera Iyer"
STORE_NAME = "Meera Home Studio"
TODAY = date(2026, 9, 16)  # fixed so "last week" matches the synthetic data window
SYSTEM_PROMPT = Path("src/prompts/system.md").read_text()

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}"),
])
chain = prompt | get_llm()


def ask_agent(question: str) -> str:
    if not question.strip():
        return "Please enter a question."
    try:
        response = chain.invoke({
            "question": question,
            "seller_name": SELLER_NAME,
            "store_name": STORE_NAME,
            "today": TODAY.strftime("%A %d %B %Y"),
        })
    except Exception as err:  # e.g. a stray tool call or a rate limit from Groq
        print(f"LLM error: {err}")
        return "Sorry, I couldn't answer that just now. Please try again in a moment."
    return response.content


demo = gr.Interface(
    fn=ask_agent,
    inputs=gr.Textbox(label="Ask about your shop", placeholder="e.g. How did my sales perform last week?"),
    outputs=gr.Textbox(label="Answer"),
    title="SellerPulse",
    description="Ask questions about your Setukart shop.",
    examples=[
        ["How did my sales perform last week?"],
        ["Draft a reply to this 2-star review: 'Nice rug but delivery took almost 3 weeks.'"],
        ["Can you offer buyers a free gift for leaving a 5-star review?"],
        ["How is my throw doing?"],
    ],
)

if __name__ == "__main__":
    demo.launch()
