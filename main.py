import flet as ft
import time
from supabase import create_client, Client

# --- CONFIGURAZIONE ---
SUPABASE_URL = "https://zdyjwoxfqzpiexuoetyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkeWp3b3hmcXpwaWV4dW9ldHlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNTMzNDAsImV4cCI6MjA4MjcyOTM0MH0.ed0kcRIQm01BPGhLnyzBCsc3KxP82VUDo-6hytJXsn8"
STORAGE_URL = f"{SUPABASE_URL}/storage/v1/object/public/foto_funghi"

# --- DATI E LINK IMMAGINI (Link puri per evitare blocchi) ---
COMUNI_GALLURA = ["Luras", "Calangianus", "Tempio", "Olbia", "Arzachena", "Santa Teresa", "Palau", "San Teodoro", "Budoni", "Badesi"]

DB_FUNGHI = {
    "Porcino Nero": {
        "lat": "Boletus aereus", "desc": "Il Re della macchia.", "full": "Cappello bronzo scuro, vellutato. Gambo robusto color ocra. Carne bianca immutabile. Eccellente commestibile.",
        "img": "https://upload.wikimedia.org/wikipedia/commons/b/b0/Boletus_aereus_3.jpg", "ok": True
    },
    "Ovolo Reale": {
        "lat": "Amanita caesarea", "desc": "L'unico che si mangia crudo.", "full": "Nasce come un uovo bianco. Cappello arancio vivo, lamelle e gambo GIALLO ORO. Ottimo crudo in insalata.",
        "img": "https://upload.wikimedia.org/wikipedia/commons/6/64/Amanita_caesarea_2.jpg", "ok": True
    },
    "Antunna": {
        "lat": "Pleurotus eryngii", "desc": "Cresce sul cardo.", "full": "Fungo saprofita che cresce sulle radici del cardo. Cappello bruno, lamelle decorrenti. Carne soda e saporita.",
        "img": "https://upload.wikimedia.org/wikipedia/commons/5/52/Pleurotus_eryngii_Mallorca.jpg", "ok": True
    },
    "Mazza di Tamburo": {
        "lat": "Macrolepiota procera", "desc": "Gigante tigrato.", "full": "Cappello con scaglie marroni, umbone centrale. Anello mobile doppio. Gambo tigrato e legnoso (non si mangia).",
        "img": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Macrolepiota_procera_bg.jpg", "ok": True
    },
    "Tignosa Verdognola": {
        "lat": "Amanita phalloides", "desc": "MORTALE.", "full": "IL PIÙ PERICOLOSO. Cappello verdastro/giallo (variabile). Ha sempre anello e VOLVA bianca. Odore dolciastro.",
        "img": "https://upload.wikimedia.org/wikipedia/commons/9/99/Amanita_phalloides_1.JPG", "ok": False
    },
    "Ovolo Malefico": {
        "lat": "Amanita muscaria", "desc": "Rosso a puntini bianchi.", "full": "Inconfondibile rosso con verruche bianche. Lamelle BIANCHE (differenza con l'Ovolo Reale). Tossico e allucinogeno.",
        "img": "https://upload.wikimedia.org/wikipedia/commons/3/32/Amanita_muscaria_3_vliegenzwammen_op_rij.jpg", "ok": False
    }
}

