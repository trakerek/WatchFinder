import requests
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ddgs import DDGS

load_dotenv()
api_key = os.getenv("apikey2")

WATCH_API_URL = "https://api.thewatchapi.com/v1/brand/list"
MODEL_API_URL = "https://api.thewatchapi.com/v1/model/list"
DETAILS_API_URL = "https://api.thewatchapi.com/v1/model/search"


class WatchRefResponse(BaseModel):
    reference_number: str
    cena: str


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
    aidata = get_watch_reference("Rolex Air King")
    ref_num = aidata.reference_number
    price = aidata.cena
    params = {
        "brand": "Rolex",
        "model" : "Rolex Air King",
        "reference_number": ref_num,
        "api_token": api_key
    }
    response = requests.get(DETAILS_API_URL,params=params)
    data = response.json()

    if isinstance(data, dict):
        data["price"] = price

    with open("model.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# AI API CONNECTION
client = genai.Client(api_key=os.getenv("gptapi"))

@app.post("/get-ref-via-ai")
def get_watch_reference(user_query: str):
    try:
        chat = client.chats.create(
            model="gemini-3.6-flash",
            config=types.GenerateContentConfig(
                system_instruction=f"Jesteś ekspertem zegarmistrzostwa. Analizujesz zapytanie użytkownika i wyciągasz z niego markę, model oraz najbardziej " \
                f"prawdopodobny główny numer referencyjny oraz cene.",
                response_mime_type="application/json",
                response_schema=WatchRefResponse,
            ),
        )
        response = chat.send_message(f"Wskaz numer referencyjny i cene zegara: {user_query}")
        print(response.parsed)
        return response.parsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
class WatchImageResponse(BaseModel):
    image_url: str
@app.post("/get-ref-via-ai")
def get_watch_image(user_query: str):
    try:
        with DDGS() as ddg:
            results = list(ddg.images(query=user_query,max_results=1, region="pl", safe="off", site="all", time="any", lang="pl"))
            if len(results) > 0:
                image_url = results[0].get("image")
                print(image_url)
                return image_url
    except Exception as e:
        print(f"Błąd wyszukiwania zdjęcia: {e}")
    return "https://via.placeholder.com/400x400?text=Brak+Zdjecia"
