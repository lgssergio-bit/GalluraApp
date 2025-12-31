import flet as ft
import os
import time
from supabase import create_client, Client

# --- CONFIGURAZIONE SUPABASE (I tuoi dati) ---
SUPABASE_URL = "https://zdyjwoxfqzpiexuoetyq.supabase.co"
SUPABASE_KEY = "sb_publishable_sr2w8GBSM-dQZ8klkb704A_y-9Wf91t" # (Questa è una chiave pubblica, va bene nell'app)

# Creiamo il collegamento
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    DB_ATTIVO = True
except:
    DB_ATTIVO = False

# --- DATI GLOBALI ---
COMUNI_GALLURA = [
    "Luras", "Calangianus", "Tempio Pausania", "Aggius", "Bortigiadas", 
    "Luogosanto", "Aglientu", "Santa Teresa Gallura", "Palau", "La Maddalena", 
    "Arzachena", "Olbia", "Telti", "Monti", "Berchidda", "Oschiri", 
    "Sant'Antonio di Gallura", "Loiri Porto San Paolo", "Padru", "Budoni", 
    "San Teodoro", "Golfo Aranci", "Trinità d'Agultu", "Badesi", "Viddalba"
]

# --- CLASSE GESTIONE DATI (CLOUD) ---
class DataManager:
    def registra_utente(self, u, p, c):
        if not DB_ATTIVO: return False, "No Internet"
        try:
            # Controllo se esiste già
            res = supabase.table("utenti").select("*").eq("username", u).execute()
            if res.data: return False, "Utente già esistente"
            
            # Inserisco
            supabase.table("utenti").insert({"username": u, "password": p, "comune": c}).execute()
            return True, "Registrato!"
        except Exception as e:
            return False, f"Errore: {str(e)}"

    def controlla_login(self, u, p):
        if not DB_ATTIVO: return False
        try:
            res = supabase.table("utenti").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                return res.data[0]['comune'] # Restituisco il comune dell'utente
            return None
        except:
            return None

    def carica_classifica(self):
        # Calcola i punti contando i post per comune
        punti = {c: 0 for c in COMUNI_GALLURA}
        try:
            if DB_ATTIVO:
                # Scarica tutti i post (per ora semplice)
                res = supabase.table("post").select("comune").execute()
                for r in res.data:
                    c = r['comune']
                    if c in punti: punti[c] += 1
        except: pass
        # Ordina
        return sorted(punti.items(), key=lambda x: x[1], reverse=True)

    def invia_post(self, autore, comune, descrizione):
        if not DB_ATTIVO: return False
        try:
            supabase.table("post").insert({
                "autore": autore,
                "comune": comune,
                "descrizione": descrizione,
                "image_path": "pending" # Per ora non carichiamo il file binario, solo il dato
            }).execute()
            return True
        except: return False

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
    
    db = DataManager()
    user_state = {"name": None, "comune": None}

    # --- FILEPICKER ---
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    img_preview = ft.Image(src="", visible=False, height=250, fit=ft.ImageFit.CONTAIN)
    
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            file_obj = e.files[0]
            img_preview.src = file_obj.path
            img_preview.visible = True
            page.update()
    
    file_picker.on_result = on_file_picked

    # --- FUNZIONI NAVIGAZIONE ---
    def cambio_tab(e):
        idx = e.control.selected_index
        page.clean()
        if idx == 0: show_home()
        elif idx == 1: show_upload()
        elif idx == 2: show_info()
        page.add(nav_bar)
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon="home", label="Home"),
            ft.NavigationBarDestination(icon="add_a_photo", label="Carica"),
            ft.NavigationBarDestination(icon="info", label="Info"),
        ],
        bgcolor="#222222", indicator_color=PRIMARY, on_change=cambio_tab
    )

    # --- PAGINE ---
    def show_login():
        page.clean()
        u_tf = ft.TextField(label="Utente", border_color=PRIMARY)
        p_tf = ft.TextField(label="Password", password=True, border_color=PRIMARY)
        
        def az_login(e):
            comune = db.controlla_login(u_tf.value, p_tf.value)
            if comune:
                user_state["name"] = u_tf.value
                user_state["comune"] = comune
                show_home()
                page.add(nav_bar)
            else:
                page.show_snack_bar(ft.SnackBar(ft.Text("Login fallito! Registrati prima.")))
            page.update()
        
        def vai_reg(e): show_register()

        page.add(ft.Container(
            content=ft.Column([
                ft.Icon("forest", size=100, color=PRIMARY),
                ft.Text("GALLURA MYCELIUM", size=30, weight="bold"),
                ft.Text("Online Database", size=12, color="grey"),
                ft.Container(height=20),
                u_tf, p_tf,
                ft.ElevatedButton("ENTRA", on_click=az_login, bgcolor=PRIMARY, color="white", width=200),
                ft.TextButton("Non hai un account? Registrati", on_click=vai_reg)
            ], alignment="center", horizontal_alignment="center"),
            padding=20, expand=True, alignment=ft.alignment.center
        ))
        page.update()

    def show_register():
        page.clean()
        u_tf = ft.TextField(label="Scegli Utente")
        p_tf = ft.TextField(label="Scegli Password", password=True)
        c_dd = ft.Dropdown(label="Il tuo Comune", options=[ft.dropdown.Option(c) for c in COMUNI_GALLURA])

        def az_reg(e):
            if not u_tf.value or not p_tf.value or not c_dd.value: return
            ok, msg = db.registra_utente(u_tf.value, p_tf.value, c_dd.value)
            page.show_snack_bar(ft.SnackBar(ft.Text(msg)))
            if ok: show_login()
            page.update()

        page.add(ft.Column([
            ft.Text("NUOVO UTENTE", size=24),
            u_tf, p_tf, c_dd,
            ft.ElevatedButton("REGISTRATI", on_click=az_reg, bgcolor=PRIMARY, color="white"),
            ft.TextButton("Torna al Login", on_click=lambda e: show_login())
        ], horizontal_alignment="center", padding=20))
        page.update()

    def show_home():
        # Carica classifica dal DB
        top_list = db.carica_classifica()
        
        items = []
        medaglie = ["🥇", "🥈", "🥉"]
        for i, (com, pt) in enumerate(top_list):
            if pt > 0: # Mostra solo chi ha punti
                med = medaglie[i] if i < 3 else f"{i+1}."
                items.append(ft.Container(
                    content=ft.Row([ft.Text(med, size=20), ft.Text(com, size=18, expand=True), ft.Text(f"{pt}", color=GOLD, weight="bold")], alignment="spaceBetween"),
                    bgcolor=CARD_COLOR, padding=15, border_radius=10, margin=2
                ))
        
        if not items: items.append(ft.Text("Ancora nessun punto. Inizia tu!", color="grey"))

        page.add(ft.Column([
            ft.Container(content=ft.Text(f"Ciao {user_state['name']} ({user_state['comune']})", size=20, weight="bold"), padding=20),
            ft.Container(content=ft.Column([ft.Text("CLASSIFICA LIVE", color=GOLD, weight="bold"), ft.Column(items)]), padding=20, margin=10, bgcolor="#111111", border_radius=15),
        ], expand=True))

    def show_upload():
        desc_tf = ft.TextField(label="Descrizione (opzionale)")
        
        def az_invia(e):
            # Per ora salviamo solo i dati testuali nel DB per evitare complessità
            if db.invia_post(user_state['name'], user_state['comune'], desc_tf.value):
                page.show_snack_bar(ft.SnackBar(ft.Text("Ritrovamento Segnalato! +1 Punto"), bgcolor="green"))
                # Pulisce
                img_preview.visible = False
                img_preview.src = ""
                desc_tf.value = ""
            else:
                page.show_snack_bar(ft.SnackBar(ft.Text("Errore di connessione"), bgcolor="red"))
            page.update()

        page.add(ft.Column([
            ft.Text("NUOVO RITROVAMENTO", size=20, weight="bold"),
            ft.ElevatedButton("SCATTA FOTO", icon="camera_alt", on_click=lambda _: file_picker.pick_files(), bgcolor=PRIMARY, color="white"),
            ft.Container(content=img_preview, alignment=ft.alignment.center, padding=10),
            desc_tf,
            ft.ElevatedButton("PUBBLICA E GUADAGNA PUNTI", on_click=az_invia, bgcolor="#444444", color="white", width=300)
        ], horizontal_alignment="center", padding=20, scroll=ft.ScrollMode.AUTO, expand=True))

    def show_info():
        page.add(ft.Container(content=ft.Text("Versione Cloud 1.0\nPowered by Supabase", text_align="center"), alignment=ft.alignment.center, expand=True))

    show_login()

ft.app(target=main)
