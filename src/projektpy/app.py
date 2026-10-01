import flet as ft
import json
from .apiconnect import get_watch_image
def start():
    ft.run(createapp)   
def get_data():
    with open("model.json","r",encoding="utf-8") as f:
        return json.load(f)

data = get_data()
status_text = ft.Text("uzyj terkstu")

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
        on_select=wybrany_brand,
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
            controls=[
                ft.Text(value=data["data"][0]["brand"], size=20),
                ft.Text(value=data["data"][0]["model"], size=15),
                ft.Text(value=data["data"][0]["year_of_production"], size=10),
                ft.Text(value=data["price"], size=10),
                ft.Image(src=get_watch_image(data["data"][0]["model"]), width=150, height=200),
            ]
        )
    )

    def on_pan_update(e: ft.DragUpdateEvent):
        card_container.offset = ft.Offset(e.local_delta.x / 15, 0)
        card_container.rotate = ft.Rotate(e.local_delta.x / 10)
        card_container.update()

    def on_pan_end(e: ft.DragEndEvent):
        if card_container.offset.x > 0.05:
            print("Like!")
        elif card_container.offset.x < -0.05:
            print("Dislike!")
            
        # Powrót na środek
        card_container.offset = ft.Offset(0, 0)
        card_container.rotate=ft.Rotate(0)
        card_container.update()

    return ft.SafeArea(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(width=50, height=50, icon=ft.icons.Icons.REMOVE_CIRCLE),
                ft.GestureDetector(
                    content=card_container,
                    on_pan_update=on_pan_update,
                    on_pan_end=on_pan_end,
                ),
                ft.IconButton(width=50, height=50, icon=ft.icons.Icons.FAVORITE),
            ]
        )
    )