# --- DATABASE MANAGER (Aggiornato con Voti e Commenti) ---
class CloudManager:
    def __init__(self):
        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.attivo = True
        except: self.attivo = False

    def login(self, u, p):
        if not self.attivo: return None
        try:
            res = self.client.table("utenti").select("*").eq("username", u).eq("password", p).execute()
            return res.data[0] if res.data else None
        except: return None

    def registra(self, u, p, c):
        if not self.attivo: return False, "Offline"
        try:
            res = self.client.table("utenti").select("*").eq("username", u).execute()
            if res.data: return False, "Utente esiste già"
            self.client.table("utenti").insert({"username": u, "password": p, "comune": c}).execute()
            return True, "Registrato!"
        except Exception as e: return False, str(e)

    def classifica(self):
        if not self.attivo: return []
        punti = {c: 0 for c in COMUNI_GALLURA}
        try:
            res = self.client.table("post").select("comune").execute()
            for r in res.data:
                c = r.get('comune')
                if c in punti: punti[c] += 1
        except: pass
        return sorted(punti.items(), key=lambda x: x[1], reverse=True)

    def upload_foto(self, path, nome):
        if not self.attivo: return False
        try:
            with open(path, 'rb') as f:
                self.client.storage.from_("foto_funghi").upload(nome, f)
            return True
        except: return False

    def nuovo_post(self, u, c, d, img):
        if not self.attivo: return False
        try:
            self.client.table("post").insert({"autore": u, "comune": c, "descrizione": d, "image_path": img}).execute()
            return True
        except: return False

    def leggi_post(self):
        if not self.attivo: return []
        try:
            return self.client.table("post").select("*").order("created_at", desc=True).execute().data
        except: return []

    # --- NUOVE FUNZIONI SOCIAL ---
    def invia_voto(self, pid, uid, tipo):
        if not self.attivo: return
        try:
            self.client.table("voti").insert({"post_id": pid, "user_id": uid, "tipo": tipo}).execute()
        except: pass # Probabilmente ha già votato

    def conta_voti(self, pid):
        if not self.attivo: return 0, 0
        l, f = 0, 0
        try:
            res = self.client.table("voti").select("tipo").eq("post_id", pid).execute()
            for r in res.data:
                if r['tipo'] == 'Like': l += 1
                elif r['tipo'] == 'Fake': f += 1
        except: pass
        return l, f

    def scrivi_commento(self, pid, autore, testo):
        if not self.attivo: return
        try:
            self.client.table("commenti").insert({"post_id": pid, "autore": autore, "testo": testo}).execute()
        except: pass

    def leggi_commenti(self, pid):
        if not self.attivo: return []
        try:
            return self.client.table("commenti").select("*").eq("post_id", pid).order("created_at", desc=True).execute().data
        except: return []

