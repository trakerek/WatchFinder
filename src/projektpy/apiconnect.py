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

adresy_ref = []

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


def model_in_cache(model_name):
    try:
        with open("cache.json","r",encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                if i == model_name:
                    return True
        get_details(model_name)
    except Exception as e:
        get_details(model_name)
        print(e)

@app.get("/details")
def get_details(modelname,ref_num=None):
    if ref_num == None:
        aidata = get_watch_reference(modelname)
        ref_num = aidata.reference_number
        price = aidata.cena
    params = {
        # "model" : modelname,
        "reference_number": ref_num,
        "api_token": api_key
    }
    response = requests.get(DETAILS_API_URL,params=params)
    try:
        data = response.json()["data"][0]
    except Exception as e:
        print(e)
        if len(adresy_ref) < 2:
            adresy_ref.append(ref_num)
            # print(adresy_ref)
            zmienna = get_watch_reference(modelname,ref_num)
            return get_details(modelname,zmienna.reference_number)
            

    if isinstance(data, dict):
        data["price"] = price

    #pobieranie modelu
    try:
        with open("model.json", "r", encoding="utf-8") as f:
            data2 = json.load(f)
            data2.append(data)
    except Exception as e:
        print(e)
        data2 = [data]
    #zapisywanie modelu
    with open("model.json", "w", encoding="utf-8") as f:
        json.dump(data2, f, indent=4, ensure_ascii=False)
    
    #zapisywanie modelu do cache
    try:
        with open("cache.json", "r", encoding="utf-8") as f:
            cache = json.load(f)
            cache.append(modelname)
    except Exception as e:
        print(e)
        cache = [modelname]

    
    with open("cache.json", "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4, ensure_ascii=False)

# AI API CONNECTION
client = genai.Client(api_key=os.getenv("gptapi"))

@app.post("/get-ref-via-ai")
def get_watch_reference(user_query: str, ref_num=None):
    try:
        if ref_num:
            tekst = f"Jesteś ekspertem zegarmistrzostwa. Analizujesz zapytanie użytkownika i wyciągasz z niego markę, model oraz najbardziej " \
                f"prawdopodobny główny numer referencyjny oraz cene najlepiej odpowiadajacy w thewatchapi. Podaj inny numer referencyjny niż {adresy_ref}"
        else:
            tekst = f"Jesteś ekspertem zegarmistrzostwa. Analizujesz zapytanie użytkownika i wyciągasz z niego markę, model oraz najbardziej " \
                f"prawdopodobny główny numer referencyjny oraz cene najlepiej odpowiadajacy w thewatchapi."
        chat = client.chats.create(
            model="gemini-3.5-flash-lite",
            config=types.GenerateContentConfig(
                
                system_instruction=tekst,
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
@app.post("/get-watch-image")
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
