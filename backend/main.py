from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Question(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/chat")
def chat(q: Question):
    if q.question.strip() == "1+1":
        return {"response": "1 + 1 = 2 😊"}
    return {"response": "Bonne question ! Réfléchissons ensemble."}
