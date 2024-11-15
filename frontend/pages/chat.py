import base64
import io
from fpdf import FPDF
import streamlit as st
from dotenv import load_dotenv
from frontend.utils.chat import fetch_file_from_s3
from frontend.utils.auth import make_authenticated_request

load_dotenv()

def display_pdf(pdf_file):
    base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def convert_chat_to_markdown():
    markdown_content = "# Chat Conversation\n\n"
    for message in st.session_state.messages:
        role = message["role"].capitalize()
        content = message["content"]
        markdown_content += f"## {role}\n\n{content}\n\n"
    return markdown_content

def download_markdown():
    markdown_content = convert_chat_to_markdown()
    b64 = base64.b64encode(markdown_content.encode()).decode()
    href = f'<a href="data:text/markdown;base64,{b64}" download="chat_conversation.md">Download Markdown</a>'
    return href

def convert_markdown_to_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Chat Conversation", ln=True, align="C")
    pdf.ln(10)

    for message in st.session_state.messages:
        role = message["role"].capitalize()
        content = message["content"]
        pdf.multi_cell(0, 10, f"{role}:\n{content}")
        pdf.ln(5)

    # Generate PDF as bytes
    pdf_output = io.BytesIO()
    pdf_data = pdf.output(dest="S").encode("latin1")
    pdf_output.write(pdf_data)
    pdf_output.seek(0)
    return pdf_output

def download_pdf():
    pdf_output = convert_markdown_to_pdf()
    b64 = base64.b64encode(pdf_output.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="chat_conversation.pdf">Download PDF</a>'
    return href

def qa_interface():
    st.title("Question Answering Interface")

    # Initialize chat history only once
    if "messages" not in st.session_state:
        st.session_state.messages = []

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

        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about the article"):
            # Append user question to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user question in chat
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

            # Display assistant response in chat
            with st.chat_message("assistant"):
                st.markdown(response["response"])

            # Append assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response["response"]})

        # Add download buttons for markdown and PDF
        if st.session_state.messages:
            st.markdown(download_markdown(), unsafe_allow_html=True)
            st.markdown(download_pdf(), unsafe_allow_html=True)

    else:
        st.warning(
            "No article selected. Please upload a PDF file before asking questions."
        )

if __name__ == "__main__":
    qa_interface()
