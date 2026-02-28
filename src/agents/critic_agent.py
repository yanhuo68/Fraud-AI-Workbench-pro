# agents/critic_agent.py
from typing import Sequence, Mapping, Any
#from langchain_openai import ChatOpenAI
from agents.llm_router import init_llm
import streamlit as st

from langchain_core.prompts import ChatPromptTemplate

def get_llm():
    # return ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    model_id = st.session_state.get("selected_llm", "openai:gpt-4o-mini")
    return init_llm(model_id)
    
def explain_sql_result(question: str, sql: str, rows: Sequence[Sequence[Any]]):
    """
    Turn raw rows into a human explanation.
    """
    llm = get_llm()
    rows_str = "\n".join(str(r) for r in rows[:20])

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a fraud analytics expert. Explain results clearly to a business user.",
            ),
            (
                "human",
                (
                    "User question:\n{question}\n\n"
                    "SQL used:\n{sql}\n\n"
                    "First rows of result:\n{rows}\n\n"
                    "Explain what this means in terms of fraud risk. "
                    "Highlight any caveats or potential issues in the SQL logic."
                ),
            ),
        ]
    )

    msg = prompt.format_messages(question=question, sql=sql, rows=rows_str)
    return llm.invoke(msg).content
