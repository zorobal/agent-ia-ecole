# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama

# ----------------- Initialisation FastAPI -----------------
app = FastAPI(
    title="Agent IA École Primaire",
    description="Agent pédagogique pour enfants du CP au CM2 utilisant Ollama",
    version="1.0"
)

# ----------------- CORS -----------------
origins = [
    "https://share.streamlit.io",
    "http://localhost",
    "*"  # Pour tests
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Modèle de requête -----------------
class Question(BaseModel):
    question: str
    niveau: str  # CP, CE1, CE2, CM1, CM2
    matiere: str  # maths, histoire, culture

# ----------------- Instructions par niveau -----------------
niveau_instructions = {
    "CP": "Utilise des phrases très simples, un exemple concret, un concept par question.",
    "CE1": "Phrase simple, exemples concrets, introduis un peu de vocabulaire nouveau.",
    "CE2": "Phrase claire, exemple en 2 étapes, vocabulaire adapté.",
    "CM1": "Phrases plus longues, exemples un peu plus abstraits.",
    "CM2": "Phrases complètes, exemples détaillés, faire réfléchir avec plusieurs étapes."
}

# ----------------- Prompts par matière -----------------
matiere_prompts = {
    "maths": "Tu es un professeur de mathématiques pour enfants. Explique les concepts étape par étape avec des exemples simples.",
    "histoire": "Tu es un professeur d'histoire pour enfants. Explique les événements, personnages, dates de façon simple et imagée.",
    "culture": "Tu es un professeur de culture générale pour enfants. Explique les concepts simplement et pose des questions pour faire réfléchir."
}

# ----------------- Prompt système strict -----------------
SYSTEM_PROMPT = """
Tu es un assistant pédagogique pour enfants de l’école primaire (CP à CM2).
RÈGLES STRICTES :
- Langage simple et clair selon le niveau de l’enfant
- Utiliser uniquement des exemples très simples et concrets (pommes, billes, crayons)
- Expliquer étape par étape comment réfléchir et trouver la réponse
- Ne jamais donner le résultat final ou le nombre directement
- Poser toujours une question finale pour que l’enfant réfléchisse
- Encourager la curiosité et la recherche personnelle
"""

# ----------------- Endpoint principal -----------------
@app.post("/chat")
async def chat(data: Question):
    niveau = data.niveau.upper()
    matiere = data.matiere.lower()
    
    if niveau not in niveau_instructions:
        return JSONResponse(content={"response": f"Niveau '{niveau}' non reconnu."}, status_code=400)
    if matiere not in matiere_prompts:
        return JSONResponse(content={"response": f"Matière '{matiere}' non reconnue."}, status_code=400)

    prompt = f"""
Niveau de l'enfant : {niveau}
Matière : {matiere}
Instructions pour le niveau : {niveau_instructions[niveau]}
Instructions pour la matière : {matiere_prompts[matiere]}
Question de l'enfant : {data.question}

Règles :
- Exemple simple et concret
- Expliquer étape par étape
- NE PAS donner le résultat final ou le chiffre
- Terminer avec une question claire pour que l'enfant réfléchisse
- Phrase courte et très claire adaptée au niveau
"""

    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response["message"]["content"]

    return JSONResponse(
        content={"response": answer},
        media_type="application/json; charset=utf-8"
    )
