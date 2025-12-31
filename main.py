import flet as ft
import os
import time
from datetime import datetime
from supabase import create_client, Client

# --- 1. CONFIGURAZIONE SUPABASE ---
# Inserisco le tue chiavi verificate dal test
SUPABASE_URL = "https://zdyjwoxfqzpiexuoetyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkeWp3b3hmcXpwaWV4dW9ldHlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNTMzNDAsImV4cCI6MjA4MjcyOTM0MH0.ed0kcRIQm01BPGhLnyzBCsc3KxP82VUDo-6hytJXsn8"
STORAGE_URL = f"{SUPABASE_URL}/storage/v1/object/public/foto_funghi"

# --- 2. GESTORE DATI "ROBUSTO" ---
# Non si connette all'avvio, ma quando serve
class CloudManager:
    def get_client(self):
        try:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
        except:
            return None

    def login(self, u, p):
        client = self.get_client()
        if not client: return None
        try:
            # Cerca utente
            res = client.table("utenti").select("*").eq("username", u).eq("password", p).execute()
            if res.data: return res.data[0]
        except: pass
        return None

    def registra(self, u, p, c):
        client = self.get_client()
        if not client: return False, "Errore Connessione Internet"
        try:
            # Controllo se esiste
            res = client.table("utenti").select("*").eq("username", u).execute()
            if res.data: return False, "Nome utente già preso!"
            
            # Inserisco
            client.table("utenti").insert({"username": u, "password": p, "comune": c}).execute()
            return True, "Registrato con successo!"
        except Exception as e: return False, f"Errore: {str(e)}"

    def carica_classifica(self):
        client = self.get_client()
        punti = {c: 0 for c in COMUNI_GALLURA}
        if not client: return []
        try:
            res = client.table("post").select("comune").execute()
            for r in res.data:
                c = r.get('comune')
                if c in punti: punti[c] += 1
        except: pass
        return sorted(punti.items(), key=lambda x: x[1], reverse=True)

    def upload_foto(self, file_path, file_name):
        client = self.get_client()
        if not client: return False
        try:
            with open(file_path, 'rb') as f:
                client.storage.from_("foto_funghi").upload(file_name, f)
            return True
        except: return False

    def crea_post(self, autore, comune, desc, nome_file):
        client = self.get_client()
        if not client: return False
        try:
            client.table("post").insert({
                "autore": autore, "comune": comune, "descrizione": desc, "image_path": nome_file
            }).execute()
            return True
        except: return False

    def leggi_post(self):
        client = self.get_client()
        if not client: return []
        try:
            return client.table("post").select("*").order("created_at", desc=True).execute().data
        except: return []

    def vota(self, post_id, user, tipo):
        client = self.get_client()
        if not client: return
        try:
            client.table("voti").insert({"post_id": post_id, "user_id": user, "tipo": tipo}).execute()
        except: pass 

    def conta_voti(self, post_id):
        client = self.get_client()
        l, f, w = 0, 0, 0
        if not client: return l,f,w
        try:
            res = client.table("voti").select("tipo").eq("post_id", post_id).execute()
            for r in res.data:
                t = r.get('tipo')
                if t == "Like": l += 1
                elif t == "Fake": f += 1
                elif t == "Wow": w += 1
        except: pass
        return l, f, w

    def commenta(self, post_id, autore, testo):
        client = self.get_client()
        if client:
            try: client.table("commenti").insert({"post_id": post_id, "autore": autore, "testo": testo}).execute()
            except: pass

    def leggi_commenti(self, post_id):
        client = self.get_client()
        if not client: return []
        try:
            return client.table("commenti").select("*").eq("post_id", post_id).order("created_at", desc=True).execute().data
        except: return []

# --- 3. DATI STATICI ---
COMUNI_GALLURA = ["Luras", "Calangianus", "Tempio Pausania", "Aggius", "Bortigiadas", "Luogosanto", "Aglientu", "Santa Teresa Gallura", "Palau", "La Maddalena", "Arzachena", "Olbia", "Telti", "Monti", "Berchidda", "Oschiri", "Sant'Antonio di Gallura", "Loiri Porto San Paolo", "Padru", "Budoni", "San Teodoro", "Golfo Aranci", "Trinità d'Agultu", "Badesi", "Viddalba"]

