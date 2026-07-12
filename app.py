import streamlit as st
from ai import create_state, process_message

st.set_page_config(page_title="Medical AI Assistant")

st.title("Medical AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph_state" not in st.session_state:
    st.session_state.graph_state = create_state()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Type your message...")

if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    state, ai_response = process_message(
        st.session_state.graph_state,
        prompt
    )

    st.session_state.graph_state = state

    with st.chat_message("assistant"):
        st.markdown(ai_response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )
    with st.sidebar:
        st.subheader("Conversation State")
        st.write(f"Patient Status: {state['patient_status']}")
        st.write(f"Duration: {state['required_duration']} mins")
        st.write(f"Booking Confirmed: {state['booking_confirmed']}")