import flet as ft
import json
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
                        ft.Text(value=data["data"][0]["brand"],size=20),
                        ft.Text(value=data["data"][0]["model"],size=15),
                        ft.Text(value=data["data"][0]["year_of_production"],size=10),
                        
                        # ft.Image(src=data["data"]["model"],width=100,height=100),
                                                
                    ]
                
                )
            )
        )
    )


