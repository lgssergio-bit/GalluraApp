import flet as ft
import os
import time

# --- DATI E LOGICA ---
COMUNI_GALLURA = [
    "Luras", "Calangianus", "Tempio Pausania", "Aggius", "Bortigiadas", 
    "Luogosanto", "Aglientu", "Santa Teresa Gallura", "Palau", "La Maddalena", 
    "Arzachena", "Olbia", "Telti", "Monti", "Berchidda", "Oschiri", 
    "Sant'Antonio di Gallura", "Loiri Porto San Paolo", "Padru", "Budoni", 
    "San Teodoro", "Golfo Aranci", "Trinità d'Agultu", "Badesi", "Viddalba"
]

# --- CLASSE PRIVACY (Simulata per Android - per evitare crash permessi) ---
class PrivacyGuard:
    def registra_utente(self, u, p, c): return True, "Ok"
    def controlla_login(self, u, p): return True 
    def leggi_classifica(self): return [("Calangianus", 15), ("Luras", 12), ("Tempio", 8)]
    def ottieni_tutti_post_ordinati(self): return []
    def salva_solo_metadati_silenzioso(self, p, u): pass 
    def prepara_immagine_forum(self, p): return None
    def registra_post_pubblico(self, f, a, d): pass
    def invia_richiesta_hof(self, f, a, d): pass

# --- INTERFACCIA ---
BG_COLOR = "#121212"
PRIMARY = "#2ecc71"
CARD_COLOR = "#1e1e1e"
GOLD = "#f1c40f"

def main(page: ft.Page):
    page.title = "Gallura Mycelium"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_COLOR
    page.padding = 0
    
    privacy = PrivacyGuard()
    user_state = {"name": None, "role": "Visitatore"}
    
    # --- FILEPICKER (IL CUORE DEL PROBLEMA) ---
    # Lo definiamo e lo aggiungiamo subito all'overlay
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    # Variabile per salvare il percorso temporaneo
    upload_path_temp = [""] 

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            file_obj = e.files[0]
            upload_path_temp[0] = file_obj.path
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Foto caricata: {file_obj.name}"), bgcolor=PRIMARY))
            # Qui aggiorneremmo l'anteprima se fossimo in una pagina specifica
            page.update()
    
    file_picker.on_result = on_file_picked

    # --- NAVIGAZIONE ---
    def cambio_tab(e):
        idx = e.control.selected_index
        page.clean()
        if idx == 0: show_home()
        elif idx == 1: show_upload() # La pagina col FilePicker
        elif idx == 2: show_forum()
        page.add(nav_bar)
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon="home", label="Home"),
            ft.NavigationBarDestination(icon="add_a_photo", label="Carica"),
            ft.NavigationBarDestination(icon="forum", label="Forum"),
        ],
        bgcolor="#222222",
        indicator_color=PRIMARY,
        on_change=cambio_tab
    )

    # --- PAGINE ---
    def show_login():
        page.clean()
        u_tf = ft.TextField(label="Utente", border_color=PRIMARY, color="white")
        p_tf = ft.TextField(label="Password", password=True, border_color=PRIMARY, color="white")
        
        def az_login(e):
            user_state["name"] = u_tf.value if u_tf.value else "Utente"
            show_home()
            page.add(nav_bar)
            page.update()

        page.add(ft.Container(
            content=ft.Column([
                ft.Icon("forest", size=100, color=PRIMARY),
                ft.Text("GALLURA MYCELIUM", size=30, weight="bold", color="white"),
                ft.Container(height=20),
                u_tf, p_tf,
                ft.ElevatedButton("ENTRA", on_click=az_login, bgcolor=PRIMARY, color="white", width=200)
            ], alignment="center", horizontal_alignment="center"),
            padding=20, expand=True, alignment=ft.alignment.center
        ))
        page.update()

    def show_home():
        top3 = privacy.leggi_classifica()
        podio = ft.Column(spacing=5)
        medaglie = ["🥇", "🥈", "🥉"]
        for i, (com, pt) in enumerate(top3):
            med = medaglie[i] if i < 3 else ""
            podio.controls.append(ft.Container(content=ft.Row([ft.Text(med, size=20), ft.Text(com, weight="bold", size=16, expand=True), ft.Text(f"{pt} pt", color=GOLD)]), bgcolor=CARD_COLOR, padding=10, border_radius=10))
        
        page.add(ft.Column([
            ft.Container(content=ft.Text(f"Ciao {user_state['name']}", size=22, weight="bold"), padding=20),
            ft.Container(content=ft.Column([ft.Text("PODIO COMUNI", color=GOLD, weight="bold"), podio]), padding=20, margin=10, bgcolor="#111111", border_radius=15),
        ], expand=True))

    def show_upload():
        # Pagina di Upload funzionante
        page.add(ft.Column([
            ft.Text("CARICA RITROVAMENTO", size=24, weight="bold"),
            ft.Container(height=20),
            ft.ElevatedButton("SCATTA / GALLERIA", icon="camera_alt", 
                              on_click=lambda _: file_picker.pick_files(allow_multiple=False), 
                              bgcolor=PRIMARY, color="white", width=250, height=50),
            ft.Container(height=20),
            ft.Text("Seleziona una foto per guadagnare punti!", color="grey")
        ], alignment="center", horizontal_alignment="center", expand=True))

    def show_forum():
        page.add(ft.Column([
            ft.Text("FORUM (Simulato)", size=24),
            ft.Text("Qui vedrai i post degli altri utenti.")
        ], alignment="center", horizontal_alignment="center", expand=True))

    # AVVIO APP
    show_login()

ft.app(target=main)
