import streamlit as st
import requests

st.set_page_config(page_title="Agent IA École", page_icon="🎓")

st.title("🎓 Agent IA École")

question = st.text_input("Pose ta question")

if question:
    with st.spinner("Réflexion en cours..."):
        try:
            response = requests.post(
                "https://URL_BACKEND/chat",  # on changera après
                json={"question": question},
                timeout=15
            )
            st.success(response.json()["response"])
        except Exception as e:
            st.error(f"Erreur : {e}")
