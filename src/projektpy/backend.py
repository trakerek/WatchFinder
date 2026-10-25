import json
import os
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
max_cena = 500

# NOWE: ustawienia doładowywania w tle
PROG_DOLADOWANIA = 3   # gdy w stosie zostaje <= 3 kart, zacznij pobierać kolejne
ILE_POBRAC = 5         # ile nowych zegarków pobrać na raz
LOCK = threading.RLock()  # chroni stos i plik model.json przed wyścigiem wątków
pobieranie = None      # aktualnie działający wątek pobierający
generacja = 0          # zwiększana przy zmianie filtrów, żeby odrzucić stare wyniki

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model.json")

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

def wypelnijtablice(zegar : Watch = None, na_poczatek=False):
    global generacja
    with LOCK:
        if zegar != None:
            # NOWE: zegarki z tła trafiają na początek listy (po tych już w kolejce)
            if na_poczatek:
                stos.insert(0, zegar)
            else:
                stos.append(zegar)
            return
        generacja += 1  # NOWE: zmiana filtra unieważnia trwające pobieranie
        stos.clear()
        with open(MODEL_PATH,"r",encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                if len(stos) > 10:
                    break
                if marka != "All" and i["brand"] != marka:
                    continue
                if za_drogi(i["price"]) or ocenione(i["brand"], i["model"]):
                    continue
                stos.append(Watch(i["brand"],i["model"],i["year_of_production"],i["price"]))
    
wypelnijtablice()

def prefetch_zdjecia():
    # w tle pobiera zdjecie nastepnej karty, zeby po przesunieciu nie trzeba bylo czekac
    if len(stos) > 1:
        threading.Thread(target=get_watch_image, args=(f"Zegarek na ręke {stos[-2].model}",), daemon=True).start()

def doladuj_w_tle():
    # NOWE: uruchamia pobieranie w osobnym wątku (jeśli jeszcze nie trwa)
    global pobieranie
    with LOCK:
        if pobieranie is not None and pobieranie.is_alive():
            return
        pobieranie = threading.Thread(
            target=znajdz_zegarek, kwargs={"w_tle": True}, daemon=True
        )
        pobieranie.start()

def getwatch():
    # NOWE: zanim karty się skończą, pobierz następne w tle
    if len(stos) <= PROG_DOLADOWANIA:
        doladuj_w_tle()
    if len(stos) == 0:
        # awaryjnie: czekamy na pobieranie z tła albo pobieramy od razu
        t = pobieranie
        if t is not None and t.is_alive():
            t.join()
        if len(stos) == 0:
            znajdz_zegarek()
    if len(stos) > 0:
        prefetch_zdjecia()
        return stos[-1]
    return None
def dislike():
    with LOCK:
        if len(stos) > 0:
            w = stos.pop()
            disliked.append(w)
def like():
    with LOCK:
        if len(stos) > 0:
            w = stos.pop()
            liked.append(w)


def zapisz_do_katalogu(z: Watch):
    with LOCK:
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

def znajdz_zegarek(w_tle=False):
    gen = generacja
    dodane = 0
    limit = f"{max_cena} PLN" if max_cena else "brak limitu"
    for _ in range(2):
        query = (f"Marka : {marka} ulubione : {liked} niulubione : {disliked} "
                 f"maksymalna cena : {limit} ilość : {ILE_POBRAC}")
        try:
            wyniki = get_suitable_watches(query)  # wolne wywołanie AI - poza lockiem
        except Exception as e:
            print(e)
            return
        for r in wyniki or []:
            zegar = Watch(r.brand, r.model, r.year_of_production, r.price)
            with LOCK:
                # NOWE: jeśli w międzyczasie zmieniono markę/cenę, wyrzuć stare wyniki
                if w_tle and gen != generacja:
                    return
                if ocenione(zegar.brand, zegar.model) or za_drogi(zegar.price):
                    continue
                if marka != "All" and zegar.brand != marka:
                    continue
                if any(w.brand == zegar.brand and w.model == zegar.model for w in stos):
                    continue
                wypelnijtablice(zegar, na_poczatek=w_tle)
            zapisz_do_katalogu(zegar)
            dodane += 1
            if w_tle and dodane >= ILE_POBRAC:
                return
        if w_tle:
            if dodane > 0:
                return
        elif len(stos) > 0:
            return