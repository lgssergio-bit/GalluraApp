import flet as ft

def main(page: ft.Page):
    page.title = "TEST VERSIONE REALE"
    page.bgcolor = "black"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # COMANDO CORRETTO: Legge il numero della versione (es. 0.25.2)
    numero_versione = ft.__version__
    
    colore = "green" if "0.25" in numero_versione else "red"
    
    page.add(ft.Column([
        ft.Icon("info", size=60, color=colore),
        ft.Text("VERSIONE RILEVATA:", color="white"),
        ft.Text(numero_versione, size=40, weight="bold", color=colore),
        ft.Container(height=20),
        ft.Text("Se leggi 0.25.2 -> Il problema è l'APK misto.\nSe leggi altro -> Il problema è requirements.txt", 
                text_align="center", color="grey")
    ], alignment="center", horizontal_alignment="center"))

ft.app(target=main)
