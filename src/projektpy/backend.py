import json
import math
import random
import re
import requests
import threading
from .apiconnect import get_suitable_watches, get_watch_image
class Watch:
    def __init__(self, brand, model,year_of_production ,price):
        self.brand = brand
        self.model = model
        # self.ref_number = ref_number
        self.year_of_production = year_of_production
        self.price = price
        # self.image = image

    def __repr__(self):
        return f"{self.brand} {self.model} ({self.year_of_production}, {self.price})"

stos = []
liked = []
disliked = []
marka = "All"
max_cena = None

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

def get_marka(inpmarka):
    global marka
    marka = inpmarka
    print(marka)
    wypelnijtablice()

def get_max_cena(wartosc):
    global max_cena
    max_cena = wartosc
    print(max_cena)
    wypelnijtablice()

def za_drogi(cena):
    c = cena_na_liczbe(cena)
    return max_cena is not None and c is not None and c > max_cena

def ocenione(brand, model):
    return any(w.brand == brand and w.model == model for w in liked + disliked)

def wypelnijtablice(zegar : Watch = None):
    if zegar != None:
        stos.append(zegar)
        return
    if(marka == "All"):
        stos.clear()
        with open("model.json","r",encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                if len(stos) > 10:
                    break
                if za_drogi(i["price"]) or ocenione(i["brand"], i["model"]):
                    continue
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
                if za_drogi(i["price"]) or ocenione(i["brand"], i["model"]):
                    continue
                stos.append(Watch(i["brand"],i["model"],i["year_of_production"],i["price"]))
    
wypelnijtablice()

def prefetch_zdjecia():
    # w tle pobiera zdjecie nastepnej karty, zeby po przesunieciu nie trzeba bylo czekac
    if len(stos) > 1:
        threading.Thread(target=get_watch_image, args=(f"Zegarek na ręke {stos[-2].model}",), daemon=True).start()

def getwatch():
    if len(stos) == 0:
        znajdz_zegarek()
    if len(stos) > 0:
        prefetch_zdjecia()
        return stos[-1]
    return None
def dislike():
    if len(stos) > 0:
        w = stos.pop()
        disliked.append(w)
def like():
    if len(stos) > 0:
        w = stos.pop()
        liked.append(w)


def zapisz_do_katalogu(z: Watch):
    try:
        with open("model.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []
    if any(i.get("brand") == z.brand and i.get("model") == z.model for i in data):
        return
    data.append({"brand": z.brand, "model": z.model,
                 "year_of_production": z.year_of_production, "price": z.price})
    with open("model.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def znajdz_zegarek():
    limit = f"{max_cena} PLN" if max_cena else "brak limitu"
    for _ in range(2):
        query = f"Marka : {marka} ulubione : {liked} niulubione : {disliked} maksymalna cena : {limit}"
        try:
            wyniki = get_suitable_watches(query)
        except Exception as e:
            print(e)
            return
        for r in wyniki or []:
            zegar = Watch(r.brand, r.model, r.year_of_production, r.price)
            if ocenione(zegar.brand, zegar.model) or za_drogi(zegar.price):
                continue
            if marka != "All" and zegar.brand != marka:
                continue
            if any(w.brand == zegar.brand and w.model == zegar.model for w in stos):
                continue
            wypelnijtablice(zegar)
            zapisz_do_katalogu(zegar)
        if len(stos) > 0:
            return