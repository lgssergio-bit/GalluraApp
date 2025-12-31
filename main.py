import flet as ft
import os
import hashlib
import time
from datetime import datetime

# --- DATI ---
COMUNI_GALLURA = [
    "Luras", "Calangianus", "Tempio Pausania", "Aggius", "Bortigiadas", 
    "Luogosanto", "Aglientu", "Santa Teresa Gallura", "Palau", "La Maddalena", 
    "Arzachena", "Olbia", "Telti", "Monti", "Berchidda", "Oschiri", 
    "Sant'Antonio di Gallura", "Loiri Porto San Paolo", "Padru", "Budoni", 
    "San Teodoro", "Golfo Aranci", "Trinità d'Agultu", "Badesi", "Viddalba"
]

# --- MOTORE FITTIZIO PER APK (Senza salvataggio su disco per evitare crash permessi) ---
class PrivacyGuard:
    def registra_utente(self, u, p, c): return True, "Ok" # Simulato
    def controlla_login(self, u, p): return True # Fa entrare chiunque per test
    def leggi_classifica(self): return [("Calangianus", 10), ("Luras", 8), ("Tempio", 5)]
    def ottieni_tutti_post_ordinati(self): return []
    def salva_solo_metadati_silenzioso(self, p, u): pass
    def prepara_immagine_forum(self, p): return None
    def registra_post_pubblico(self, f, a, d): pass
    def invia_richiesta_hof(self, f, a, d): pass
    def invia_notifica(self, a, m, pid, t): pass

# --- INTERFACCIA ---
BG_COLOR = "#121212"
PRIMARY = "#2ecc71"
CARD_COLOR = "#1e1e1e"

def main(page: ft.Page):
    page.title = "Gallura Mycelium"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_COLOR
    
    privacy = PrivacyGuard()
    
    # FilePicker configurato correttamente
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Foto selezionata: {e.files[0].name}"), bgcolor="green"))
            page.update()
            
    file_picker.on_result = on_file_result

    def cambio_tab(e):
        idx = e.control.selected_index
        page.clean()
        if idx == 0: show_home()
        elif idx == 1: show_upload()
        elif idx == 2: show_info()
        page.navigation_bar.selected_index = idx
        page.add(page.navigation_bar)
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon="home", label="Home"),
            ft.NavigationBarDestination(icon="add_a_photo", label="Carica"),
            ft.NavigationBarDestination(icon="info", label="Info"),
        ],
        bgcolor="#222222",
        indicator_color=PRIMARY,
        on_change=cambio_tab
    )
    page.navigation_bar = nav_bar

    def show_home():
        page.add(ft.Column([
            ft.Text("GALLURA MYCELIUM", size=30, weight="bold", color=PRIMARY),
            ft.Text("Benvenuto nell'App Ufficiale", size=16),
            ft.Container(height=20),
            ft.Text("Classifica Rapida:", weight="bold"),
            ft.Text("1. Calangianus - 10 pt", color="yellow"),
            ft.Text("2. Luras - 8 pt", color="white"),
        ], alignment="center", horizontal_alignment="center"))

    def show_upload():
        page.add(ft.Column([
            ft.Text("CARICA RITROVAMENTO", size=24),
            ft.ElevatedButton("SCATTA / GALLERIA", icon="camera_alt", 
                              on_click=lambda _: file_picker.pick_files(), 
                              bgcolor=PRIMARY, color="white")
        ], alignment="center", horizontal_alignment="center"))

    def show_info():
        page.add(ft.Column([ft.Text("Versione 1.0 - Build Android")]))

    # Avvio diretto alla Home per test
    show_home() 

ft.app(target=main)