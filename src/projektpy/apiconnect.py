import requests
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("apikey2")

WATCH_API_URL = "https://api.thewatchapi.com/v1/brand/list"
MODEL_API_URL = "https://api.thewatchapi.com/v1/model/list"
DETAILS_API_URL = "https://api.thewatchapi.com/v1/model/search"

app =FastAPI()
@app.get("/brands")
def get_brands():
    
    params = { 
        "api_token": api_key
    }
    response = requests.get(WATCH_API_URL,params=params)
    with open("brand_list.json","w",encoding="utf-8") as f:
        json.dump(response.json(),f,indent=4,ensure_ascii=False)


@app.get("/models")
def get_model():
    params = {
        "brand": "rolex",
        "api_token": api_key
    }
    response = requests.get(MODEL_API_URL,params=params)
    with open("model_list.json","w",encoding="utf-8") as f:
        json.dump(response.json(),f,indent=4,ensure_ascii=False)


@app.get("/details")
def get_details():
    params = {
        "brand": "Rolex",
        "model" : "Rolex Air King",
        "reference_number": get_watch_reference("Rolex Air King"),
        "api_token": api_key
    }
    response = requests.get(DETAILS_API_URL,params=params)
    with open("model.json","w",encoding="utf-8") as f:
        json.dump(response.json(),f,indent=4,ensure_ascii=False)


# AI API CONNECTION
client = genai.Client(api_key=os.getenv("gptapi"))
class WatchRefResponse(BaseModel):
    # brand: str
    # model: str
    reference_number: str
    # confidence: str  # np. "high", "medium"

@app.post("/get-ref-via-ai")
def get_watch_reference(user_query: str):
    try:
        chat = client.chats.create(
            model="gemini-3.6-flash",
            config=types.GenerateContentConfig(
                system_instruction=f"Jesteś ekspertem zegarmistrzostwa. Analizujesz zapytanie użytkownika i wyciągasz z niego markę, model oraz najbardziej " \
                f"prawdopodobny główny numer referencyjny.",
                response_mime_type="application/json",
                response_schema=WatchRefResponse,
            ),
        )
        response = chat.send_message(f"Wskaz numer referencyjny zegara: {user_query}")
        print(response.parsed)
        return response.parsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
class WatchImageResponse(BaseModel):
    image_url: str
@app.post("/get-ref-via-ai")
def get_watch_image(user_query: str):
    try:
        chat = client.chats.create(
            model="gemini-3.6-flash",
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                system_instruction=(
                    "Jesteś ekspertem zegarmistrzostwa. Wyciągnij model i numer referencyjny. "
                    "Wyszukaj w sieci bezpośredni, publicznie dostępny adres URL do zdjęcia "
                    "tego zegarka. Zwróć dane wyłącznie w formacie JSON zgodnym ze schematem."
                ),
                response_mime_type="application/json",
                response_schema=WatchImageResponse,
            )
        )
        response = chat.send_message(f"Zwróc link do zdjecia zegara: {user_query}")
        print(response.parsed)
        return response.parsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))