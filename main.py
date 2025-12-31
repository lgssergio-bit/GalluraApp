import flet as ft
import time
from supabase import create_client, Client

# --- CONFIGURAZIONE ---
SUPABASE_URL = "https://zdyjwoxfqzpiexuoetyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkeWp3b3hmcXpwaWV4dW9ldHlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNTMzNDAsImV4cCI6MjA4MjcyOTM0MH0.ed0kcRIQm01BPGhLnyzBCsc3KxP82VUDo-6hytJXsn8"
STORAGE_URL = f"{SUPABASE_URL}/storage/v1/object/public/foto_funghi"

COMUNI_GALLURA = ["Luras", "Calangianus", "Tempio", "Olbia", "Arzachena", "Santa Teresa", "Palau", "San Teodoro", "Budoni", "Badesi"]

# --- DATABASE FUNGHI (Link Stabili e Testati) ---
DB_FUNGHI = {
    "Porcino Nero": {
        "lat": "Boletus aereus", "ok": True,
        "desc": "Il Re della macchia.", 
        "full": "CAPPELLO: Bronzo scuro, vellutato. GAMBO: Ocra, robusto. CARNE: Bianca immutabile. HABITAT: Latifoglie (Sughere).",
        "img": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Boletus_aereus_fere_niger.jpg" # Link diretto stabile
    },
    "Ovolo Reale": {
        "lat": "Amanita caesarea", "ok": True,
        "desc": "L'unico che si mangia crudo.", 
        "full": "CAPPELLO: Arancio vivo. LAMELLE: Giallo oro. GAMBO: Giallo. VOLVA: Bianca ampia. NOTE: Ottimo crudo.",
        "img": "https://upload.wikimedia.org/wikipedia/commons/2/22/Amanita_caesarea_3.jpg"
    },
    "Antunna": {
        "lat": "Pleurotus eryngii", "ok": True,
        "desc": "Cresce sul cardo.", 
        "full": "CAPPELLO: Bruno. LAMELLE: Decorrenti chiare. HABITAT: Radici di cardo. CUCINA: Ottimo alla brace.",
        "img": "https://upload.wikimedia.org/wikipedia/commons/0/05/Pleurotus_eryngii_01.jpg"
    },
    "Mazza di Tamburo": {
        "lat": "Macrolepiota procera", "ok": True,
        "desc": "Gigante tigrato.", 
        "full": "CAPPELLO: Scaglie brune. GAMBO: Tigrato con anello mobile. NOTE: Gambo legnoso da scartare.",
        "img": "https://upload.wikimedia.org/wikipedia/commons/5/5b/Macrolepiota_procera_bgiu.jpg"
    },
    "Tignosa Verdognola": {
        "lat": "Amanita phalloides", "ok": False,
        "desc": "MORTALE.", 
        "full": "CAPPELLO: Verdastro/giallo/bianco. GAMBO: Anello e VOLVA bianca. ODORE: Dolciastro.",
        "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Amanita_phalloides_1.JPG/800px-Amanita_phalloides_1.JPG"
    },
    "Ovolo Malefico": {
        "lat": "Amanita muscaria", "ok": False,
        "desc": "Rosso a puntini.", 
        "full": "CAPPELLO: Rosso con verruche bianche. LAMELLE: Bianche (NON gialle). TOSSICO.",
        "img": "https://upload.wikimedia.org/wikipedia/commons/3/32/Amanita_muscaria_3_vliegenzwammen_op_rij.jpg"
    }
}

