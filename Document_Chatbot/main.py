import os
from dotenv import load_dotenv
import openai
import requests
import json

import time
import logging
from datetime import datetime
import streamlit as st

load_dotenv()

client = openai.OpenAI()

model = "gpt-4-1106-preview"

thread_id = "thread_EBOLCzNXvqimZ5hpsQ3vtbXv"
assis_id = "asst_3HPrdmyMeJ2t8UxkW7l2SqPJ"

if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(
    page_title="Document Chatbot",
    page_icon=":robot:",
)

def upload_to_openai(filepath):
    with open(filepath, "rb") as file:
        response = client.files.create(file=file.read(), purpose="assistants")
    return response.id

file_upload = st.sidebar.file_uploader("Upload a file", type="pdf", key="file_upload")

if st.sidebar.button("Start Chat"):
    if file_upload:
        with open(file_upload.name, "wb") as f:
            f.write(file_upload.getbuffer())
        another_file_id = upload_to_openai(file_upload.name)
        st.session_state.file_id_list.append(another_file_id)
        st.sidebar.write('File Id:', another_file_id)

if st.session_state.file_id_list:
    st.sidebar.write('File Id:', st.session_state.file_id_list)
    for file_id in st.session_state.file_id_list:
        st.sidebar.write('File Id:', file_id)
        assistant_file = client.beta.assistants.files.create(
            assistant_id=assis_id, 
            file_id=file_id
            )
        
if st.sidebar.button("Start Chatting..."):
    if st.session_state.file_id_list:
        st.session_state.start_chat = True

        chat_thread = client.beta.threads.create()
        st.session_state.thread_id = chat_thread.id
        st.write("Thread ID:", chat_thread.id)
    else:
        st.sidebar.warning(
            "No files found. Please upload at least one file to get started."
        )

# Define the function to process messages with citations
def process_message_with_citations(message):
    """Extract content and annotations from the message and format citations as footnotes."""
    message_content = message.content[0].text
    annotations = (
        message_content.annotations if hasattr(message_content, "annotations") else []
    )
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(
            annotation.text, f" [{index + 1}]"
        )

        # Gather citations based on annotation attributes
        if file_citation := getattr(annotation, "file_citation", None):
            # Retrieve the cited file details (dummy response here since we can't call OpenAI)
            cited_file = {
                "filename": "cryptocurrency.pdf"
            }  # This should be replaced with actual file retrieval
            citations.append(
                f'[{index + 1}] {file_citation.quote} from {cited_file["filename"]}'
            )
        elif file_path := getattr(annotation, "file_path", None):
            # Placeholder for file download citation
            cited_file = {
                "filename": "cryptocurrency.pdf"
            }  # TODO: This should be replaced with actual file retrieval
            citations.append(
                f'[{index + 1}] Click [here](#) to download {cited_file["filename"]}'
            )  # The download link should be replaced with the actual download path

    # Add footnotes to the end of the message content
    full_response = message_content.value + "\n\n" + "\n".join(citations)
    return full_response

st.title("Document Chatbot")
st.write('ask your document here')

if st.session_state.start_chat:
    if "openai_response" not in st.session_state:
        st.session_state.openai_model = "gpt-4-1106-preview"
    if "message" not in st.session_state:
        st.session_state.message = []

    for message in st.session_state.message:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("what new?:"):
        st.session_state.message.append({"role": "user", "content": prompt})
        with st.chat_message('user'):
            st.markdown(prompt)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assis_id,
            instructions="""Please answer the questions using the knowledge provided in the files.
            when adding additional information, make sure to distinguish it with bold or underlined text.""",
        )

        with st.spinner("Wait... Generating response..."):
            while run.status != "completed":
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id, run_id=run.id
                )
            # Retrieve messages added by the assistant
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            # Process and display assis messages
            assistant_messages_for_run = [
                message
                for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]

            for message in assistant_messages_for_run:
                full_response = process_message_with_citations(message=message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)

    else:
        # Promopt users to start chat
        st.write(
            "Please upload at least a file to get started by clicking on the 'Start Chat' button"
        )