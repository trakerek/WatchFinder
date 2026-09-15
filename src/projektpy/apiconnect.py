import requests
import json
import os
from dotenv import load_dotenv
import base64

# Pobieranie klucza api
load_dotenv()
api_key = os.getenv("apikey")

#połaczenie z bazą api
def connect():

    url = "https://watch-database1.p.rapidapi.com/search-watches-by-name"

    payload = {
        "searchTerm": "Rolex",
        "page": "1",
        "limit": "2"
    }
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "watch-database1.p.rapidapi.com",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)

    disc = response.json()

    with open("dane.json","w",encoding="utf-8") as f:
        json.dump(disc,f,indent=4,ensure_ascii=False)
def get_Image(imgsrc):
    url = f"https://watch-database1.p.rapidapi.com/images/{imgsrc}"
    
    headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "watch-database1.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        
        img_base64 = base64.b64encode(response.content).decode("utf-8")
        return img_base64
    else:
        return response.status_code
print(get_Image("5441-9-0008-a8.jpg"))