# --- CLOUD MANAGER (God Mode) ---
class CloudManager:
    def __init__(self):
        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.attivo = True
        except: self.attivo = False

    def login(self, u, p):
        if not self.attivo: return None, "Offline"
        try:
            res = self.client.table("utenti").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                user_data = res.data[0]
                if user_data.get('bannato', False):
                    return None, "SEI STATO BANNATO DALL'ADMIN."
                return user_data, "Ok"
            return None, "Dati errati"
        except Exception as e: return None, str(e)

    def registra(self, u, p, c):
        if not self.attivo: return False, "Offline"
        try:
            res = self.client.table("utenti").select("*").eq("username", u).execute()
            if res.data: return False, "Utente esiste già"
            self.client.table("utenti").insert({"username": u, "password": p, "comune": c, "is_admin": False, "bannato": False}).execute()
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

    # --- AZIONI ADMIN ---
    def elimina_post(self, pid):
        if not self.attivo: return
        try: self.client.table("post").delete().eq("id", pid).execute()
        except: pass

    def elimina_commento(self, cid):
        if not self.attivo: return
        try: self.client.table("commenti").delete().eq("id", cid).execute()
        except: pass

    def banna_utente(self, username_da_bannare):
        if not self.attivo: return
        try: self.client.table("utenti").update({"bannato": True}).eq("username", username_da_bannare).execute()
        except: pass

    def get_post_by_id(self, pid):
        if not self.attivo: return None
        try:
            res = self.client.table("post").select("*").eq("id", pid).execute()
            return res.data[0] if res.data else None
        except: return None

    # --- SOCIAL ---
    def leggi_post(self):
        if not self.attivo: return []
        try: return self.client.table("post").select("*").order("created_at", desc=True).execute().data
        except: return []

    def conta_social(self, pid):
        l, f, c = 0, 0, 0
        if not self.attivo: return l, f, c
        try:
            res_v = self.client.table("voti").select("tipo").eq("post_id", pid).execute()
            for r in res_v.data:
                if r['tipo'] == 'Like': l += 1
                elif r['tipo'] == 'Fake': f += 1
            res_c = self.client.table("commenti").select("id", count="exact").eq("post_id", pid).execute()
            c = res_c.count
        except: pass
        return l, f, c

    def invia_voto(self, pid, uid, tipo):
        if not self.attivo: return False
        try:
            self.client.table("voti").insert({"post_id": pid, "user_id": uid, "tipo": tipo}).execute()
            return True
        except: return False # Già votato

    def scrivi_commento(self, pid, autore, testo, autore_post):
        if not self.attivo: return
        try:
            self.client.table("commenti").insert({"post_id": pid, "autore": autore, "testo": testo}).execute()
            if autore != autore_post:
                msg = f"{autore} ha commentato il tuo post!"
                self.client.table("notifiche").insert({"user_id": autore_post, "testo": msg, "post_id": pid}).execute()
        except: pass

    def leggi_commenti(self, pid):
        if not self.attivo: return []
        try: return self.client.table("commenti").select("*").eq("post_id", pid).order("created_at", desc=True).execute().data
        except: return []

    # --- NOTIFICHE ---
    def conta_notifiche_non_lette(self, user):
        if not self.attivo: return 0
        try:
            res = self.client.table("notifiche").select("id", count="exact").eq("user_id", user).eq("letto", False).execute()
            return res.count
        except: return 0

    def leggi_notifiche(self, user):
        if not self.attivo: return []
        try: return self.client.table("notifiche").select("*").eq("user_id", user).order("created_at", desc=True).execute().data
        except: return []

    def segna_tutte_lette(self, user):
        if not self.attivo: return
        try: self.client.table("notifiche").update({"letto": True}).eq("user_id", user).execute()
        except: pass

