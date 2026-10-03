import flet as ft
import json
from .apiconnect import get_watch_image
from .backend import *

def start():
    ft.run(createapp)   
def get_data():
    with open("model.json","r",encoding="utf-8") as f:
        return json.load(f)
    return ""

try:
    data = get_data()
except Exception as e:
    data = ""
    print(e)


def createapp(page: ft.Page):
    
    page.title = "WatchFinder"
    page.add(ft.Text("Projekt Py"))
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.width = 600
    page.window.height = 700
    # page.add(search_bar())
    page.add(create_dropdown())
    page.add(create_card())
    
def wybrany_brand(value):
    get_marka(value)
    print(value)
def get_brands():
    lista = []
    with open("brand_list.json","r",encoding="utf-8") as f:
        data = json.load(f)
        for i in data["data"]:
            lista.append(i)
        return lista
def create_dropdown():
    dropdown = ft.Dropdown(
        label="Wybierz marke",
        value="All",
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
def create_card():
    brand = ft.Text(size=20)
    model = ft.Text(size=15)
    year = ft.Text(size=10)
    price = ft.Text(size=13)
    image = ft.Image(src="",width=150, height=200)
    card_container = ft.Container(
        padding=20,
        width=300,
        height=400,
        border_radius=10,
        border=ft.border.Border.all(color=ft.Colors.BLUE),
        bgcolor=ft.Colors.WHITE_30,
        alignment=ft.alignment.Alignment.CENTER,
        offset=ft.Offset(0, 0),
        rotate=ft.Rotate(0),
        animate_offset=ft.Animation(100, ft.AnimationCurve.EASE_OUT),
        content=ft.Column(
            alignment=ft.alignment.Alignment.CENTER,
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
            image.src = w.image
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
        card_container.offset = ft.Offset(total_dx / 300, 0)
        card_container.rotate = ft.Rotate(total_dx / 2000)
        card_container.update()

    def on_pan_end(e: ft.DragEndEvent):
        nonlocal total_dx
        dx, total_dx = total_dx, 0
        if dx > 100:
            decide(True)
        elif dx < -100:
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


