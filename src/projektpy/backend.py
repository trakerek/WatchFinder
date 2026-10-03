import json
import requests
from .apiconnect import get_watch_image
class Watch:
    def __init__(self, brand, model,ref_number,year_of_production ,price,image):
        self.brand = brand
        self.model = model
        self.ref_number = ref_number
        self.year_of_production = year_of_production
        self.price = price
        self.image = image

# exp = Watch("Rolex","Explorer II","126900", "2020 - 2024","7450 EUR",get_watch_image("Rolex Explorer II"))
# air = Watch("Rolex","Air King","226570", "2012 - 2024","45000 PLN", get_watch_image("Rolex Air King"))
stos = []
liked = []
disliked = []
marka = "All"
def get_marka(inpmarka):
    marka = inpmarka
get_marka("All")
def wypelnijtablice():
    if(marka == "All"):
        stos.clear()
        with open("model.json","r",encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                if len(stos) > 10:
                    break
                stos.append(Watch(i["brand"],i["model"],i["reference_number"],i["year_of_production"],i["price"],get_watch_image(i["model"])))
    else:
        stos.clear()
        with open("model.json","r",encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                if len(stos) > 10:
                    break
                if i["brand"] != marka:
                    continue
                stos.append(Watch(i["brand"],i["model"],i["reference_number"],i["year_of_production"],i["price"],get_watch_image(i["model"])))
        
wypelnijtablice()
def getwatch():
    if len(stos) > 0:
        return stos[-1]
def dislike():
    if len(stos) > 0:
        disliked.append(stos.pop())
        print(stos)
def like():
    if len(stos) > 0:
        liked.append(stos.pop())
