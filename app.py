import os
import io
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="SAGL.IA",
    page_icon="💬",
    layout="centered"
)

st.title("SAGL.IA")
st.markdown("Chat com IA Generativa")

if "client" not in st.session_state:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ Chave API não encontrada! Configure a variável GEMINI_API_KEY no arquivo .env")
        st.stop()
    st.session_state.client = genai.Client(api_key=api_key)

if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="Você é um assistente de IA útil e amigável. Responda de forma clara e concisa. O usuário está no Brasil (fuso horário de Brasília, GMT-3). Use esse fuso horário como referência apenas quando o usuário perguntar sobre horário, data ou fuso horário."
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "file_name" in message:
            st.caption(f"📎 {message['file_name']}")

col1, col2 = st.columns([4, 1])

with col1:
    prompt = st.chat_input("Digite sua mensagem...")

with col2:
    with st.container():
        st.write("")
        uploaded_file = st.file_uploader(
            "Anexar arquivo",
            type=['png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx', 'txt', 'py', 'json', 'csv', 'xlsx', 'pptx'],
            label_visibility="visible"
        )

if uploaded_file is not None:
    with st.chat_message("user"):
        st.markdown(prompt if prompt else "Arquivo anexado")
        st.caption(f"📎 {uploaded_file.name}")
    
    st.session_state.messages.append({
        "role": "user",
        "content": prompt if prompt else "Arquivo anexado",
        "file_name": uploaded_file.name
    })
    
    with st.chat_message("assistant"):
        response_container = st.empty()
        full_response = ""
        
        try:
            file_data = uploaded_file.getvalue()
            mime_type = uploaded_file.type if uploaded_file.type else "application/octet-stream"
            
            config = types.UploadFileConfig(mime_type=mime_type)
            uploaded = st.session_state.client.files.upload(
                file=io.BytesIO(file_data),
                config=config
            )
            
            prompt_text = prompt if prompt else "Analise este arquivo e responda"
            contents = [uploaded, prompt_text]
            
            for chunk in st.session_state.client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=contents
            ):
                if chunk.text:
                    full_response += chunk.text
                    response_container.markdown(full_response + "▌")
            
            response_container.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Erro: {str(e)}")

elif prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        response_container = st.empty()
        full_response = ""
        
        try:
            for chunk in st.session_state.chat.send_message_stream(prompt):
                if chunk.text:
                    full_response += chunk.text
                    response_container.markdown(full_response + "▌")
            
            response_container.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Erro: {str(e)}")

if st.sidebar.button("🗑️ Limpar conversa"):
    st.session_state.messages = []
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="Você é um assistente de IA útil e amigável. Responda de forma clara e concisa. O usuário está no Brasil (fuso horário de Brasília, GMT-3). Use esse fuso horário como referência apenas quando o usuário perguntar sobre horário, data ou fuso horário."
        )
    )
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Modelo:** gemini-2.5-flash")