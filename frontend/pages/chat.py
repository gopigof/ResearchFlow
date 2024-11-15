import base64
import io
from fpdf import FPDF
import streamlit as st
from dotenv import load_dotenv

from frontend.pages.list_docs import fetch_documents
from frontend.utils.chat import fetch_file_from_s3
from frontend.utils.auth import make_authenticated_request
import base64
import io
from fpdf import FPDF
import streamlit as st
from dotenv import load_dotenv
import os

class ChatPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_margins(20, 20, 20)  # Left, Top, Right margins

    def chapter_title(self, text):
        self.set_font('Helvetica', 'B', 24)
        self.cell(0, 20, text, ln=True)
        self.ln(10)

    def section_title(self, text):
        # Add a line above each section
        self.line(20, self.get_y(), self.w - 20, self.get_y())
        self.ln(5)
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, text, ln=True)
        self.ln(5)

    def body_text(self, text):
        self.set_font('Helvetica', '', 12)
        # Handle bullet points by replacing Unicode bullet with hyphen
        text = text.replace('•', '-')
        # Split text into paragraphs
        paragraphs = text.split('\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                if paragraph.strip().startswith('-'):
                    # Handle bullet points with proper indentation
                    self.cell(10)  # Add indentation
                    self.multi_cell(0, 10, paragraph.strip())
                else:
                    self.multi_cell(0, 10, paragraph.strip())
        self.ln(5)

def convert_to_pdf(markdown_content):
    try:
        # Initialize PDF
        pdf = ChatPDF()

        # Add main title
        pdf.chapter_title("Chat Conversation")

        # Process chat messages
        messages = st.session_state.chat_history

        for message in messages:
            # Add role as section header
            role = message["role"].capitalize()
            pdf.section_title(role)

            # Process content
            content = message["content"]

            # Clean up markdown formatting
            content = content.replace('**', '')
            # Replace markdown bullet points with hyphen
            content = content.replace('- ', '- ')

            # Add content
            pdf.body_text(content)

            # Add space between messages
            pdf.ln(5)

        # Save to BytesIO
        pdf_output = io.BytesIO()
        pdf_data = pdf.output(dest='S').encode('latin-1')
        pdf_output.write(pdf_data)
        pdf_output.seek(0)
        return pdf_output

    except Exception as e:
        st.error(f"Error converting to PDF: {str(e)}")
        return None

def convert_chat_to_markdown():
    markdown_content = "# Chat Conversation\n\n"

    if 'selected_document' in st.session_state:
        doc = st.session_state.selected_document
        markdown_content += f"Document: {doc['title']}\n\n"

    for message in st.session_state.chat_history:
        role = message["role"].capitalize()
        content = message["content"]
        markdown_content += f"## {role}\n\n{content}\n\n"

    return markdown_content

# Add this function at the beginning of your code
def display_pdf(pdf_file):
    """Display PDF in Streamlit app."""
    base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="1400" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Then modify the qa_interface function to include the PDF preview
def qa_interface():
    st.title("Research Question Answering Interface")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Fetch documents from backend API
    documents = fetch_documents()
    selected_doc = None
    if not documents:
        st.write("No documents available.")
        return

    selected_doc_name = st.selectbox("Choose a document", [doc["filename"] for doc in documents])
    if selected_doc_name:
        if st.button(f"View {selected_doc_name}"):
            selected_doc = next((doc for doc in documents if doc["filename"] == selected_doc_name), None)

    # Main interface
    if selected_doc:
        doc = selected_doc
        st.subheader(f"Analyzing: {doc['filename']}")

        # Get OpenAI model choices
        openai_models_choice = st.selectbox(
            "Choose an OpenAI model", ["gpt-4o", "gpt-4o-mini", "gpt-3.5"]
        )

        # Document preview at the top
        with st.expander("Document Preview", expanded=False):
            try:
                pdf_path = fetch_file_from_s3(doc["sourcepdf_url"], None)
                with open(pdf_path, "rb") as f:
                    display_pdf(io.BytesIO(f.read()))
            except Exception as e:
                st.error(f"Error displaying PDF: {str(e)}")

        st.divider()  # Add a divider between PDF and chat

        # Chat interface below
        chat_container = st.container()

        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask your research question:"):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            # Get AI response
            with st.spinner("Analyzing..."):
                try:
                    response = make_authenticated_request(
                        f"/chat/{doc['a_id']}/qa",
                        "POST",
                        {"question": prompt}
                    )

                    with st.chat_message("assistant"):
                        st.markdown(response["response"])

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response["response"]
                    })
                except Exception as e:
                    st.error(f"Analysis error: {str(e)}")

        # Export options at the bottom
        if st.session_state.chat_history:
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                markdown_content = convert_chat_to_markdown()
                st.download_button(
                    "Download as Markdown",
                    markdown_content,
                    "chat_conversation.md",
                    "text/markdown"
                )

            with col2:
                pdf_output = convert_to_pdf(markdown_content)
                if pdf_output:
                    st.download_button(
                        "Download as PDF",
                        pdf_output.getvalue(),
                        "chat_conversation.pdf",
                        "application/pdf"
                    )

    else:
        st.divider()
        st.warning("Please select a document to begin your research.")

if __name__ == "__main__":
    qa_interface()
