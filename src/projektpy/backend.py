import json
import math
import random
import re
import requests
from .apiconnect import get_watch_image
class Watch:
    def __init__(self, brand, model,year_of_production ,price):
        self.brand = brand
        self.model = model
        # self.ref_number = ref_number
        self.year_of_production = year_of_production
        self.price = price
        # self.image = image

stos = []
liked = []
disliked = []
brand_value = {"All":0,"Rolex": 0, "Omega": 0, "Casio": 0}
fav_price = None
marka = "All"

KURSY = {"PLN": 1, "EUR": 4.3, "USD": 4.0, "GBP": 5.0, "CHF": 4.5}

def cena_na_liczbe(tekst):
    tekst = str(tekst)
    m = re.search(r"\d[\d\s]*", tekst)
    if not m:
        return None
    liczba = int(re.sub(r"\D", "", m.group()))
    waluta = re.search(r"[A-Za-z]{3}", tekst)
    kurs = KURSY.get(waluta.group().upper(), 1) if waluta else 1
    return liczba * kurs if liczba > 0 else None

def ocena(w):
    s = brand_value.get(w.brand, 0)
    cena = cena_na_liczbe(w.price)
    if fav_price and cena:
        s += 1 - min(1, abs(math.log(cena) - math.log(fav_price)))
    return s

def sortuj():
    stos.sort(key=lambda w: ocena(w) + random.random() * 0.01)
    if len(stos) > 2 and random.random() < 0.2:
        i = random.randrange(len(stos))
        stos[i], stos[-1] = stos[-1], stos[i]

def get_marka(inpmarka):
    global marka
    marka = inpmarka
    print(marka)
    wypelnijtablice()

def wypelnijtablice():
    if(marka == "All"):
        stos.clear()
        with open("model.json","r",encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                if len(stos) > 10:
                    break
                stos.append(Watch(i["brand"],i["model"],i["year_of_production"],i["price"]))
    else:
        stos.clear()
        with open("model.json","r",encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                if len(stos) > 10:
                    break
                if i["brand"] != marka:
                    continue
                stos.append(Watch(i["brand"],i["model"],i["year_of_production"],i["price"]))
    sortuj()

wypelnijtablice()

def getwatch():
    if len(stos) > 0:
        return stos[-1]
def dislike():
    if len(stos) > 0:
        w = stos.pop()
        brand_value[w.brand] = brand_value.get(w.brand, 0) - 1
        disliked.append(w)
        sortuj()
def like():
    global fav_price
    if len(stos) > 0:
        w = stos.pop()
        brand_value[w.brand] = brand_value.get(w.brand, 0) + 1
        liked.append(w)
        cena = cena_na_liczbe(w.price)
        if cena:
            fav_price = cena if fav_price is None else 0.7 * fav_price + 0.3 * cena
        sortuj()