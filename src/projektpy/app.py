import flet as ft
import json
from .apiconnect import get_Image 
def start():
    ft.run(createapp)   
def get_data():
    with open("dane.json","r",encoding="utf-8") as f:
        return json.load(f)

data = get_data()
def createapp(page: ft.Page):
    page.title = "WatchFinder"
    page.add(ft.Text("Projekt Py"))
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(search_bar())
    page.add(create_card())

def search_bar():
    return ft.SafeArea(
        content=ft.Container(
            width=300,
            border=ft.border.Border.all(color=ft.Colors.BLUE),
            border_radius=10,
            padding=5,
            content=ft.Row(
                controls=[
                ft.TextField(label="Search",expand=True, border=ft.InputBorder.NONE),
                ft.IconButton(icon=ft.Icons.SEARCH)
            ]),
        ),
    )
    
def create_card():
    return ft.SafeArea(
        content=ft.Card(
            content=ft.Container(
                padding=20,
                width=300,
                height=400,
                border_radius=10,
                border=ft.border.Border.all(color=ft.Colors.BLUE),
                bgcolor=ft.Colors.WHITE_30,
                content=ft.Column(
                    controls=[
                        ft.Text(value=data["watches"][0]["makeName"],size=20),
                        ft.Text(value=data["watches"][0]["modelName"],size=10),
                        ft.Text(value=data["watches"][0]["yearProducedName"],size=10),
                        # ft.Image(src_base64=get_Image(data["watches"][0]["watchImageName"]),width=20,height=20),
                                                
                    ]
                
                )
            )
        )
    )