DB_FUNGHI = {
    "Porcino Nero": {"lat": "Boletus aereus", "desc": "Il Re della macchia.", "full": "Cappello bronzo scuro, gambo panciuto. Eccellente.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Boletus_aereus_3.jpg/640px-Boletus_aereus_3.jpg", "ok": True},
    "Ovolo Reale": {"lat": "Amanita caesarea", "desc": "Arancio vivo, lamelle gialle.", "full": "Cappello arancio, lamelle e gambo GIALLO ORO. Ottimo crudo.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Amanita_caesarea_2.jpg/640px-Amanita_caesarea_2.jpg", "ok": True},
    "Antunna": {"lat": "Pleurotus eryngii", "desc": "Cresce sul cardo.", "full": "Cappello bruno, lamelle decorrenti. Ottimo alla brace.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Pleurotus_eryngii_Mallorca.jpg/640px-Pleurotus_eryngii_Mallorca.jpg", "ok": True},
    "Mazza di Tamburo": {"lat": "Macrolepiota procera", "desc": "Gigante tigrato.", "full": "Gambo alto con anello mobile. Si mangia solo il cappello.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Macrolepiota_procera_bg.jpg/640px-Macrolepiota_procera_bg.jpg", "ok": True},
    "Tignosa Verdognola": {"lat": "Amanita phalloides", "desc": "MORTALE.", "full": "MORTALE. Cappello verde/giallo, volva bianca.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Amanita_phalloides_1.JPG/640px-Amanita_phalloides_1.JPG", "ok": False},
    "Ovolo Malefico": {"lat": "Amanita muscaria", "desc": "Rosso a puntini bianchi.", "full": "Rosso con verruche bianche. Lamelle BIANCHE. Tossico.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Amanita_muscaria_3_vliegenzwammen_op_rij.jpg/640px-Amanita_muscaria_3_vliegenzwammen_op_rij.jpg", "ok": False}
}

# --- 4. INTERFACCIA ---
BG_COLOR = "#121212"
PRIMARY = "#2ecc71"
CARD_COLOR = "#1e1e1e"
GOLD = "#f1c40f"

