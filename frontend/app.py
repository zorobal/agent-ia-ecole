# -*- coding: utf-8 -*-
import streamlit as st
import requests

# ----------------- Configuration -----------------
st.set_page_config(page_title="Agent IA École Primaire", page_icon="📚", layout="centered")
st.title("🧠 Agent IA pour les enfants")
st.markdown("Pose une question et découvre comment réfléchir pas à pas !")

# ----------------- Sidebar -----------------
niveau = st.sidebar.selectbox("Choisis ton niveau", ["CP", "CE1", "CE2", "CM1", "CM2"])
matiere = st.sidebar.selectbox("Choisis la matière", ["maths", "histoire", "culture"])
question = st.text_input("Pose ta question ici :")

# ----------------- URL du backend Cloud -----------------
BACKEND_URL = "https://TON_BACKEND_URL/chat"  # <-- à remplacer par ton URL Railway/Render

if st.button("Demander à l'IA") and question:
    payload = {"question": question, "niveau": niveau, "matiere": matiere}
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=30)
        if response.status_code == 200:
            st.markdown(f"### 🤖 Réponse pédagogique :\n\n{response.json().get('response','')}")
        else:
            st.error(f"Erreur du serveur : {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Impossible de joindre le serveur : {e}")
