import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="SAGL.IA",
    page_icon="💬",
    layout="centered"
)

st.title("SAGL.IA")
st.markdown("Chat com IA Generativa")

api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyCNyX19b3YL7zdez-GUkpmPb4HkAS2_Sxs")

if not api_key:
    st.error("⚠️ Chave API não encontrada!")
    st.stop()

if "client" not in st.session_state:
    try:
        st.session_state.client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Erro ao conectar: {str(e)}")
        st.stop()

if "chat" not in st.session_state:
    try:
        st.session_state.chat = st.session_state.client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="Você é um assistente de IA útil e amigável. Responda de forma clara e concisa. O usuário está no Brasil (fuso horário de Brasília, GMT-3). Use esse fuso horário como referência apenas quando o usuário perguntar sobre horário, data ou fuso horário."
            )
        )
    except Exception as e:
        st.error(f"Erro ao criar chat: {str(e)}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua mensagem..."):
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