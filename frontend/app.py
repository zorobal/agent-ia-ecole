# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import requests
import os

# ----------------- Configuration page -----------------
st.set_page_config(
    page_title="Agent IA École Primaire",
    page_icon="📚",
    layout="centered"
)

# ----------------- Initialiser la session -----------------
if 'exercices' not in st.session_state:
    st.session_state.exercices = []
if 'reponses_utilisateur' not in st.session_state:
    st.session_state.reponses_utilisateur = {}
if 'resultats' not in st.session_state:
    st.session_state.resultats = {}
if 'derniere_config' not in st.session_state:
    st.session_state.derniere_config = {}

st.title("🧠 Agent IA pour les enfants")
st.markdown("Pose une question et découvre comment réfléchir pas à pas !")

# ----------------- Backend URL -----------------
# Utilise variable d'environnement BACKEND_URL ou localhost pour tests
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# ----------------- Sidebar -----------------
niveau = st.sidebar.selectbox("Choisis ton niveau", ["CP", "CE1", "CE2", "CM1", "CM2"])

# Choix du mode
mode = st.sidebar.radio(
    "Que veux-tu faire ?",
    ["Poser une question libre", "Apprendre une opération"]
)

# Info sur le niveau
niveau_info = {
    "CP": "🎈 Niveau CP : Explications très simples avec des objets concrets",
    "CE1": "🎯 Niveau CE1 : Phrases simples et exemples clairs",
    "CE2": "🚀 Niveau CE2 : Début de raisonnement guidé",
    "CM1": "🎓 Niveau CM1 : Raisonnement plus élaboré",
    "CM2": "🏆 Niveau CM2 : Méthodes et stratégies"
}
st.sidebar.info(niveau_info[niveau])

# ----------------- Détection des changements et réinitialisation -----------------
config_actuelle = {
    'niveau': niveau,
    'mode': mode
}

if mode == "Poser une question libre":
    matiere = st.sidebar.selectbox("Choisis la matière", ["maths", "histoire", "culture"])
    config_actuelle['matiere'] = matiere
else:
    operation = st.sidebar.selectbox(
        "Choisis l'opération à apprendre",
        ["Addition ➕", "Soustraction ➖", "Multiplication ✖️", "Division ➗"]
    )
    config_actuelle['operation'] = operation

# Réinitialisation si configuration change
if st.session_state.derniere_config != config_actuelle:
    st.session_state.exercices = []
    st.session_state.reponses_utilisateur = {}
    st.session_state.resultats = {}
    st.session_state.derniere_config = config_actuelle.copy()
    st.rerun()

# ----------------- MODE 1 : QUESTION LIBRE -----------------
if mode == "Poser une question libre":
    question = st.text_input("Pose ta question ici :", placeholder="Exemple : 1+1, ou 5-2, ou Qui était Napoléon ?")
    
    if st.button("Demander à l'IA", type="primary") and question:
        url = f"{BACKEND_URL}/chat"
        payload = {
            "question": question,
            "niveau": niveau,
            "matiere": matiere
        }
        
        with st.spinner("🤔 L'IA réfléchit à la meilleure façon de t'expliquer..."):
            try:
                response = requests.post(url, json=payload, timeout=120)
                if response.status_code == 200:
                    answer = response.json().get("response", "")
                    st.markdown(f"### 🤖 Réponse de l'IA (niveau {niveau})")
                    st.markdown(f"{answer}")
                    st.success("💡 N'oublie pas : l'important c'est de réfléchir par toi-même !")
                else:
                    st.error(f"Erreur du serveur : {response.status_code}")
            except requests.exceptions.Timeout:
                st.error("⏱️ Le serveur met trop de temps à répondre.")
            except requests.exceptions.RequestException as e:
                st.error(f"Impossible de joindre le serveur : {e}")

# ----------------- MODE 2 : APPRENDRE UNE OPÉRATION -----------------
else:
    operation_name = operation.split()[0].lower()
    st.markdown(f"## 📖 Apprendre : {operation}")
    
    if st.button("📚 Commencer la leçon", type="primary"):
        url = f"{BACKEND_URL}/lecon"
        payload = {
            "niveau": niveau,
            "operation": operation_name
        }
        
        with st.spinner("📖 Préparation de ta leçon personnalisée..."):
            try:
                response = requests.post(url, json=payload, timeout=120)
                if response.status_code == 200:
                    data = response.json()
                    st.markdown("### 🎓 Leçon")
                    st.markdown(data.get("lecon", ""))
                    
                    st.markdown("### 📝 Exemples")
                    for i, exemple in enumerate(data.get("exemples", []), 1):
                        st.info(f"**Exemple {i}** : {exemple}")
                    
                    st.session_state.exercices = data.get("exercices", [])
                    st.session_state.reponses_utilisateur = {}
                    st.session_state.resultats = {}
                    
                    st.success("✅ Leçon chargée ! Maintenant, passons aux exercices ci-dessous.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Erreur : {e}")
    
    # Exercices
    if st.session_state.exercices:
        st.markdown("---")
        st.markdown("## ✏️ Exercices pratiques")
        st.markdown("Réponds aux problèmes suivants. L'IA vérifiera tes réponses !")
        
        for i, exercice in enumerate(st.session_state.exercices):
            st.markdown(f"### 📌 Exercice {i+1}")
            st.markdown(exercice['enonce'])
            
            col1, col2 = st.columns([3, 1])
            with col1:
                reponse_key = f"reponse_{i}"
                reponse = st.text_input("Ta réponse :", key=reponse_key, placeholder="Écris ta réponse ici")
            
            with col2:
                if st.button("Vérifier", key=f"check_{i}"):
                    if reponse:
                        url = f"{BACKEND_URL}/verifier"
                        payload = {
                            "exercice": exercice,
                            "reponse_utilisateur": reponse,
                            "niveau": niveau
                        }
                        try:
                            response = requests.post(url, json=payload, timeout=30)
                            if response.status_code == 200:
                                st.session_state.resultats[i] = response.json()
                                st.rerun()
                        except:
                            st.error("Erreur lors de la vérification")
            
            if i in st.session_state.resultats:
                result = st.session_state.resultats[i]
                if result['correct']:
                    st.success(f"✅ {result['message']}")
                else:
                    st.error(f"❌ {result['message']}")
                    st.info(f"💡 {result['explication']}")
            
            st.markdown("---")

# ----------------- Footer -----------------
st.markdown("---")
st.markdown("💡 **Astuce** : Essaie de réfléchir par toi-même avant de vérifier !")
