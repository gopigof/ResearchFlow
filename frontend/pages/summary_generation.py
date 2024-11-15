from typing import Optional

import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000"

def generate_summary(article_id: int) -> Optional[dict]:
    """Generate summary for the given article ID"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/articles/generate-summary/{article_id}",
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.error(f"Article with ID {article_id} not found")
        else:
            st.error(f"Failed to generate summary. Status code: {response.status_code}")
        return None
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None


def summary_generation_page():
    st.title("Article Summary Generation")

    # Initialize session state for summaries if not exists
    if 'summaries' not in st.session_state:
        st.session_state.summaries = {}

    # Article selection
    article_id = st.number_input("Enter Article ID", min_value=1, step=1)

    # Generate summary button
    if st.button("Generate Summary", key="generate_btn"):
        with st.spinner("Generating summary..."):
            summary_response = generate_summary(article_id)

            if summary_response:
                st.session_state.summaries[article_id] = summary_response
                st.success("Summary generated successfully!")

    # Display existing summaries
    if st.session_state.summaries:
        st.subheader("Generated Summaries")
        for aid, summary_data in st.session_state.summaries.items():
            with st.expander(f"Article {aid}: {summary_data['title']}", expanded=True):
                st.markdown(
                    f"""
                    <div class="summary-container">
                        <h4>Summary</h4>
                        <p>{summary_data['summary']}</p>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Summary", key=f"save_{aid}"):
                        try:
                            # You can implement the save functionality here
                            # Example: saving to a database or file
                            st.success("Summary saved successfully!")
                        except Exception as e:
                            st.error(f"Error saving summary: {str(e)}")

                with col2:
                    if st.button("Share Summary", key=f"share_{aid}"):
                        try:
                            # You can implement the share functionality here
                            # Example: generating a shareable link or sending via email
                            st.success("Summary shared successfully!")
                        except Exception as e:
                            st.error(f"Error sharing summary: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(page_title="Article Summary Generator", layout="wide")
    summary_generation_page()