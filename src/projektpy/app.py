import flet as ft
import json
import asyncio
from .apiconnect import get_watch_image
from .backend import *

#Scieżki do plików
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND_LIST_PATH = os.path.join(BASE_DIR, "brand_list.json")
MODEL_LIST_PATH = os.path.join(BASE_DIR, "model_list.json")
ICON_PATH = os.path.join(BASE_DIR, "zegarekimg.png")

def start():
    ft.run(createapp,name="WatchFinder",assets_dir=BASE_DIR)   
def get_data():
    with open(MODEL_LIST_PATH,"r",encoding="utf-8") as f:
        return json.load(f)
    return ""

try:
    data = get_data()
except Exception as e:
    data = ""
    print(e)

#Tworzenie aplikacji
def createapp(page: ft.Page):
    get_max_cena(500)
    page.title = "WatchFinder"
    page.window.icon = "zegarekimg.ico"
    page.scroll = ft.ScrollMode.AUTO 
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Text("Projekt Py"))
    # page.add(search_bar())
    page.add(create_dropdown())
    page.add(create_card(page))
    create_slider(page)

#Wybrana Marka
def wybrany_brand(value):
    get_marka(value)
    print(value)

#wypełnianie listy marek
def get_brands():
    lista = []
    with open(BRAND_LIST_PATH,"r",encoding="utf-8") as f:
        data = json.load(f)
        for i in data["data"]:
            lista.append(i)
        return lista

#Tworzenie wybierania  marki
def create_dropdown():
    dropdown = ft.Dropdown(
        label="Wybierz marke",
        value="All",
        width=280,
        on_select=lambda e: wybrany_brand(e.control.value),
        options=[
            ft.DropdownOption(key="All",text="All"),
            *[ft.DropdownOption(brand) for brand in get_brands()]
                
        ])
    return dropdown

# def search_bar():
#     return ft.SafeArea(
#         content=ft.Container(
#             width=300,
#             border=ft.border.Border.all(color=ft.Colors.BLUE),
#             border_radius=10,
#             padding=5,
#             content=ft.Row(
#                 controls=[
#                 ft.TextField(label="Search",expand=True, border=ft.InputBorder.NONE),
#                 ft.IconButton(icon=ft.Icons.SEARCH)
#             ]),
#         ),
#     )

#SLider do ceny
def create_slider(page: ft.Page): 
    def handle_slider_change(e):
        get_max_cena(e.control.value)
        val = e.control.value if hasattr(e, "control") else e
        message.value = f"Cena: {round(val)} PLN"
        message.update()

    my_slider = ft.Slider(
        min=0,
        max=10000,
        value=500,
        label="{value}",
        on_change=handle_slider_change,
    )

    message = ft.Text(f"Cena: {my_slider.value} PLN")

    page.add(
        ft.SafeArea(
            content=ft.Container(
                width=min(300, (page.width or 360) - 40),
                content=ft.Column(
                    controls=[
                        ft.Text("Wybierz cenę:"),
                        my_slider,
                        message,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        )
    )
#Karta
def create_card(page: ft.Page):
    pw = page.width or 360
    card_w = max(200, min(300, pw - 140)) 
    card_h = card_w * 4 / 3

    brand = ft.Text(size=20)
    model = ft.Text(size=15)
    year = ft.Text(size=10)
    price = ft.Text(size=13)
    image = ft.Image(src="", width=card_w * 0.5, height=card_h * 0.5, fit=ft.BoxFit.CONTAIN)
    card_container = ft.Container(
        padding=20,
        width=card_w,
        height=card_h,
        border_radius=10,
        border=ft.border.Border.all(color=ft.Colors.BLUE),
        bgcolor=ft.Colors.WHITE_30,
        alignment=ft.alignment.Alignment.CENTER,
        offset=ft.Offset(0, 0),
        rotate=ft.Rotate(0),
        animate_offset=ft.Animation(100, ft.AnimationCurve.EASE_OUT),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[brand, model, year, price, image]
        )
    )
    def fill():
        w = getwatch()
        if w is None:
            brand.value = "Koniec zegarków"
            model.value = year.value = price.value = ""
            image.visible = False
        else:
            brand.value = w.brand
            model.value = w.model
            year.value = w.year_of_production
            price.value = w.price
            image.src = get_watch_image("zegarek" + w.model)
            image.visible = True

    fill()

    def decide(liked: bool):
        if getwatch() is None:
            return
        like() if liked else dislike()
        card_container.offset = ft.Offset(0, 0)
        card_container.rotate = ft.Rotate(0)
        fill()
        card_container.update()

    total_dx = 0

    def on_pan_update(e: ft.DragUpdateEvent):
        nonlocal total_dx
        total_dx += e.local_delta.x
        card_container.offset = ft.Offset(total_dx / card_w, 0)
        card_container.rotate = ft.Rotate(total_dx / 2000)
        card_container.update()

    def on_pan_end(e: ft.DragEndEvent):
        nonlocal total_dx
        dx, total_dx = total_dx, 0
        if dx > card_w / 3:
            decide(True)
        elif dx < -card_w / 3:
            decide(False)
        else:
            card_container.offset = ft.Offset(0, 0)
            card_container.rotate = ft.Rotate(0)
            card_container.update()

    return ft.SafeArea(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(icon=ft.icons.Icons.REMOVE_CIRCLE,
                              on_click=lambda e: decide(False)),
                ft.GestureDetector(
                    content=card_container,
                    on_pan_update=on_pan_update,
                    on_pan_end=on_pan_end,
                ),
                ft.IconButton(icon=ft.icons.Icons.FAVORITE,
                              on_click=lambda e: decide(True)),
            ],
        )
    )