import flet as ft
import os
import time
from datetime import datetime
from supabase import create_client, Client

# --- 1. CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = "https://zdyjwoxfqzpiexuoetyq.supabase.co"
# Inserisco la TUA chiave ANON (quella pubblica corretta)
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkeWp3b3hmcXpwaWV4dW9ldHlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNTMzNDAsImV4cCI6MjA4MjcyOTM0MH0.ed0kcRIQm01BPGhLnyzBCsc3KxP82VUDo-6hytJXsn8"

# URL base per scaricare le immagini (bucket 'foto_funghi')
STORAGE_URL = f"{SUPABASE_URL}/storage/v1/object/public/foto_funghi"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    DB_ATTIVO = True
except:
    DB_ATTIVO = False

# --- 2. DATI GUIDA E COMUNI ---
COMUNI_GALLURA = ["Luras", "Calangianus", "Tempio Pausania", "Aggius", "Bortigiadas", "Luogosanto", "Aglientu", "Santa Teresa Gallura", "Palau", "La Maddalena", "Arzachena", "Olbia", "Telti", "Monti", "Berchidda", "Oschiri", "Sant'Antonio di Gallura", "Loiri Porto San Paolo", "Padru", "Budoni", "San Teodoro", "Golfo Aranci", "Trinità d'Agultu", "Badesi", "Viddalba"]

DB_FUNGHI = {
    "Porcino Nero": {"lat": "Boletus aereus", "desc": "Il Re della macchia.", "full": "Cappello bronzo scuro, gambo panciuto. Eccellente.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Boletus_aereus_3.jpg/640px-Boletus_aereus_3.jpg", "ok": True},
    "Ovolo Reale": {"lat": "Amanita caesarea", "desc": "Arancio vivo, lamelle gialle.", "full": "Cappello arancio, lamelle e gambo GIALLO ORO. Ottimo crudo.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Amanita_caesarea_2.jpg/640px-Amanita_caesarea_2.jpg", "ok": True},
    "Antunna": {"lat": "Pleurotus eryngii", "desc": "Cresce sul cardo.", "full": "Cappello bruno, lamelle decorrenti. Ottimo alla brace.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Pleurotus_eryngii_Mallorca.jpg/640px-Pleurotus_eryngii_Mallorca.jpg", "ok": True},
    "Mazza di Tamburo": {"lat": "Macrolepiota procera", "desc": "Gigante tigrato.", "full": "Gambo alto con anello mobile. Si mangia solo il cappello.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Macrolepiota_procera_bg.jpg/640px-Macrolepiota_procera_bg.jpg", "ok": True},
    "Tignosa Verdognola": {"lat": "Amanita phalloides", "desc": "MORTALE.", "full": "MORTALE. Cappello verde/giallo, volva bianca.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Amanita_phalloides_1.JPG/640px-Amanita_phalloides_1.JPG", "ok": False},
    "Ovolo Malefico": {"lat": "Amanita muscaria", "desc": "Rosso a puntini bianchi.", "full": "Rosso con verruche bianche. Lamelle BIANCHE. Tossico.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Amanita_muscaria_3_vliegenzwammen_op_rij.jpg/640px-Amanita_muscaria_3_vliegenzwammen_op_rij.jpg", "ok": False}
}

# --- 3. GESTORE DATI CLOUD ---
class CloudManager:
    def login(self, u, p):
        if not DB_ATTIVO: return None
        try:
            # Cerca utente
            res = supabase.table("utenti").select("*").eq("username", u).eq("password", p).execute()
            if res.data: return res.data[0]
        except Exception as e: 
            print(f"Err login: {e}")
        return None

    def registra(self, u, p, c):
        if not DB_ATTIVO: return False, "Offline"
        try:
            res = supabase.table("utenti").select("*").eq("username", u).execute()
            if res.data: return False, "Utente esiste già"
            supabase.table("utenti").insert({"username": u, "password": p, "comune": c}).execute()
            return True, "Ok"
        except Exception as e: return False, str(e)

    def carica_classifica(self):
        punti = {c: 0 for c in COMUNI_GALLURA}
        try:
            res = supabase.table("post").select("comune").execute()
            for r in res.data:
                c = r.get('comune')
                if c in punti: punti[c] += 1
        except: pass
        return sorted(punti.items(), key=lambda x: x[1], reverse=True)

    def upload_foto(self, file_path, file_name):
        try:
            with open(file_path, 'rb') as f:
                supabase.storage.from_("foto_funghi").upload(file_name, f)
            return True
        except Exception as e:
            print(f"Errore upload: {e}")
            return False

    def crea_post(self, autore, comune, desc, nome_file):
        try:
            supabase.table("post").insert({
                "autore": autore, "comune": comune, "descrizione": desc, "image_path": nome_file
            }).execute()
            return True
        except: return False

    def leggi_post(self):
        try:
            return supabase.table("post").select("*").order("created_at", desc=True).execute().data
        except: return []

    def vota(self, post_id, user, tipo):
        try:
            supabase.table("voti").insert({"post_id": post_id, "user_id": user, "tipo": tipo}).execute()
            return True
        except: return False 

    def conta_voti(self, post_id):
        l, f, w = 0, 0, 0
        try:
            res = supabase.table("voti").select("tipo").eq("post_id", post_id).execute()
            for r in res.data:
                t = r.get('tipo')
                if t == "Like": l += 1
                elif t == "Fake": f += 1
                elif t == "Wow": w += 1
        except: pass
        return l, f, w

    def commenta(self, post_id, autore, testo):
        try:
            supabase.table("commenti").insert({"post_id": post_id, "autore": autore, "testo": testo}).execute()
        except: pass

    def leggi_commenti(self, post_id):
        try:
            return supabase.table("commenti").select("*").eq("post_id", post_id).order("created_at", desc=True).execute().data
        except: return []

