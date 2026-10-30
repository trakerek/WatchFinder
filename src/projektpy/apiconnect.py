import requests
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ddgs import DDGS


#Sciezki do kluczów api
base_path = os.path.dirname(os.path.abspath(__file__))
for name in ("secrets.env", ".env"):
    p = os.path.join(base_path, name)
    if os.path.exists(p):
        load_dotenv(p)
        break
#Podlaczenie do api
api_key = os.getenv("apikey2")
gemini_key = os.getenv("gptapi")
client = genai.Client(api_key=gemini_key) if gemini_key else None

#Linki do api do pobierania zegarków
WATCH_API_URL = "https://api.thewatchapi.com/v1/brand/list"
MODEL_API_URL = "https://api.thewatchapi.com/v1/model/list"
DETAILS_API_URL = "https://api.thewatchapi.com/v1/model/search"
REF_NUM_URL = "https://api.thewatchapi.com/v1/reference/list"

#Sciezki do plików 
adresy_ref = []
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model.json")
IMAGE_CACHE_FILE = os.path.join(BASE_DIR, "image_cache.json")
CACHE_PATH = os.path.join(BASE_DIR, "cache.json")
MODEL_LIST_PATH = os.path.join(BASE_DIR, "model_list.json")
BRAND_LIST_PATH = os.path.join(BASE_DIR, "brand_list.json")

class WatchRefResponse(BaseModel):
    marka: str
    model: str
    reference_number: str
    cena: str
class WatchModelByAi(BaseModel):
    brand: str
    model: str
    year_of_production: str
    price: str
class WatchImageResponse(BaseModel):
    image_url: str

#Tworzenie obiektu do pobierania z api
app =FastAPI()

#Pobieranie Marek z api zegarków
@app.get("/brands")
def get_brands():
    
    params = { 
        "api_token": api_key
    }
    response = requests.get(WATCH_API_URL,params=params)
    with open(BRAND_LIST_PATH,"w",encoding="utf-8") as f:
        json.dump(response.json(),f,indent=4,ensure_ascii=False)

#Pobieranie modeli do testowania api
@app.get("/models")
def get_model():
    params = {
        "brand": "rolex",
        "api_token": api_key
    }
    response = requests.get(MODEL_API_URL,params=params)
    with open(MODEL_LIST_PATH,"w",encoding="utf-8") as f:
        json.dump(response.json(),f,indent=4,ensure_ascii=False)

#pobierania iformacji o zegarze z api
def find_watch_by_ai(modelname):
    try:
            chat = client.chats.create(
                model="gemini-3.5-flash-lite",
                config=types.GenerateContentConfig(
                    
                    system_instruction="Jesteś ekspertem zegarmistrzostwa. Analizujesz zapytanie użytkownika i wyciągasz z niego markę, model oraz najbardziej prawdopodoby rok produkcji i cene w PLN",
                    response_mime_type="application/json",
                    response_schema=WatchModelByAi,
                ),
            )
            response = chat.send_message(f"Wskaz markę, model, rok_produkcji i cene zegara: {modelname}")
            print(response.parsed)
            return response.parsed
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Pobieranie cachu
def model_in_cache(model_name):
    try:
        with open(CACHE_PATH,"r",encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                if i == model_name:
                    return True
        get_details(model_name)
    except Exception as e:
        get_details(model_name)
        print(e)

#Pobieranie informacji o zegarze
@app.get("/details")
def get_details(modelname):
    aidata = get_watch_reference(modelname)
    ref_num = aidata.reference_number
    brand = aidata.marka
    price = aidata.cena
    params = {
        "brand": brand,
        # "model" : model,
        "reference_number": ref_num,
        "api_token": api_key
    }
    response = requests.get(DETAILS_API_URL,params=params)
    try:
        data = response.json()["data"][0]
    except Exception as e:
        print(e)
        reponse = dict(find_watch_by_ai(modelname))
        print(reponse)
        zapisywanie_cachu(reponse,modelname)
        return


    if isinstance(data, dict):
        data["price"] = price

    zapisywanie_cachu(data,modelname)

#Zapis do cachu
def zapisywanie_cachu(data,modelname):
    try:
            with open(MODEL_PATH, "r", encoding="utf-8") as f:
                data2 = json.load(f)
                data2.append(data)
    except Exception as e:
                print(e)
                data2 = [data]
        #zapisywanie modelu
    with open(MODEL_PATH, "w", encoding="utf-8") as f:
            json.dump(data2, f, indent=4, ensure_ascii=False)
        
        #zapisywanie modelu do cache
    try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                cache = json.load(f)
                cache.append(modelname)
    except Exception as e:
            print(e)
            cache = [modelname]
    
        
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=4, ensure_ascii=False)

