from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter(tags=["Chat"])

class ChatMessage(BaseModel):
    message: str

@router.post("/api/chat")
async def chat_with_bot(request: ChatMessage):
    try:
        try:
            import google.generativeai as genai
        except ImportError:
            return {"reply": "Salam ! (Mode Démo) Je suis MoroGuide. N'hésitez pas à découvrir Marrakech pour son histoire, ou Dakhla pour ses plages incroyables !"}

        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"reply": "Désolé, je suis en mode hors-ligne pour le moment (Clé API manquante). Ajoutez GEMINI_API_KEY dans votre fichier .env"}
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        system_prompt = "Tu es MoroGuide, un assistant de voyage virtuel expert sur le Maroc. Tes réponses doivent être très courtes (2-3 phrases max), chaleureuses, et toujours prêtes à aider pour visiter le Maroc."
        
        response = model.generate_content(f"{system_prompt}\n\nUtilisateur: {request.message}")
        
        return {"reply": response.text}
    except Exception as e:
        print(f"Chat error: {e}")
        return {"reply": "Je rencontre une petite erreur de connexion, veuillez réessayer plus tard !"}
