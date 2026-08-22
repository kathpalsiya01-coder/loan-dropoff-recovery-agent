"""
Loan Drop-off Recovery Agent
-----------------------------
Mirrors RevRag AI's "Recover Abandoned Loan Applications" use case:
AI agents proactively reach drop-off users, understand their hesitation,
and guide them to complete their application.

Pipeline (LangGraph StateGraph):
  1. detect_dropoff   -> figure out exactly where + why the user got stuck
  2. retrieve_context -> pull relevant FAQ/policy chunks via FAISS
  3. generate_message -> Groq LLM writes a personalized re-engagement message
  4. handle_objection -> answers follow-up user questions using the same RAG context

Requires: GROQ_API_KEY environment variable (set locally via .env, or via
Streamlit Cloud's Secrets manager when deployed).
"""

import os
from typing import TypedDict, List, Optional

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# Streamlit Cloud doesn't read .env files -- secrets are injected via st.secrets.
# This makes sure GROQ_API_KEY is available as an env var either way, so the
# rest of the code (ChatGroq, which reads from the env var) doesn't need to change.
if not os.getenv("GROQ_API_KEY"):
    try:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass  # will fail loudly later if the key truly isn't set anywhere

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END

from faq_data import FAQ_DOCS

# ---------------------------------------------------------------------------
# Vector store setup (FAISS + HuggingFace embeddings, matching existing stack)
# ---------------------------------------------------------------------------

def build_vectorstore() -> FAISS:
    docs = [
        Document(page_content=d["text"], metadata={"id": d["id"], "field": d["field"]})
        for d in FAQ_DOCS
    ]
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(docs, embeddings)


# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    user_name: str
    stuck_field: str            # e.g. "pan_card", "income_proof"
    idle_seconds: int           # how long they've been inactive on that field
    loan_amount: int
    user_message: Optional[str] # follow-up question, if any (objection-handling turn)
    retrieved_context: List[str]
    dropoff_reason: str
    generated_message: str


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def detect_dropoff(state: AgentState) -> AgentState:
    """
    Turns raw session signals (which field, how long idle) into a
    human-readable reason. In production this would come from actual
    frontend event tracking; here it's a simple rule-based mapping.
    """
    field = state["stuck_field"]
    idle = state["idle_seconds"]

    reasons = {
        "pan_card": "hesitating to share PAN card, likely a privacy/trust concern",
        "income_proof": "unsure what income document to upload or doesn't have salary slips",
        "aadhaar": "stuck on Aadhaar verification, possibly OTP/mobile-linking issue",
        "loan_terms": "confused or concerned about interest rate or fees before confirming",
    }
    reason = reasons.get(field, "generic inactivity, reason unclear")

    if idle > 300:
        reason += " (idle over 5 minutes -- high abandonment risk)"

    state["dropoff_reason"] = reason
    return state


def retrieve_context(state: AgentState) -> AgentState:
    """RAG step: pull the most relevant FAQ chunks for the stuck field
    (or for the user's follow-up question, if this is an objection-handling turn)."""
    vectorstore = state.get("_vectorstore") or build_vectorstore()
    query = state.get("user_message") or f"{state['stuck_field']} {state['dropoff_reason']}"
    results = vectorstore.similarity_search(query, k=2)
    state["retrieved_context"] = [r.page_content for r in results]
    return state


def generate_message(state: AgentState) -> AgentState:
    """Groq LLM turn: writes either the initial re-engagement message
    or a direct answer to the user's follow-up question."""
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.4)
    context = "\n\n".join(state["retrieved_context"])

    if state.get("user_message"):
        prompt = f"""You are a helpful loan application assistant. The user asked:
"{state['user_message']}"

Relevant policy context:
{context}

Answer clearly and reassuringly in 2-4 sentences. Do not invent details not in the context.
No preamble, just the answer."""
    else:
        prompt = f"""A user named {state['user_name']} started a loan application for
₹{state['loan_amount']:,} but stopped midway. They appear stuck on: {state['stuck_field']}.
Likely reason: {state['dropoff_reason']}.

Relevant policy context to draw on:
{context}

Write a short, warm re-engagement message (3-4 sentences) that:
- Names the specific step they're stuck on (don't be vague)
- Directly addresses their likely hesitation using the context above
- Ends with a clear, low-friction next action
Do not sound like a generic marketing email. No preamble, just the message."""

    response = llm.invoke(prompt)
    state["generated_message"] = response.content
    return state


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("detect_dropoff", detect_dropoff)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("generate_message", generate_message)

    graph.set_entry_point("detect_dropoff")
    graph.add_edge("detect_dropoff", "retrieve_context")
    graph.add_edge("retrieve_context", "generate_message")
    graph.add_edge("generate_message", END)

    return graph.compile()


def run_recovery_flow(user_name: str, stuck_field: str, idle_seconds: int, loan_amount: int):
    """Initial re-engagement message for a freshly abandoned session."""
    app = build_graph()
    result = app.invoke({
        "user_name": user_name,
        "stuck_field": stuck_field,
        "idle_seconds": idle_seconds,
        "loan_amount": loan_amount,
        "user_message": None,
        "retrieved_context": [],
        "dropoff_reason": "",
        "generated_message": "",
    })
    return result


def answer_followup(user_name: str, stuck_field: str, loan_amount: int,
                     dropoff_reason: str, user_message: str):
    """Handles a follow-up question in the same session, reusing the same
    detect -> retrieve -> generate pipeline but skipping re-detection."""
    app = build_graph()
    result = app.invoke({
        "user_name": user_name,
        "stuck_field": stuck_field,
        "idle_seconds": 0,
        "loan_amount": loan_amount,
        "user_message": user_message,
        "retrieved_context": [],
        "dropoff_reason": dropoff_reason,
        "generated_message": "",
    })
    return result