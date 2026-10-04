import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import gradio as gr

load_dotenv()

SELLER_DATA = """
Seller Performance Data (Q3 2024):

| Seller        | Orders | Revenue   | Rating | Returns | Fulfillment |
|---------------|--------|-----------|--------|---------|-------------|
| TechGadgets   | 1,240  | $89,500   | 4.7    | 2.1%    | 98.2%       |
| FashionHub    | 3,100  | $145,200  | 4.3    | 8.4%    | 95.1%       |
| HomeDecorPlus | 780    | $62,300   | 4.8    | 1.2%    | 99.0%       |
| SportZone     | 2,050  | $112,400  | 4.1    | 5.7%    | 93.8%       |
| BookWorld     | 4,500  | $67,800   | 4.9    | 0.8%    | 99.5%       |

Metrics explanation:
- Returns: percentage of orders returned
- Fulfillment: on-time delivery rate
"""

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", f"You are a seller performance analyst. Use this data to answer questions:\n{SELLER_DATA}"),
    ("human", "{question}"),
])

chain = prompt | llm


def ask_agent(question: str) -> str:
    if not question.strip():
        return "Please enter a question."
    response = chain.invoke({"question": question})
    return response.content


demo = gr.Interface(
    fn=ask_agent,
    inputs=gr.Textbox(label="Ask about seller performance", placeholder="e.g. Who has the highest revenue?"),
    outputs=gr.Textbox(label="Answer"),
    title="SellerPulse Agent",
    description="Ask natural language questions about seller performance data.",
    examples=[
        ["Which seller has the best rating?"],
        ["Who has the lowest return rate?"],
        ["Compare fulfillment rates across all sellers."],
        ["Which seller should I be concerned about and why?"],
    ],
)

if __name__ == "__main__":
    demo.launch()