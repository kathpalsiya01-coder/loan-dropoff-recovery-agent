# 💰 Loan Drop-off Recovery Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" alt="Python 3.11"/>
  <img src="https://img.shields.io/badge/LangGraph-Agent%20Orchestration-1C3C3C" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/Groq-llama--3.3--70b-orange" alt="Groq"/>
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-005571" alt="FAISS"/>
  <img src="https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"/><https://kathpalsiya01-coder-loan-dropoff-recovery-agent-app-x6tlfd.streamlit.app/>
  <img src="https://img.shields.io/badge/status-working%20demo-brightgreen" alt="Status"/>
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License"/>
</p>

<p align="center">
  An AI agent that detects <b>where and why</b> a user abandoned a loan application,
  retrieves grounded policy context, and generates a personalized message to bring them back —
  then keeps the conversation going to handle real objections.
</p>

<p align="center">
  Built as a portfolio piece mirroring <a href="https://www.revrag.ai">RevRag AI's</a>
  "Recover Abandoned Loan Applications" use case.
</p>

---

## 📑 Table of Contents

- [Why this problem](#-why-this-problem)
- [How it works](#-how-it-works)
- [Architecture](#-architecture)
- [Demo](#-demo)
- [Setup](#-setup)
- [Project structure](#-project-structure)
- [What it demonstrates](#-what-it-demonstrates)
- [Possible extensions](#-possible-extensions)

---

## 🎯 Why this problem

Most loan-application drop-off isn't disinterest — it's **friction**. A user unsure
why PAN is needed. Confused about which income document to upload. Hesitant about a
rate they don't understand. Generic reminder emails ("complete your application!")
don't address the actual blocker.

This agent tries to diagnose the *specific* blocker and respond to it directly,
grounded in real policy — not a guess.

---

## ⚙️ How it works

| Step | What happens |
|------|---------------|
| 1️⃣ Detect | Agent reads session signals (which field, how long idle) and infers the likely reason for drop-off |
| 2️⃣ Retrieve | Pulls the most relevant policy/FAQ chunks via FAISS similarity search |
| 3️⃣ Generate | Groq LLM writes a personalized re-engagement message, grounded only in retrieved context |
| 4️⃣ Converse | Same pipeline handles follow-up objections in a live chat loop |

---

## 🏗️ Architecture

```
                 ┌─────────────────┐
   session data  │  detect_dropoff │   rule-based diagnosis
   ────────────► │                 │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │ retrieve_context│   FAISS + sentence-transformers
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │ generate_message│   Groq · llama-3.3-70b-versatile
                 └────────┬────────┘
                          │
                    re-engagement
                       message
```

Built as a **LangGraph StateGraph** — the same 3-node pipeline is reused for both
the cold-open recovery message and every follow-up turn in the chat, just with a
different `user_message` in state.

---

## 🎬 Demo

**Try it live:** *https://kathpalsiya01-coder-loan-dropoff-recovery-agent-app-x6tlfd.streamlit.app/*

---

## 🚀 Setup

```bash
# 1. Create environment
conda create -n loan-agent python=3.11 -y
conda activate loan-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Groq API key
cp .env.example .env
# then edit .env and paste your key from console.groq.com

# 4. Run
streamlit run app.py
```

---

## 📂 Project structure

```
loan-dropoff-recovery-agent/
├── agent.py         # LangGraph pipeline: detect → retrieve → generate
├── app.py           # Streamlit UI + chat loop
├── faq_data.py       # Mock loan policy / FAQ knowledge base
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🧠 What it demonstrates

- ✅ LangGraph StateGraph orchestration (linear pipeline, reused across turns)
- ✅ RAG grounding — the agent can't invent fees, rates, or policy details
- ✅ Rule-based signal interpretation feeding an LLM generation step
- ✅ One pipeline serving both a "cold open" message and multi-turn chat

---

## 🔮 Possible extensions

- [ ] Real event-tracking hook instead of a manual "idle seconds" slider
- [ ] Swap rule-based `detect_dropoff` for an LLM classifier over raw session logs
- [ ] Voice mode using Whisper STT (mirrors RevRag's Calling AI Agent)
- [ ] Multilingual support (Hindi/regional languages) for the generated message

---

<p align="center">Built by <a href="https://github.com/kathpalsiya01-coder">Siya Kathpal</a></p>
