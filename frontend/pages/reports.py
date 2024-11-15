import base64
import io
import uuid

import streamlit as st
from dotenv import load_dotenv

from frontend.utils.chat import fetch_file_from_s3
from frontend.utils.auth import make_authenticated_request

load_dotenv()

# Initialize session states
if 'reports' not in st.session_state:
    st.session_state.reports = []
if 'responses_feedback' not in st.session_state:
    st.session_state.responses_feedback = {}


def handle_feedback(response_idx, feedback, article_id: str, report_id: str):
    """Handle the accept/deny feedback for a response"""
    st.session_state.responses_feedback[response_idx] = feedback
    make_authenticated_request(f"/chat/{article_id}/{report_id}/index", "POST", data={"feedback": feedback})
    st.toast(f"Response marked as {feedback}")


def display_pdf(pdf_file):
    base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def generate_report_interface():
    st.title("Report Generation")

    # Main interface
    if 'selected_document' in st.session_state and st.session_state.selected_document:
        doc = st.session_state.selected_document
        st.subheader(f"Viewing: {doc['title']}")

        # Get OpenAI model choices
        openai_models_choice = st.selectbox(
            "Choose an OpenAI model", ["gpt-4o", "gpt-4o-mini", "gpt-3.5"]
        )

        # Display PDF content preview
        st.subheader("PDF Content Preview")
        with st.spinner("Loading PDF"):
            pdf_path = fetch_file_from_s3(doc["pdf_url"], None)
            with open(pdf_path, "rb") as f:
                content = f.read()
            display_pdf(io.BytesIO(content))

        st.divider()

        # Display chat messages with feedback buttons
        for idx, message in enumerate(st.session_state.reports):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Only show feedback buttons for assistant messages
                if message["role"] == "assistant":
                    col1, col2, col3 = st.columns([1, 1, 4])

                    # Check if this response already has feedback
                    current_feedback = st.session_state.responses_feedback.get(idx)

                    with col1:
                        accept_button = st.button("✓ Accept",
                                                  key=f"accept_{idx}",
                                                  type="primary" if current_feedback == "accepted" else "secondary",
                                                  disabled=current_feedback is not None)
                        if accept_button:
                            handle_feedback(idx, "accepted", doc["a_id"], st.session_state.get("report_id", ""))

                    with col2:
                        deny_button = st.button("✗ Deny",
                                                key=f"deny_{idx}",
                                                type="primary" if current_feedback == "denied" else "secondary",
                                                disabled=current_feedback is not None)
                        if deny_button:
                            handle_feedback(idx, "denied", doc["a_id"], st.session_state.get("report_id", ""))

        # Chat input
        if prompt := st.chat_input("Ask an analytical question to generate reports:"):
            st.session_state.reports.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Process the query
            with st.spinner("Thinking..."):
                article_id = doc['a_id']
                data = {
                    "model": openai_models_choice,
                    "question": prompt,
                }
                response = make_authenticated_request(f"/chat/{article_id}/qa", "POST", data)
                st.session_state.report_id = response.get("report_id", uuid.uuid4().hex)

            # Display the response
            with st.chat_message("assistant"):
                st.markdown(response["response"])

            st.session_state.reports.append(
                {"role": "assistant", "content": response["response"]}
            )

    else:
        st.warning(
            "No article selected. Please upload a PDF file before asking questions."
        )