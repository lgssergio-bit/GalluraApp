import flet as ft
import os

# --- DATI FINTI (Per ora, finché non colleghiamo il Cloud) ---
COMUNI_GALLURA = ["Calangianus", "Luras", "Tempio", "Olbia"]

def main(page: ft.Page):
    page.title = "Gallura Mycelium"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 0

    PRIMARY = "#2ecc71"
    
    # --- 1. CONFIGURAZIONE FOTOCAMERA ---
    # Variabile che conterrà l'immagine selezionata
    img_preview = ft.Image(src="", visible=False, height=300, fit=ft.ImageFit.CONTAIN)
    text_status = ft.Text("", color="yellow")

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            file_obj = e.files[0]
            # AGGIORNAMENTO GRAFICO: Mostra la foto
            img_preview.src = file_obj.path
            img_preview.visible = True
            text_status.value = f"Pronta per l'upload: {file_obj.name}"
            # Se siamo nella pagina di upload, aggiorniamo la vista
            page.update()

    file_picker.on_result = on_file_picked

    # --- NAVIGAZIONE ---
    def cambio_tab(e):
        idx = e.control.selected_index
        page.clean()
        if idx == 0: show_home()
        elif idx == 1: show_upload()
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

    def show_home():
        page.add(ft.Container(
            content=ft.Column([
                ft.Icon("forest", size=80, color=PRIMARY),
                ft.Text("BENTORNATO!", size=24, weight="bold"),
                ft.Text("Il Database è ancora locale.", color="grey"),
                ft.Container(height=20),
                # Classifica finta per estetica
                ft.Container(content=ft.Row([ft.Text("🥇 Calangianus", size=18), ft.Text("15 pt", color="yellow")], alignment="spaceBetween"), bgcolor="#1e1e1e", padding=15, border_radius=10),
                ft.Container(content=ft.Row([ft.Text("🥈 Luras", size=18), ft.Text("12 pt", color="yellow")], alignment="spaceBetween"), bgcolor="#1e1e1e", padding=15, border_radius=10),
            ], horizontal_alignment="center"),
            padding=20, alignment=ft.alignment.center, expand=True
        ))

    def show_upload():
        page.add(ft.Column([
            ft.Text("NUOVO RITROVAMENTO", size=20, weight="bold"),
            ft.Container(height=10),
            
            # Pulsante Scatto
            ft.ElevatedButton("SCATTA / GALLERIA", icon="camera_alt", 
                              on_click=lambda _: file_picker.pick_files(allow_multiple=False), 
                              bgcolor=PRIMARY, color="white", width=250, height=50),
            
            ft.Container(height=20),
            
            # QUI APPARIRÀ LA FOTO
            ft.Container(content=img_preview, border=ft.border.all(1, "grey"), border_radius=10, alignment=ft.alignment.center),
            text_status,

            ft.Container(height=20),
            ft.ElevatedButton("INVIA AL DATABASE", bgcolor="#333333", color="white") 
        ], horizontal_alignment="center", padding=20, scroll=ft.ScrollMode.AUTO, expand=True))

    def show_forum():
        page.add(ft.Column([ft.Text("Area Condivisa (In Costruzione)")], alignment="center", horizontal_alignment="center", expand=True))

    show_home()
    page.add(nav_bar)

ft.app(target=main)