# --- APP ---
def main(page: ft.Page):
    page.title = "Gallura Mycelium"
    page.bgcolor = "#121212"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "auto"
    
    cloud = CloudManager()
    user = {"name": None, "comune": None}

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    img_temp = ft.Image(visible=False, height=200)
    path_box = [""]

    def on_file(e):
        if e.files:
            path_box[0] = e.files[0].path
            img_temp.src = e.files[0].path
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
        bgcolor="#222222",
        on_change=cambio_tab
    )

    # --- PAGINE LOGIN/REG/HOME (Invariate) ---
    def show_login():
        page.clean()
        u = ft.TextField(label="Utente", border_color="green")
        p = ft.TextField(label="Password", password=True, border_color="green")
        def az_login(e):
            page.show_snack_bar(ft.SnackBar(ft.Text("Accesso...")))
            page.update()
            data = cloud.login(u.value, p.value)
            if data:
                user['name'] = data['username']
                user['comune'] = data['comune']
                show_home(); page.add(nav_bar)
            else: page.show_snack_bar(ft.SnackBar(ft.Text("Errore login"), bgcolor="red"))
            page.update()
        page.add(ft.Container(padding=20, content=ft.Column([
            ft.Icon("forest", size=80, color="green"), ft.Text("GALLURA MYCELIUM", size=30, weight="bold"),
            ft.Container(height=20), u, p, ft.ElevatedButton("ENTRA", on_click=az_login, bgcolor="green", color="white"),
            ft.TextButton("Registrati", on_click=lambda _: show_register())
        ], horizontal_alignment="center", alignment="center")))
        page.update()

    def show_register():
        page.clean()
        u = ft.TextField(label="Utente"); p = ft.TextField(label="Password", password=True)
        c = ft.Dropdown(label="Comune", options=[ft.dropdown.Option(x) for x in COMUNI_GALLURA])
        def az_ok(e):
            if not u.value or not p.value or not c.value: return
            ok, msg = cloud.registra(u.value, p.value, c.value)
            page.show_snack_bar(ft.SnackBar(ft.Text(msg)))
            if ok: time.sleep(1); show_login()
            page.update()
        page.add(ft.Container(padding=20, content=ft.Column([
            ft.Text("REGISTRAZIONE", size=24), u, p, c,
            ft.ElevatedButton("CONFERMA", on_click=az_ok, bgcolor="blue", color="white"),
            ft.TextButton("Annulla", on_click=lambda _: show_login())
        ], horizontal_alignment="center")))
        page.update()

    def show_home():
        rank = cloud.classifica()
        col_rank = ft.Column()
        for i, (com, pt) in enumerate(rank[:5]):
            color = "yellow" if i == 0 else "white"
            col_rank.controls.append(ft.Container(bgcolor="#222222", padding=10, border_radius=5,
                content=ft.Row([ft.Text(f"{i+1}. {com}", color=color), ft.Text(f"{pt}", weight="bold", color=color)])))
        page.add(ft.Container(padding=20, content=ft.Column([
            ft.Text(f"Ciao {user['name']}!", size=24, weight="bold"), ft.Divider(),
            ft.Text("CLASSIFICA", color="yellow"), col_rank
        ])))

    # --- GUIDA CON DETTAGLIO ---
    def show_dettaglio_fungo(nome_fungo):
        page.clean()
        dati = DB_FUNGHI[nome_fungo]
        colore = "green" if dati['ok'] else "red"
        page.add(ft.Container(padding=10, content=ft.Column([
            ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: (page.clean(), show_guida(), page.add(nav_bar), page.update()))]),
            ft.Image(src=dati['img'], height=300, fit=ft.ImageFit.COVER, border_radius=10),
            ft.Text(nome_fungo, size=30, weight="bold", color=colore),
            ft.Text(dati['lat'], italic=True, size=18, color="grey"),
            ft.Container(bgcolor=colore, padding=5, border_radius=5, content=ft.Text("COMMESTIBILE" if dati['ok'] else "TOSSICO", color="white")),
            ft.Divider(), ft.Text(dati['full'], size=16),
        ], scroll="auto")))
        page.update()

    def show_guida():
        lv = ft.Column(scroll="auto", expand=True)
        for k, v in DB_FUNGHI.items():
            col = "green" if v['ok'] else "red"
            lv.controls.append(ft.Container(bgcolor="#1e1e1e", padding=10, margin=5, border_radius=10,
                on_click=lambda e, x=k: show_dettaglio_fungo(x),
                content=ft.Column([
                    ft.Image(src=v['img'], height=150, fit=ft.ImageFit.COVER, border_radius=5),
                    ft.Text(k, size=20, weight="bold", color=col),
                    ft.Text(v['desc'])
                ])))
        page.add(ft.Container(padding=10, expand=True, content=lv))

    # --- UPLOAD ---
    def show_upload():
        desc = ft.TextField(label="Descrizione")
        def az_pub(e):
            if not path_box[0]: page.show_snack_bar(ft.SnackBar(ft.Text("Manca foto!"))); page.update(); return
            nome_file = f"{int(time.time())}_{user['name']}.jpg"
            page.show_snack_bar(ft.SnackBar(ft.Text("Caricamento..."))); page.update()
            if cloud.upload_foto(path_box[0], nome_file):
                cloud.nuovo_post(user['name'], user['comune'], desc.value, nome_file)
                page.show_snack_bar(ft.SnackBar(ft.Text("Pubblicato!"), bgcolor="green"))
                img_temp.visible = False; desc.value = ""; path_box[0] = ""; show_forum(); page.add(nav_bar)
            else: page.show_snack_bar(ft.SnackBar(ft.Text("Errore Upload"), bgcolor="red"))
            page.update()
        page.add(ft.Container(padding=20, content=ft.Column([
            ft.Text("NUOVO RITROVAMENTO", size=20),
            ft.ElevatedButton("FOTO", on_click=lambda _: file_picker.pick_files(), bgcolor="green", color="white"),
            img_temp, desc, ft.ElevatedButton("PUBBLICA", on_click=az_pub, bgcolor="#333333", color="white")
        ], horizontal_alignment="center")))

    # --- FORUM SOCIAL COMPLETO ---
    def show_dettaglio_post(post):
        page.clean()
        url = f"{STORAGE_URL}/{post['image_path']}"
        comm_box = ft.TextField(hint_text="Scrivi un commento...", expand=True)
        lista_commenti = ft.Column()

        def ricarica_commenti():
            lista_commenti.controls.clear()
            comms = cloud.leggi_commenti(post['id'])
            for c in comms:
                lista_commenti.controls.append(ft.Container(
                    bgcolor="#222222", padding=5, border_radius=5,
                    content=ft.Column([
                        ft.Text(c['autore'], weight="bold", size=12, color="green"),
                        ft.Text(c['testo'])
                    ])
                ))
            page.update()

        def az_invia_comm(e):
            if comm_box.value:
                cloud.scrivi_commento(post['id'], user['name'], comm_box.value)
                comm_box.value = ""
                ricarica_commenti()

        ricarica_commenti() # Carica subito i commenti

        page.add(ft.Container(padding=10, content=ft.Column([
            ft.IconButton(icon="arrow_back", on_click=lambda _: (page.clean(), show_forum(), page.add(nav_bar), page.update())),
            ft.Image(src=url, fit=ft.ImageFit.FIT_WIDTH, border_radius=10),
            ft.Text(f"Post di {post['autore']}", size=20, weight="bold"),
            ft.Text(post['descrizione'], size=16),
            ft.Divider(),
            ft.Text("Commenti:", weight="bold"),
            lista_commenti,
            ft.Row([comm_box, ft.IconButton(icon="send", on_click=az_invia_comm)])
        ], scroll="auto")))
        page.update()

    def show_forum():
        posts = cloud.leggi_post()
        lv = ft.Column(scroll="auto", expand=True)
        if not posts: lv.controls.append(ft.Text("Nessun post."))
        
        for p in posts:
            url = f"{STORAGE_URL}/{p['image_path']}"
            likes, fakes = cloud.conta_voti(p['id'])

            # Azioni pulsanti
            def az_vota(e, pid=p['id'], tipo="Like"):
                cloud.invia_voto(pid, user['name'], tipo)
                show_forum(); page.add(nav_bar); page.update() # Ricarica per aggiornare i numeri

            # Card del post
            card = ft.Container(
                bgcolor="#1e1e1e", padding=10, margin=5, border_radius=10,
                content=ft.Column([
                    ft.Row([ft.Text(p['autore'], weight="bold"), ft.Text(p['comune'], color="grey")], alignment="spaceBetween"),
                    # Cliccando sull'immagine si apre il dettaglio
                    ft.Container(
                        content=ft.Image(src=url, height=250, fit=ft.ImageFit.COVER, border_radius=5),
                        on_click=lambda e, x=p: show_dettaglio_post(x)
                    ),
                    ft.Text(p['descrizione']),
                    ft.Row([
                        ft.ElevatedButton(f"👍 {likes}", on_click=lambda e, x=p['id']: az_vota(e, x, "Like"), height=30),
                        ft.ElevatedButton(f"🤥 {fakes}", on_click=lambda e, x=p['id']: az_vota(e, x, "Fake"), height=30, bgcolor="red", color="white"),
                        ft.TextButton("💬 Commenta", on_click=lambda e, x=p: show_dettaglio_post(x))
                    ], alignment="center")
                ])
            )
            lv.controls.append(card)
        
        page.add(ft.Container(padding=10, expand=True, content=lv))

    show_login()

ft.app(target=main)
