import streamlit as st
import assistant as asst
import textwrap

st.title("Youtube Assistant")

with st.sidebar:
    with st.form(key='my_form'):
        youtube_url = st.sidebar.text_area(
            label="Give the link of the youtube video",
            max_chars=100
        )
        query = st.sidebar.text_area(
            label="Ask a question about the video",
            max_chars=100,
            key='query'
        )

        submit_button = st.form_submit_button(label='Submit')

if query and youtube_url:
    db = asst.create_vector_db_from_youtube(youtube_url)
    response, doc = asst.get_response_from_query(db, query)
    st.subheader('Answer:')
    st.text(textwrap.fill(response, width=100))