# --- APP ---
def main(page: ft.Page):
    page.title = "Gallura Mycelium Admin"
    page.bgcolor = "#121212"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "auto"
    
    cloud = CloudManager()
    user = {"name": None, "comune": None, "is_admin": False}

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    img_temp = ft.Image(visible=False, height=200)
    path_box = [""]

    def on_file(e):
        if e.files:
            path_box[0] = e.files[0].path; img_temp.src = e.files[0].path; img_temp.visible = True; page.update()
    file_picker.on_result = on_file

    def aggiorna_nav(e=None):
        idx = 0
        if e: idx = e.control.selected_index
        n_not = cloud.conta_notifiche_non_lette(user['name']) if user['name'] else 0
        
        page.navigation_bar = ft.NavigationBar(
            selected_index=idx, bgcolor="#222222", on_change=cambio_tab,
            destinations=[
                ft.NavigationBarDestination(icon="home", label="Home"),
                ft.NavigationBarDestination(icon="menu_book", label="Guida"),
                ft.NavigationBarDestination(icon="add_a_photo", label="Carica"),
                ft.NavigationBarDestination(icon="forum", label="Forum"),
                ft.NavigationBarDestination(icon=ft.Icon(ft.icons.NOTIFICATIONS), label=f"Notifiche ({n_not})" if n_not > 0 else "Notifiche"),
            ]
        )
        page.clean()
        if idx == 0: show_home()
        elif idx == 1: show_guida()
        elif idx == 2: show_upload()
        elif idx == 3: show_forum()
        elif idx == 4: show_notifiche()
        page.add(page.navigation_bar)
        page.update()

    def cambio_tab(e): aggiorna_nav(e)

    # --- LOGIN ---
    def show_login():
        page.clean()
        u = ft.TextField(label="Utente"); p = ft.TextField(label="Password", password=True)
        def az_login(e):
            page.show_snack_bar(ft.SnackBar(ft.Text("Accesso..."))); page.update()
            data, msg = cloud.login(u.value, p.value)
            if data:
                user['name'] = data['username']; user['comune'] = data['comune']; user['is_admin'] = data.get('is_admin', False)
                aggiorna_nav()
            else: page.show_snack_bar(ft.SnackBar(ft.Text(f"Errore: {msg}"), bgcolor="red")); page.update()
        page.add(ft.Container(padding=20, content=ft.Column([
            ft.Icon("forest", size=80, color="green"), ft.Text("GALLURA MYCELIUM", size=30, weight="bold"),
            ft.Container(height=20), u, p, ft.ElevatedButton("ENTRA", on_click=az_login, bgcolor="green", color="white"),
            ft.TextButton("Registrati", on_click=lambda _: show_register())
        ], horizontal_alignment="center", alignment="center")))
        page.update()

    def show_register():
        page.clean()
        u = ft.TextField(label="Utente"); p = ft.TextField(label="Password", password=True); c = ft.Dropdown(label="Comune", options=[ft.dropdown.Option(x) for x in COMUNI_GALLURA])
        def az_ok(e):
            if not u.value or not p.value or not c.value: return
            ok, msg = cloud.registra(u.value, p.value, c.value)
            page.show_snack_bar(ft.SnackBar(ft.Text(msg)))
            if ok: time.sleep(1); show_login()
            page.update()
        page.add(ft.Container(padding=20, content=ft.Column([ft.Text("REGISTRAZIONE", size=24), u, p, c, ft.ElevatedButton("CONFERMA", on_click=az_ok, bgcolor="blue", color="white"), ft.TextButton("Annulla", on_click=lambda _: show_login())], horizontal_alignment="center")))
        page.update()

    # --- HOME ---
    def show_home():
        rank = cloud.classifica()
        col_rank = ft.Column()
        for i, (com, pt) in enumerate(rank[:5]):
            color = "yellow" if i == 0 else "white"
            col_rank.controls.append(ft.Container(bgcolor="#222222", padding=10, border_radius=5, content=ft.Row([ft.Text(f"{i+1}. {com}", color=color), ft.Text(f"{pt}", weight="bold", color=color)])))
        titolo = f"Ciao {user['name']} 🛡️" if user['is_admin'] else f"Ciao {user['name']}"
        colore_titolo = "red" if user['is_admin'] else "white"
        page.add(ft.Container(padding=20, content=ft.Column([ft.Text(titolo, size=24, weight="bold", color=colore_titolo), ft.Divider(), ft.Text("CLASSIFICA", color="yellow"), col_rank])))

    # --- NOTIFICHE ---
    def show_notifiche():
        notifiche = cloud.leggi_notifiche(user['name'])
        lv = ft.Column(scroll="auto", expand=True)
        if not notifiche: lv.controls.append(ft.Text("Nessuna notifica."))
        
        for n in notifiche:
            bg = "#333333" if not n['letto'] else "#1e1e1e"
            icon = "mark_email_unread" if not n['letto'] else "check"
            
            # Click notifica -> Vai al post
            def vai_al_post(e, pid=n.get('post_id')):
                if pid:
                    post = cloud.get_post_by_id(pid)
                    if post: show_dettaglio_post(post)
                    else: page.show_snack_bar(ft.SnackBar(ft.Text("Post eliminato!")))
                else: page.show_snack_bar(ft.SnackBar(ft.Text("Info non disponibile")))

            lv.controls.append(ft.Container(bgcolor=bg, padding=15, border_radius=10, margin=5, on_click=vai_al_post,
                content=ft.Row([ft.Icon(icon, color="yellow" if not n['letto'] else "grey"), ft.Text(n['testo'], expand=True, weight="bold" if not n['letto'] else "normal")])))
        
        def az_segna_tutte(e):
            cloud.segna_tutte_lette(user['name'])
            aggiorna_nav()

        page.add(ft.Container(padding=10, expand=True, content=ft.Column([
            ft.Row([ft.Text("NOTIFICHE", size=24), ft.IconButton(icon="done_all", tooltip="Segna tutte lette", on_click=az_segna_tutte)], alignment="spaceBetween"),
            lv
        ])))

    # --- GUIDA ---
    def show_dettaglio_fungo(nome_fungo):
        page.clean()
        dati = DB_FUNGHI[nome_fungo]
        colore = "green" if dati['ok'] else "red"
        page.add(ft.Container(padding=10, content=ft.Column([
            ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: aggiorna_nav())]),
            ft.Image(src=dati['img'], height=300, fit=ft.ImageFit.COVER, border_radius=10),
            ft.Text(nome_fungo, size=30, weight="bold", color=colore),
            ft.Container(bgcolor=colore, padding=5, border_radius=5, content=ft.Text("COMMESTIBILE" if dati['ok'] else "TOSSICO", color="white")),
            ft.Divider(), ft.Text(dati['full'], size=16),
        ], scroll="auto")))
        page.update()

    def show_guida():
        lv = ft.Column(scroll="auto", expand=True)
        for k, v in DB_FUNGHI.items():
            col = "green" if v['ok'] else "red"
            lv.controls.append(ft.Container(bgcolor="#1e1e1e", padding=10, margin=5, border_radius=10,
                content=ft.Column([
                    ft.Image(src=v['img'], height=150, fit=ft.ImageFit.COVER, border_radius=5),
                    ft.Text(k, size=20, weight="bold", color=col), ft.Text(v['desc']),
                    ft.ElevatedButton("SCHEDA COMPLETA", icon="info", bgcolor="#333333", color="white", width=400, on_click=lambda e, x=k: show_dettaglio_fungo(x))
                ])))
        page.add(ft.Container(padding=10, expand=True, content=lv))

    # --- FORUM & DETTAGLIO POST ---
    def show_dettaglio_post(post):
        page.clean()
        url = f"{STORAGE_URL}/{post['image_path']}"
        comm_box = ft.TextField(hint_text="Scrivi commento...", expand=True)
        lista_commenti = ft.Column()

        def ricarica_commenti():
            lista_commenti.controls.clear()
            comms = cloud.leggi_commenti(post['id'])
            for c in comms:
                # Selettore Ban / Elimina Commento
                comandi = []
                if user['is_admin']:
                    comandi.append(ft.IconButton(icon="delete", icon_color="red", icon_size=16, tooltip="Elimina Commento", on_click=lambda e, x=c['id']: az_del_comm(x)))
                    if c['autore'] != user['name']: # Non bannare se stesso
                        comandi.append(ft.IconButton(icon="block", icon_color="red", icon_size=16, tooltip="BANNA UTENTE", on_click=lambda e, x=c['autore']: az_ban(x)))

                lista_commenti.controls.append(ft.Container(bgcolor="#222222", padding=8, border_radius=5, margin=2,
                    content=ft.Row([
                        ft.Column([ft.Text(c['autore'], weight="bold", size=12, color="green"), ft.Text(c['testo'])]),
                        ft.Row(comandi)
                    ], alignment="spaceBetween")
                ))
            page.update()

        def az_invia_comm(e):
            if comm_box.value:
                cloud.scrivi_commento(post['id'], user['name'], comm_box.value, post['autore'])
                comm_box.value = ""; ricarica_commenti()
        
        def az_del_comm(cid):
            cloud.elimina_commento(cid); ricarica_commenti()
            
        def az_ban(nome_utente):
            cloud.banna_utente(nome_utente)
            page.show_snack_bar(ft.SnackBar(ft.Text(f"{nome_utente} è stato BANNATO!"), bgcolor="red")); page.update()

        ricarica_commenti()
        page.add(ft.Container(padding=10, content=ft.Column([
            ft.IconButton(icon="arrow_back", on_click=lambda _: aggiorna_nav()),
            ft.Image(src=url, fit=ft.ImageFit.FIT_WIDTH, border_radius=10),
            ft.Text(f"Post di {post['autore']}", size=20, weight="bold"),
            ft.Text(post['descrizione'], size=16),
            ft.Divider(), ft.Text("Commenti:", weight="bold"), lista_commenti,
            ft.Row([comm_box, ft.IconButton(icon="send", on_click=az_invia_comm)])
        ], scroll="auto")))
        page.update()

    def show_forum():
        posts = cloud.leggi_post()
        lv = ft.Column(scroll="auto", expand=True)
        if not posts: lv.controls.append(ft.Text("Nessun post."))
        
        for p in posts:
            url = f"{STORAGE_URL}/{p['image_path']}"
            likes, fakes, num_comm = cloud.conta_social(p['id'])
            
            # Tasti aggiornabili in tempo reale
            btn_like = ft.ElevatedButton(f"👍 {likes}")
            btn_fake = ft.ElevatedButton(f"🤥 {fakes}", bgcolor="red", color="white")
            
            def az_vota(e, pid=p['id'], tipo="Like", bl=btn_like, bf=btn_fake):
                ok = cloud.invia_voto(pid, user['name'], tipo)
                if ok: # Aggiorna SOLO il numero sul tasto (UI Optimistic)
                    if tipo == "Like": bl.text = f"👍 {int(bl.text.split()[1]) + 1}"
                    else: bf.text = f"🤥 {int(bf.text.split()[1]) + 1}"
                    bl.update(); bf.update()

            def az_elimina(e, pid=p['id']):
                cloud.elimina_post(pid); aggiorna_nav(e)
            
            def az_ban_post(e, nome_utente):
                cloud.banna_utente(nome_utente)
                page.show_snack_bar(ft.SnackBar(ft.Text(f"{nome_utente} Bannato!"), bgcolor="red")); page.update()

            admin_row = ft.Row()
            if user['is_admin']:
                admin_row = ft.Row([
                    ft.IconButton(icon="delete", icon_color="red", tooltip="Elimina Post", on_click=lambda e, x=p['id']: az_elimina(e, x)),
                    ft.IconButton(icon="block", icon_color="red", tooltip="BANNA UTENTE", on_click=lambda e, x=p['autore']: az_ban_post(e, x))
                ])

            card = ft.Container(bgcolor="#1e1e1e", padding=10, margin=5, border_radius=10, content=ft.Column([
                ft.Row([ft.Row([ft.Text(p['autore'], weight="bold"), ft.Text(p['comune'], color="grey")]), admin_row], alignment="spaceBetween"),
                ft.Image(src=url, height=200, fit=ft.ImageFit.COVER, border_radius=5),
                ft.Text(p['descrizione']),
                ft.Row([
                    ft.Container(content=btn_like, on_click=lambda e, x=p['id']: az_vota(e, x, "Like")),
                    ft.Container(content=btn_fake, on_click=lambda e, x=p['id']: az_vota(e, x, "Fake"))
                ], alignment="center"),
                ft.Container(height=5),
                ft.OutlinedButton(f"💬 {num_comm} - INGRANDISCI", icon="fullscreen", width=400, on_click=lambda e, x=p: show_dettaglio_post(x))
            ]))
            lv.controls.append(card)
        page.add(ft.Container(padding=10, expand=True, content=lv))

    def show_upload():
        desc = ft.TextField(label="Descrizione")
        def az_pub(e):
            if not path_box[0]: page.show_snack_bar(ft.SnackBar(ft.Text("Manca foto!"))); page.update(); return
            nome_file = f"{int(time.time())}_{user['name']}.jpg"
            page.show_snack_bar(ft.SnackBar(ft.Text("Caricamento..."))); page.update()
            if cloud.upload_foto(path_box[0], nome_file):
                cloud.nuovo_post(user['name'], user['comune'], desc.value, nome_file)
                page.show_snack_bar(ft.SnackBar(ft.Text("Pubblicato!"), bgcolor="green"))
                img_temp.visible = False; desc.value = ""; path_box[0] = ""; 
                page.navigation_bar.selected_index = 3; show_forum(); page.add(page.navigation_bar)
            else: page.show_snack_bar(ft.SnackBar(ft.Text("Errore Upload"), bgcolor="red")); page.update()
        page.add(ft.Container(padding=20, content=ft.Column([ft.Text("NUOVO RITROVAMENTO", size=20), ft.ElevatedButton("FOTO", on_click=lambda _: file_picker.pick_files(), bgcolor="green", color="white"), img_temp, desc, ft.ElevatedButton("PUBBLICA", on_click=az_pub, bgcolor="#333333", color="white")], horizontal_alignment="center")))

    show_login()

ft.app(target=main)
