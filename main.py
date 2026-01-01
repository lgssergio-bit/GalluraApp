import flet as ft

def main(page: ft.Page):
    page.title = "TEST VERSIONE"
    page.bgcolor = "black"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # Leggiamo la versione reale installata nel telefono
    versione_installata = ft.version
    
    msg = ft.Text(f"Versione Flet: {versione_installata}", size=30, color="white", weight="bold")
    
    # Istruzioni
    info = ft.Text("Se leggi '0.21' o inferiore, l'app è VECCHIA.\nSe leggi '0.25.2', l'app è NUOVA.", 
                   color="yellow", text_align="center")

    page.add(ft.Column([
        ft.Icon("build", size=50, color="orange"),
        msg,
        ft.Container(height=20),
        info
    ], alignment="center", horizontal_alignment="center"))

ft.app(target=main)