#Pobieranie numerów referencyjnych do testow
@app.post("/get-ref-via-ai")
def get_ref_list(brand):
    params = {
        "brand": brand,
        "api_token": api_key
    }
    response = requests.get(REF_NUM_URL,params=params)
    with open("ref_nums.json","w",encoding="utf-8") as f:
        json.dump(response.json(),f,indent=4,ensure_ascii=False)

#Wsyazywanie numerów referencyjnych przez ai
@app.post("/get-ref-via-ai")
def get_watch_reference(user_query: str):
    try:
       
        tekst = f"Jesteś ekspertem zegarmistrzostwa. Analizujesz zapytanie użytkownika i wyciągasz z niego markę, model oraz najbardziej " \
                f"prawdopodobna marke, model i główny numer referencyjny oraz cene najlepiej odpowiadajacy w thewatchapi."
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

#Wybieranie odpowiednich zegarów przez ai
@app.post("/get-suitable-watch")
def get_suitable_watch(user_query: str):
    try:
        tekst = f"Jestes Ekspertem zegarmistrza i analizujesz polubione i nielubiane zegaraki na podstwaie podanej marki i cen i dobierasz najbardziej odpowiadający"\
                f"zegarek dla klienta"
        chat = client.chats.create(
            model="gemini-3.5-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=tekst,
                response_mime_type="application/json",
                response_schema=WatchModelByAi,
            ),
        )
        response = chat.send_message(f"Wybierz zegar dla klienta {user_query}")
        print(response.parsed)
        return response.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Pobierania 5 zegarów przez ai do płynnego działania aplikcaji
def get_suitable_watches(user_query: str, n: int = 5):
    try:
        tekst = "Jestes ekspertem zegarmistrza i analizujesz polubione i nielubiane zegarki na podstawie podanej marki i cen. " \
                "Dobierasz zegarki najbardziej odpowiadajace klientowi."
        chat = client.chats.create(
            model="gemini-3.5-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=tekst,
                response_mime_type="application/json",
                response_schema=list[WatchModelByAi],
            ),
        )
        response = chat.send_message(f"Wybierz {n} roznych zegarow dla klienta {user_query}")
        print(response.parsed)
        return response.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


try:
    with open(IMAGE_CACHE_FILE, "r", encoding="utf-8") as f:
        image_cache = json.load(f)
except Exception:
    image_cache = {}

#Pobieranie zdjęcia zegara
@app.post("/get-watch-image")
def get_watch_image(user_query: str):
    klucz = user_query.strip().lower()
    if klucz in image_cache:
        return image_cache[klucz]
    try:
        with DDGS() as ddg:
            results = list(ddg.images(query=user_query,max_results=1, region="pl", safe="off", site="all", time="any", lang="pl"))
            if len(results) > 0:
                image_url = results[0].get("image")
                print(image_url)
                image_cache[klucz] = image_url
                try:
                    with open(IMAGE_CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(image_cache, f, indent=4, ensure_ascii=False)
                except Exception as e:
                    print(e)
                return image_url
    except Exception as e:
        print(f"Błąd wyszukiwania zdjęcia: {e}")
    return "https://via.placeholder.com/400x400?text=Brak+Zdjecia"