# --- 4. INTERFACCIA ---
BG_COLOR = "#121212"
PRIMARY = "#2ecc71"
SECONDARY = "#e74c3c"
CARD_COLOR = "#1e1e1e"
GOLD = "#f1c40f"

def main(page: ft.Page):
    page.title = "Gallura Mycelium"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_COLOR
    page.padding = 0
    
    cloud = CloudManager()
    user_state = {"name": None, "comune": None}

    # --- FILEPICKER ---
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

    # --- NAVIGAZIONE ---
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
            page.show_snack_bar(ft.SnackBar(ft.Text("Accesso in corso...")))
            page.update()
            data = cloud.login(u.value, p.value)
            if data:
                user_state["name"] = data['username']
                user_state["comune"] = data['comune']
                show_home()
                page.add(nav_bar)
            else: page.show_snack_bar(ft.SnackBar(ft.Text("Login errato o Utente non trovato")))
            page.update()
            
        def az_reg(e): show_register()

        page.add(ft.Container(content=ft.Column([
            ft.Icon("forest", size=100, color=PRIMARY),
            ft.Text("GALLURA MYCELIUM", size=30, weight="bold"),
            ft.Container(height=20), u, p,
            ft.ElevatedButton("ENTRA", on_click=az_log, bgcolor=PRIMARY, color="white", width=200),
            ft.TextButton("Registrati", on_click=az_reg)
        ], alignment="center", horizontal_alignment="center"), padding=20, expand=True, alignment=ft.alignment.center))
        page.update()

    def show_register():
        page.clean()
        u = ft.TextField(label="Scegli Utente"); p = ft.TextField(label="Scegli Password", password=True)
        c = ft.Dropdown(label="Comune", options=[ft.dropdown.Option(x) for x in COMUNI_GALLURA])
        
        def az_fai_reg(e):
            if not u.value or not p.value or not c.value:
                page.show_snack_bar(ft.SnackBar(ft.Text("Compila tutto!"))); page.update(); return
                
            ok, msg = cloud.registra(u.value, p.value, c.value)
            page.show_snack_bar(ft.SnackBar(ft.Text(msg)))
            if ok: 
                time.sleep(1)
                show_login()
            page.update()

        page.add(ft.Column([
            ft.Text("REGISTRAZIONE", size=24), 
            u, p, c, 
            ft.ElevatedButton("CREA ACCOUNT", on_click=az_fai_reg, bgcolor=PRIMARY, color="white")
        ], padding=20, horizontal_alignment="center"))
        page.update()

    def show_home():
        classifica = cloud.carica_classifica()
        items = []
        for i, (com, pt) in enumerate(classifica[:5]):
            col = GOLD if i==0 else "white"
            items.append(ft.Container(content=ft.Row([ft.Text(f"{i+1}.", color=col, size=18), ft.Text(com, size=18, expand=True), ft.Text(str(pt), weight="bold", color=col)]), bgcolor=CARD_COLOR, padding=10, border_radius=5))
        
        page.add(ft.Column([
            ft.Container(content=ft.Text(f"Ciao {user_state['name']} ({user_state['comune']})", size=24, weight="bold"), padding=20),
            ft.Container(content=ft.Column([ft.Text("PODIO ATTUALE", color=GOLD), ft.Column(items)]), padding=20, bgcolor="#111111", border_radius=10, margin=10)
        ], expand=True))

    def show_guida():
        lv = ft.ListView(expand=True, spacing=10, padding=10)
        for k, v in DB_FUNGHI.items():
            col = PRIMARY if v["ok"] else SECONDARY
            lv.controls.append(ft.Container(
                content=ft.Column([
                    ft.Image(src=v["img"], height=150, fit=ft.ImageFit.COVER, border_radius=10),
                    ft.Text(k, size=20, weight="bold", color=col),
                    ft.Text(v["lat"], italic=True, size=12),
                    ft.Text(v["full"])
                ]), bgcolor=CARD_COLOR, padding=10, border_radius=10
            ))
        page.add(ft.Column([ft.Text("GUIDA FUNGHI", size=24, weight="bold"), lv], padding=10, expand=True))

    def show_upload():
        desc = ft.TextField(label="Descrizione")
        def az_pubblica(e):
            if not upload_path_box[0]: 
                page.show_snack_bar(ft.SnackBar(ft.Text("Manca la foto!"))); page.update(); return
            
            nome_file = f"{int(time.time())}_{user_state['name']}.jpg"
            
            page.show_snack_bar(ft.SnackBar(ft.Text("Caricamento foto in corso...")))
            page.update()
            
            if cloud.upload_foto(upload_path_box[0], nome_file):
                if cloud.crea_post(user_state['name'], user_state['comune'], desc.value, nome_file):
                    page.show_snack_bar(ft.SnackBar(ft.Text("Pubblicato!"), bgcolor="green"))
                    img_temp.src = ""; img_temp.visible = False; desc.value = ""; upload_path_box[0] = ""
                    show_forum()
                    page.add(nav_bar)
                else: page.show_snack_bar(ft.SnackBar(ft.Text("Errore Salvataggio Post")))
            else: page.show_snack_bar(ft.SnackBar(ft.Text("Errore Upload Foto")))
            page.update()

        page.add(ft.Column([
            ft.Text("CARICA FOTO", size=24),
            ft.ElevatedButton("SCATTA", icon="camera", on_click=lambda _: file_picker.pick_files(), bgcolor=PRIMARY, color="white"),
            ft.Container(content=img_temp, alignment=ft.alignment.center, padding=10),
            desc,
            ft.ElevatedButton("PUBBLICA", on_click=az_pubblica, bgcolor="#333333", color="white")
        ], horizontal_alignment="center", padding=20, scroll=ft.ScrollMode.AUTO, expand=True))

    def show_forum():
        lv = ft.ListView(expand=True, spacing=15, padding=10)
        posts = cloud.leggi_post()
        if not posts: lv.controls.append(ft.Text("Nessun post. Carica il primo!"))
        
        for p in posts:
            img_url = f"{STORAGE_URL}/{p['image_path']}"
            l, f, w = cloud.conta_voti(p['id'])
            
            def az_vota(e, pid=p['id'], t="Like"):
                cloud.vota(pid, user_state['name'], t)
                show_forum(); page.add(nav_bar); page.update()
                
            card = ft.Container(
                content=ft.Column([
                    ft.Row([ft.Text(p['autore'], weight="bold", size=16), ft.Text(p['comune'], color="grey")]),
                    ft.Image(src=img_url, height=250, fit=ft.ImageFit.COVER, border_radius=10),
                    ft.Text(p['descrizione'] if p['descrizione'] else ""),
                    ft.Row([
                        ft.ElevatedButton(f"👍 {l}", on_click=lambda e, x=p['id']: az_vota(e, x, "Like"), height=30),
                        ft.ElevatedButton(f"🤨 {f}", on_click=lambda e, x=p['id']: az_vota(e, x, "Fake"), height=30),
                        ft.ElevatedButton(f"😮 {w}", on_click=lambda e, x=p['id']: az_vota(e, x, "Wow"), height=30)
                    ], alignment="center"),
                    ft.Divider(),
                    ft.TextButton("Commenti", on_click=lambda e, x=p: show_dettaglio(x))
                ]), bgcolor=CARD_COLOR, padding=10, border_radius=10
            )
            lv.controls.append(card)
        page.add(ft.Column([ft.Text("FORUM GALLURA", size=24, weight="bold"), lv], padding=10, expand=True))

    def show_dettaglio(post_data):
        page.clean()
        comm_tf = ft.TextField(hint_text="Scrivi commento...", expand=True)
        lv_comm = ft.ListView(expand=True, height=200)
        
        def ricarica_comm():
            lv_comm.controls.clear()
            for c in cloud.leggi_commenti(post_data['id']):
                lv_comm.controls.append(ft.Text(f"{c['autore']}: {c['testo']}"))
            page.update()
        
        def az_invia_comm(e):
            if comm_tf.value:
                cloud.commenta(post_data['id'], user_state['name'], comm_tf.value)
                comm_tf.value = ""
                ricarica_comm()

        ricarica_comm()
        img_url = f"{STORAGE_URL}/{post_data['image_path']}"
        page.add(ft.Column([
            ft.IconButton(icon="arrow_back", on_click=lambda _: show_forum()),
            ft.Image(src=img_url, height=200, fit=ft.ImageFit.COVER),
            ft.Text(f"Post di {post_data['autore']}", size=20, weight="bold"),
            lv_comm,
            ft.Row([comm_tf, ft.IconButton(icon="send", on_click=az_invia_comm)])
        ], padding=20))
        page.update()

    show_login()

ft.app(target=main)