def main(page: ft.Page):
    page.title = "Gallura Mycelium"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_COLOR
    page.padding = 0
    
    cloud = CloudManager()
    user_state = {"name": None, "comune": None}

    # Setup FilePicker
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    img_temp = ft.Image(src="", visible=False, height=200, fit=ft.ImageFit.CONTAIN)
    upload_path_box = [""] 

    def on_file(e: ft.FilePickerResultEvent):
        if e.files:
            f = e.files[0]
            upload_path_box[0] = f.path
            img_temp.src = f.path
            img_temp.visible = True
            page.update()
    file_picker.on_result = on_file

    def cambio_tab(e):
        i = e.control.selected_index
        page.clean()
        if i == 0: show_home()
        elif i == 1: show_guida()
        elif i == 2: show_upload()
        elif i == 3: show_forum()
        page.add(nav_bar)
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon="home", label="Home"),
            ft.NavigationBarDestination(icon="menu_book", label="Guida"),
            ft.NavigationBarDestination(icon="add_a_photo", label="Carica"),
            ft.NavigationBarDestination(icon="forum", label="Forum"),
        ],
        bgcolor="#222222", indicator_color=PRIMARY, on_change=cambio_tab
    )

    # --- SCHERMATE ---
    def show_login():
        page.clean()
        u = ft.TextField(label="Utente", border_color=PRIMARY)
        p = ft.TextField(label="Password", password=True, border_color=PRIMARY)
        
        def az_log(e):
            page.show_snack_bar(ft.SnackBar(ft.Text("Connessione in corso...")))
            page.update()
            data = cloud.login(u.value, p.value)
            if data:
                user_state["name"] = data['username']
                user_state["comune"] = data['comune']
                show_home()
                page.add(nav_bar)
            else: 
                page.show_snack_bar(ft.SnackBar(ft.Text("Login fallito. Controlla utente/password.")))
            page.update()
            
        def az_reg(e): show_register()

        page.add(ft.Container(content=ft.Column([
            ft.Icon("forest", size=100, color=PRIMARY),
            ft.Text("GALLURA MYCELIUM", size=30, weight="bold"),
            ft.Container(height=20), u, p,
            ft.ElevatedButton("ENTRA", on_click=az_log, bgcolor=PRIMARY, color="white", width=200),
            ft.TextButton("Non hai un account? Registrati", on_click=az_reg)
        ], alignment="center", horizontal_alignment="center"), padding=20, expand=True, alignment=ft.alignment.center))
        page.update()

    def show_register():
        page.clean()
        u = ft.TextField(label="Scegli Utente"); p = ft.TextField(label="Scegli Password", password=True)
        c = ft.Dropdown(label="Comune", options=[ft.dropdown.Option(x) for x in COMUNI_GALLURA])
        
        def az_fai_reg(e):
            if not u.value or not p.value or not c.value:
                page.show_snack_bar(ft.SnackBar(ft.Text("Compila tutti i campi!"))); page.update(); return
                
            page.show_snack_bar(ft.SnackBar(ft.Text("Registrazione in corso...")))
            page.update()
            
            ok, msg = cloud.registra(u.value, p.value, c.value)
            page.show_snack_bar(ft.SnackBar(ft.Text(msg)))
            if ok: 
                time.sleep(1)
                show_login()
            page.update()

        page.add(ft.Column([
            ft.Text("NUOVO UTENTE", size=24, weight="bold"),
            u, p, c,
            ft.Container(height=20),
            ft.ElevatedButton("REGISTRATI ORA", on_click=az_fai_reg, bgcolor=PRIMARY, color="white", width=200),
            ft.TextButton("Torna indietro", on_click=lambda _: show_login())
        ], horizontal_alignment="center", padding=20))
        page.update()

    def show_home():
        classifica = cloud.carica_classifica()
        items = []
        for i, (com, pt) in enumerate(classifica[:5]):
            col = GOLD if i==0 else "white"
            items.append(ft.Container(content=ft.Row([ft.Text(f"{i+1}.", color=col, size=18), ft.Text(com, size=18, expand=True), ft.Text(str(pt), weight="bold", color=col)]), bgcolor=CARD_COLOR, padding=10, border_radius=5))
        
        page.add(ft.Column([
            ft.Container(content=ft.Text(f"Ciao {user_state['name']}!", size=24, weight="bold"), padding=20),
            ft.Container(content=ft.Column([ft.Text("PODIO GALLURA", color=GOLD), ft.Column(items)]), padding=20, bgcolor="#111111", border_radius=10, margin=10)
        ], expand=True))

    def show_guida():
        lv = ft.ListView(expand=True, spacing=10, padding=10)
        for k, v in DB_FUNGHI.items():
            col = PRIMARY if v["ok"] else "#e74c3c"
            lv.controls.append(ft.Container(content=ft.Column([
                ft.Image(src=v["img"], height=150, fit=ft.ImageFit.COVER, border_radius=10),
                ft.Text(k, size=20, weight="bold", color=col),
                ft.Text(v["desc"])
            ]), bgcolor=CARD_COLOR, padding=10, border_radius=10))
        page.add(ft.Column([ft.Text("GUIDA", size=24), lv], padding=10, expand=True))

    def show_upload():
        desc = ft.TextField(label="Descrizione")
        def az_pubblica(e):
            if not upload_path_box[0]: 
                page.show_snack_bar(ft.SnackBar(ft.Text("Devi scegliere una foto!"))); page.update(); return
            
            nome_file = f"{int(time.time())}_{user_state['name']}.jpg"
            page.show_snack_bar(ft.SnackBar(ft.Text("Caricamento...")))
            page.update()
            
            if cloud.upload_foto(upload_path_box[0], nome_file):
                cloud.crea_post(user_state['name'], user_state['comune'], desc.value, nome_file)
                page.show_snack_bar(ft.SnackBar(ft.Text("Fungo Pubblicato!"), bgcolor="green"))
                img_temp.visible = False; desc.value = ""
                show_forum(); page.add(nav_bar)
            else: page.show_snack_bar(ft.SnackBar(ft.Text("Errore Upload")))
            page.update()

        page.add(ft.Column([
            ft.Text("CARICA", size=24),
            ft.ElevatedButton("SCATTA FOTO", on_click=lambda _: file_picker.pick_files(), bgcolor=PRIMARY, color="white"),
            ft.Container(content=img_temp), desc,
            ft.ElevatedButton("PUBBLICA", on_click=az_pubblica, bgcolor="#333333", color="white")
        ], padding=20, horizontal_alignment="center"))
        page.update()

    def show_forum():
        lv = ft.ListView(expand=True, spacing=15, padding=10)
        posts = cloud.leggi_post()
        if not posts: lv.controls.append(ft.Text("Nessun post ancora."))
        
        for p in posts:
            img_url = f"{STORAGE_URL}/{p['image_path']}"
            card = ft.Container(content=ft.Column([
                ft.Text(f"{p['autore']} a {p['comune']}", weight="bold"),
                ft.Image(src=img_url, height=200, fit=ft.ImageFit.COVER, border_radius=10),
                ft.Text(p['descrizione'])
            ]), bgcolor=CARD_COLOR, padding=10, border_radius=10)
            lv.controls.append(card)
        page.add(ft.Column([ft.Text("FORUM", size=24), lv], padding=10, expand=True))

    show_login()

ft.app(target=main)
