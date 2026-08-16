import streamlit as st
from agent import run_recovery_flow, answer_followup

st.set_page_config(page_title="Loan Drop-off Recovery Agent", page_icon="💰", layout="centered")

st.title("💰 Loan Drop-off Recovery Agent")
st.caption(
    "Simulates RevRag AI's 'Recover Abandoned Loan Applications' use case — "
    "detects where a user abandoned a loan application and proactively re-engages them."
)

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent_result" not in st.session_state:
    st.session_state.agent_result = None

# ---------------------------------------------------------------------------
# Step 1: simulate an abandoned session
# ---------------------------------------------------------------------------
st.subheader("1. Simulate an abandoned application")

with st.form("simulate_form"):
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("Applicant name", value="Rohan")
        loan_amount = st.number_input("Loan amount requested (₹)", value=200000, step=10000)
    with col2:
        stuck_field = st.selectbox(
            "Field they got stuck on",
            ["pan_card", "income_proof", "aadhaar", "loan_terms"],
            format_func=lambda x: {
                "pan_card": "PAN Card upload",
                "income_proof": "Income proof upload",
                "aadhaar": "Aadhaar eKYC",
                "loan_terms": "Reviewing interest rate / fees",
            }[x],
        )
        idle_seconds = st.slider("Idle time on this step (seconds)", 30, 900, 400)

    submitted = st.form_submit_button("Simulate drop-off & generate recovery message")

if submitted:
    with st.spinner("Detecting drop-off reason and generating message..."):
        result = run_recovery_flow(user_name, stuck_field, idle_seconds, loan_amount)
    st.session_state.agent_result = result
    st.session_state.session_active = True
    st.session_state.chat_history = []

# ---------------------------------------------------------------------------
# Step 2: show the agent's diagnosis + generated message
# ---------------------------------------------------------------------------
if st.session_state.session_active and st.session_state.agent_result:
    result = st.session_state.agent_result

    st.subheader("2. Agent's diagnosis")
    st.info(f"**Likely drop-off reason:** {result['dropoff_reason']}")

    with st.expander("Retrieved policy context (RAG)"):
        for chunk in result["retrieved_context"]:
            st.markdown(f"- {chunk}")

    st.subheader("3. Re-engagement message")
    st.success(result["generated_message"])

    # -----------------------------------------------------------------
    # Step 3: chat loop for follow-up objections
    # -----------------------------------------------------------------
    st.subheader("4. Continue the conversation")
    st.caption("Reply as the user would — e.g. ask a follow-up question or raise an objection.")

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    user_input = st.chat_input("Type the user's reply...")
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.spinner("Agent responding..."):
            followup_result = answer_followup(
                user_name=result["user_name"],
                stuck_field=result["stuck_field"],
                loan_amount=result["loan_amount"],
                dropoff_reason=result["dropoff_reason"],
                user_message=user_input,
            )
        st.session_state.chat_history.append(("assistant", followup_result["generated_message"]))
        st.rerun()