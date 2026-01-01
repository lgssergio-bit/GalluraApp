import flet as ft
import flet.map as map
import time
import json
import math
from supabase import create_client, Client

# --- CONFIGURAZIONE ---
SUPABASE_URL = "https://zdyjwoxfqzpiexuoetyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkeWp3b3hmcXpwaWV4dW9ldHlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNTMzNDAsImV4cCI6MjA4MjcyOTM0MH0.ed0kcRIQm01BPGhLnyzBCsc3KxP82VUDo-6hytJXsn8"
STORAGE_URL = f"{SUPABASE_URL}/storage/v1/object/public/foto_funghi"

COMUNI_GALLURA = ["Luras", "Calangianus", "Tempio", "Olbia", "Arzachena", "Santa Teresa", "Palau", "San Teodoro", "Budoni", "Badesi"]

# --- DB FUNGHI ---
DB_FUNGHI = {
    "Porcino Nero": {"lat": "Boletus aereus", "ok": True, "desc": "Il Re.", "full": "CAPPELLO: Bronzo scuro. GAMBO: Ocra. HABITAT: Sughere.", "img": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Boletus_aereus_fere_niger.jpg"},
    "Ovolo Reale": {"lat": "Amanita caesarea", "ok": True, "desc": "Mangia crudo.", "full": "CAPPELLO: Arancio. LAMELLE: Giallo oro.", "img": "https://upload.wikimedia.org/wikipedia/commons/2/22/Amanita_caesarea_3.jpg"},
    "Antunna": {"lat": "Pleurotus eryngii", "ok": True, "desc": "Del Cardo.", "full": "HABITAT: Radici del Cardo. CUCINA: Brace.", "img": "https://upload.wikimedia.org/wikipedia/commons/0/05/Pleurotus_eryngii_01.jpg"},
    "Mazza di Tamburo": {"lat": "Macrolepiota procera", "ok": True, "desc": "Gigante.", "full": "GAMBO: Tigrato con anello mobile.", "img": "https://upload.wikimedia.org/wikipedia/commons/5/5b/Macrolepiota_procera_bgiu.jpg"},
    "Tignosa Verdognola": {"lat": "Amanita phalloides", "ok": False, "desc": "MORTALE.", "full": "MORTALE. Cappello verdastro, volva bianca.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Amanita_phalloides_1.JPG/800px-Amanita_phalloides_1.JPG"},
    "Ovolo Malefico": {"lat": "Amanita muscaria", "ok": False, "desc": "Tossico.", "full": "Rosso con verruche. Lamelle Bianche.", "img": "https://upload.wikimedia.org/wikipedia/commons/3/32/Amanita_muscaria_3_vliegenzwammen_op_rij.jpg"}
}

# --- CLOUD MANAGER ---
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
                if user_data.get('bannato', False): return None, "BANNATO"
                return user_data, "Ok"
            return None, "Dati errati"
        except Exception as e: return None, str(e)

    def registra(self, u, p, c):
        if not self.attivo: return False, "Offline"
        try:
            res = self.client.table("utenti").select("*").eq("username", u).execute()
            if res.data: return False, "Esiste già"
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

    # --- MAPPA GPS ---
    def salva_marker(self, uid, lat, lon, desc):
        if not self.attivo: return
        try: self.client.table("markers").insert({"user_id": uid, "lat": lat, "lon": lon, "descrizione": desc}).execute()
        except: pass

    def leggi_markers(self, uid):
        if not self.attivo: return []
        try: return self.client.table("markers").select("*").eq("user_id", uid).execute().data
        except: return []

    def salva_percorso(self, uid, nome, coordinate, durata):
        if not self.attivo: return
        try:
            coord_json = json.dumps(coordinate)
            self.client.table("percorsi").insert({"user_id": uid, "nome": nome, "coordinate_json": coord_json, "durata": durata}).execute()
        except Exception as e: print(e)

    def leggi_percorsi(self, uid):
        if not self.attivo: return []
        try: return self.client.table("percorsi").select("*").eq("user_id", uid).order("created_at", desc=True).execute().data
        except: return []

    # --- SOCIAL ---
    def elimina_post(self, pid):
        if self.attivo: 
            try: self.client.table("post").delete().eq("id", pid).execute()
            except: pass
    def banna_utente(self, u):
        if self.attivo:
            try: self.client.table("utenti").update({"bannato": True}).eq("username", u).execute()
            except: pass
    def get_post_by_id(self, pid):
        if not self.attivo: return None
        try: return self.client.table("post").select("*").eq("id", pid).execute().data[0]
        except: return None
    def leggi_post(self):
        if not self.attivo: return []
        try: return self.client.table("post").select("*").order("created_at", desc=True).execute().data
        except: return []
    def conta_social(self, pid):
        l, f, c = 0, 0, 0
        if self.attivo:
            try:
                res = self.client.table("voti").select("tipo").eq("post_id", pid).execute()
                for r in res.data:
                    if r['tipo'] == 'Like': l+=1
                    elif r['tipo'] == 'Fake': f+=1
                c = self.client.table("commenti").select("id", count="exact").eq("post_id", pid).execute().count
            except: pass
        return l, f, c
    def invia_voto(self, pid, uid, t):
        if self.attivo:
            try: 
                self.client.table("voti").insert({"post_id": pid, "user_id": uid, "tipo": t}).execute(); return True
            except: return False
        return False
    def scrivi_commento(self, pid, aut, txt, aut_post):
        if self.attivo:
            try:
                self.client.table("commenti").insert({"post_id": pid, "autore": aut, "testo": txt}).execute()
                if aut != aut_post: self.client.table("notifiche").insert({"user_id": aut_post, "testo": f"{aut} ha commentato!", "post_id": pid}).execute()
            except: pass
    def leggi_commenti(self, pid):
        if not self.attivo: return []
        try: return self.client.table("commenti").select("*").eq("post_id", pid).order("created_at", desc=True).execute().data
        except: return []
    def elimina_commento(self, cid):
        if self.attivo: 
            try: self.client.table("commenti").delete().eq("id", cid).execute()
            except: pass
    def conta_notifiche_non_lette(self, u):
        if not self.attivo: return 0
        try: return self.client.table("notifiche").select("id", count="exact").eq("user_id", u).eq("letto", False).execute().count
        except: return 0
    def leggi_notifiche(self, u):
        if not self.attivo: return []
        try: return self.client.table("notifiche").select("*").eq("user_id", u).order("created_at", desc=True).execute().data
        except: return []
    def segna_tutte_lette(self, u):
        if self.attivo: 
            try: self.client.table("notifiche").update({"letto": True}).eq("user_id", u).execute()
            except: pass

# --- APP ---
def main(page: ft.Page):
    page.title = "Gallura Mycelium"
    page.bgcolor = "#121212"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "auto"
    page.keep_screen_on = True 
    
    # Audio Muto
    audio_silenzioso = ft.Audio(src="https://github.com/anars/blank-audio/raw/master/10-minutes-of-silence.mp3", autoplay=False, volume=0, release_mode="loop")
    page.overlay.append(audio_silenzioso)

    cloud = CloudManager()
    user = {"name": None, "comune": None, "is_admin": False}
    
    geolocator = ft.Geolocator()
    page.overlay.append(geolocator)
    map_state = {
        "recording": False, 
        "path": [], 
        "pos": [40.936, 9.160], 
        "start_time": 0
    }

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    img_temp = ft.Image(visible=False, height=200)
    path_box = [""]

    def on_file(e):
        if e.files: path_box[0]=e.files[0].path; img_temp.src=e.files[0].path; img_temp.visible=True; page.update()
    file_picker.on_result = on_file

    def aggiorna_nav(e=None):
        idx = e.control.selected_index if e else 0
        n = cloud.conta_notifiche_non_lette(user['name']) if user['name'] else 0
        page.navigation_bar = ft.NavigationBar(
            selected_index=idx, bgcolor="#222222", on_change=cambio_tab,
            destinations=[
                ft.NavigationBarDestination(icon="home", label="Home"),
                ft.NavigationBarDestination(icon="menu_book", label="Guida"),
                ft.NavigationBarDestination(icon="map", label="Mappa"),
                ft.NavigationBarDestination(icon="add_a_photo", label="Carica"),
                ft.NavigationBarDestination(icon="forum", label="Forum"),
                ft.NavigationBarDestination(icon=ft.Icon(ft.icons.NOTIFICATIONS), label=f"Notifiche ({n})" if n>0 else "Notifiche"),
            ]
        )
        page.clean()
        if idx==0: show_home()
        elif idx==1: show_guida()
        elif idx==2: show_mappa_container()
        elif idx==3: show_upload()
        elif idx==4: show_forum()
        elif idx==5: show_notifiche()
        page.add(page.navigation_bar); page.update()

    def cambio_tab(e): aggiorna_nav(e)

    # --- CONTAINER MAPPA (TRACKER + ARCHIVIO) ---
    def show_mappa_container():
        sub_page = ft.Column(expand=True)

        def switch_mode(e):
            mode = e.control.data
            sub_page.controls.clear()
            if mode == "tracker": show_tracker(sub_page)
            else: show_archivio(sub_page)
            page.update()

        header = ft.Row([
            ft.ElevatedButton("🔴 REGISTRA", data="tracker", on_click=switch_mode, bgcolor="#333333", color="white", expand=True),
            ft.ElevatedButton("📂 ARCHIVIO", data="archivio", on_click=switch_mode, bgcolor="#333333", color="white", expand=True)
        ])

        show_tracker(sub_page) # Default
        page.add(ft.Column([header, ft.Container(content=sub_page, expand=True)], expand=True))

    def show_tracker(container):
        map_widget = map.Map(
            expand=True,
            configuration=map.MapConfiguration(
                initial_center=map.MapLatitudeLongitude(map_state["pos"][0], map_state["pos"][1]),
                initial_zoom=15,
            ),
            layers=[
                map.TileLayer(url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                map.PolylineLayer(polylines=[]),
                map.MarkerLayer(markers=[]),
            ],
        )

        txt_stat = ft.Text("STANDBY", color="grey", weight="bold")
        
        # Dashboard Layer
        dashboard_layer = ft.Container(
            visible=map_state["recording"],
            bgcolor="#DD000000", expand=True,
            content=ft.Column([
                ft.Text("MODALITÀ CAMMINATA", size=20, weight="bold", color="white"),
                ft.Container(height=20),
                ft.ElevatedButton("🍄 FUNGO", bgcolor="green", color="white", width=250, height=80, on_click=lambda _: quick_add("Fungo")),
                ft.Container(height=10),
                ft.ElevatedButton("🚗 AUTO", bgcolor="blue", color="white", width=250, height=80, on_click=lambda _: quick_add("Auto")),
                ft.Container(height=10),
                ft.ElevatedButton("📍 PUNTO", bgcolor="orange", color="white", width=250, height=80, on_click=lambda _: quick_add("Punto Generico")),
                ft.Container(height=40),
                ft.ElevatedButton("STOP REGISTRAZIONE", bgcolor="red", color="white", on_click=lambda _: toggle_rec(None))
            ], alignment="center", horizontal_alignment="center")
        )

        def ridisegna():
            map_widget.layers[1].polylines = [map.Polyline(coordinates=[map.MapLatitudeLongitude(x, y) for x,y in map_state["path"]], color="red", stroke_width=4)]
            map_widget.layers[2].markers = [map.Marker(content=ft.Icon(ft.icons.MY_LOCATION, color="red", size=30), coordinates=map.MapLatitudeLongitude(map_state["pos"][0], map_state["pos"][1]))]
            page.update()

        def on_gps(e):
            if e.latitude:
                map_state["pos"] = [e.latitude, e.longitude]
                if map_state["recording"]: map_state["path"].append([e.latitude, e.longitude])
                ridisegna()
        geolocator.on_position_change = on_gps

        def quick_add(desc):
            cloud.salva_marker(user['name'], map_state["pos"][0], map_state["pos"][1], desc)
            page.show_snack_bar(ft.SnackBar(ft.Text(f"{desc} SALVATO!")))
            
        def toggle_rec(e):
            if not map_state["recording"]:
                map_state["recording"] = True; map_state["path"] = []; map_state["start_time"] = time.time()
                txt_stat.value = "🔴 REC"; txt_stat.color = "red"
                geolocator.request_permission(); audio_silenzioso.play()
                dashboard_layer.visible = True
            else:
                map_state["recording"] = False
                dashboard_layer.visible = False; page.update()
                audio_silenzioso.pause()
                
                durata_sec = int(time.time() - map_state["start_time"])
                hh = durata_sec // 3600
                mm = (durata_sec % 3600) // 60
                durata_fmt = f"{hh}h {mm}m"

                if len(map_state["path"])>2:
                    nome = f"Giro del {time.strftime('%d/%m %H:%M')}"
                    cloud.salva_percorso(user['name'], nome, map_state["path"], durata_fmt)
                    page.show_snack_bar(ft.SnackBar(ft.Text(f"Salvata: {durata_fmt}")))
                txt_stat.value = "STANDBY"; txt_stat.color = "grey"
            page.update()

        ridisegna()
        container.controls.append(ft.Stack([
            map_widget,
            ft.Container(bgcolor="#CC000000", padding=10, border_radius=10, bottom=20, left=10, right=10, content=ft.Row([txt_stat, ft.Switch(label="REGISTRA", value=map_state["recording"], active_color="red", on_change=toggle_rec)], alignment="spaceBetween")),
            dashboard_layer
        ], expand=True))

    def show_archivio(container):
        polylines = []
        markers = []
        all_paths = cloud.leggi_percorsi(user['name'])
        
        for p in all_paths:
            try:
                coords = json.loads(p['coordinate_json'])
                polylines.append(map.Polyline(coordinates=[map.MapLatitudeLongitude(x,y) for x,y in coords], color="blue", stroke_width=3))
            except: pass
            
        for m in cloud.leggi_markers(user['name']):
            markers.append(map.Marker(content=ft.Icon(ft.icons.LOCATION_ON, color="green", tooltip=m['descrizione']), coordinates=map.MapLatitudeLongitude(m['lat'], m['lon'])))

        map_global = map.Map(
            expand=True,
            configuration=map.MapConfiguration(initial_center=map.MapLatitudeLongitude(map_state["pos"][0], map_state["pos"][1]), initial_zoom=12),
            layers=[
                map.TileLayer(url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                map.PolylineLayer(polylines=polylines),
                map.MarkerLayer(markers=markers),
            ],
        )

        lv_camminate = ft.ListView(expand=True, spacing=10, padding=10)
        if not all_paths: lv_camminate.controls.append(ft.Text("Nessuna camminata registrata."))
        else:
            for p in all_paths:
                durata = p.get('durata', 'N/D')
                lv_camminate.controls.append(ft.Container(bgcolor="#1e1e1e", padding=15, border_radius=10, content=ft.Row([ft.Icon(ft.icons.DIRECTIONS_WALK, color="yellow"), ft.Column([ft.Text(p['nome'], weight="bold", size=16), ft.Text(f"Durata: {durata}", color="grey")], expand=True)])))

        container.controls.append(ft.Column([
            ft.Container(content=map_global, height=300, border=ft.border.all(1, "grey")),
            ft.Container(padding=10, content=ft.Text("DIARIO DI BORDO", size=20, weight="bold")),
            lv_camminate
        ], expand=True))

    # --- LOGIN ---
    def show_login():
        page.clean()
        u = ft.TextField(label="Utente"); p = ft.TextField(label="Password", password=True)
        def az(e):
            d, m = cloud.login(u.value, p.value)
            if d: user.update(d); aggiorna_nav()
            else: page.show_snack_bar(ft.SnackBar(ft.Text(m), bgcolor="red")); page.update()
        page.add(ft.Container(padding=20, content=ft.Column([ft.Icon("forest", size=80, color="green"), ft.Text("GALLURA MYCELIUM", size=30, weight="bold"), ft.Container(height=20), u, p, ft.ElevatedButton("ENTRA", on_click=az), ft.TextButton("Registrati", on_click=lambda _: show_reg())], horizontal_alignment="center", alignment="center")))
        page.update()

    def show_reg():
        page.clean()
        u = ft.TextField(label="Utente"); p = ft.TextField(label="Password", password=True); c = ft.Dropdown(label="Comune", options=[ft.dropdown.Option(x) for x in COMUNI_GALLURA])
        def az(e):
            if not u.value or not p.value or not c.value: return
            ok, m = cloud.registra(u.value, p.value, c.value)
            page.show_snack_bar(ft.SnackBar(ft.Text(m)))
            if ok: time.sleep(1); show_login()
            page.update()
        page.add(ft.Container(padding=20, content=ft.Column([ft.Text("REGISTRAZIONE"), u, p, c, ft.ElevatedButton("CONFERMA", on_click=az), ft.TextButton("Annulla", on_click=lambda _: show_login())], horizontal_alignment="center")))
        page.update()

    # --- PAGINE STANDARD ---
    def show_home():
        rank = cloud.classifica(); col_r = ft.Column()
        for i, (c, pt) in enumerate(rank[:5]): col_r.controls.append(ft.Container(bgcolor="#222222", padding=10, border_radius=5, content=ft.Row([ft.Text(f"{i+1}. {c}", color="yellow" if i==0 else "white"), ft.Text(str(pt), weight="bold")])))
        t = f"Ciao {user['name']} 🛡️" if user['is_admin'] else f"Ciao {user['name']}"
        page.add(ft.Container(padding=20, content=ft.Column([ft.Text(t, size=24, color="red" if user['is_admin'] else "white", weight="bold"), ft.Divider(), ft.Text("CLASSIFICA", color="yellow"), col_r])))

    def show_guida():
        lv = ft.Column(scroll="auto", expand=True)
        for k, v in DB_FUNGHI.items():
            lv.controls.append(ft.Container(bgcolor="#1e1e1e", padding=10, margin=5, border_radius=10, content=ft.Column([ft.Image(src=v['img'], height=150, fit=ft.ImageFit.COVER), ft.Text(k, size=20, weight="bold", color="green" if v['ok'] else "red"), ft.Text(v['desc']), ft.ElevatedButton("SCHEDA", on_click=lambda e, x=k: show_det_fungo(x))])))
        page.add(ft.Container(padding=10, expand=True, content=lv))

    def show_det_fungo(k):
        page.clean(); d=DB_FUNGHI[k]; c="green" if d['ok'] else "red"
        page.add(ft.Container(padding=10, content=ft.Column([ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: aggiorna_nav())]), ft.Image(src=d['img']), ft.Text(k, size=30, color=c), ft.Text("COMMESTIBILE" if d['ok'] else "TOSSICO", color=c), ft.Text(d['full'])], scroll="auto"))); page.update()

    def show_forum():
        lv = ft.Column(scroll="auto", expand=True)
        for p in cloud.leggi_post():
            l, f, c = cloud.conta_social(p['id'])
            bl = ft.ElevatedButton(f"👍 {l}"); bf = ft.ElevatedButton(f"🤥 {f}", bgcolor="red", color="white")
            def v(e, pid=p['id'], t="Like", b1=bl, b2=bf): 
                if cloud.invia_voto(pid, user['name'], t): b1.text=f"👍 {int(b1.text.split()[1])+1}" if t=="Like" else b1.text; b2.text=f"🤥 {int(b2.text.split()[1])+1}" if t=="Fake" else b2.text; page.update()
            
            cmds = ft.Row()
            if user['is_admin']: cmds = ft.Row([ft.IconButton(icon="delete", icon_color="red", on_click=lambda e, x=p['id']: (cloud.elimina_post(x), aggiorna_nav(e))), ft.IconButton(icon="block", icon_color="red", on_click=lambda e, x=p['autore']: (cloud.banna_utente(x), page.update()))])
            
            lv.controls.append(ft.Container(bgcolor="#1e1e1e", padding=10, margin=5, border_radius=10, content=ft.Column([ft.Row([ft.Text(p['autore'], weight="bold"), cmds], alignment="spaceBetween"), ft.Image(src=f"{STORAGE_URL}/{p['image_path']}", height=200, fit=ft.ImageFit.COVER), ft.Text(p['descrizione']), ft.Row([ft.Container(content=bl, on_click=lambda e: v(e)), ft.Container(content=bf, on_click=lambda e: v(e, t="Fake"))], alignment="center"), ft.OutlinedButton(f"💬 {c} - INGRANDISCI", on_click=lambda e, x=p: show_det_post(x))])))
        page.add(ft.Container(padding=10, expand=True, content=lv))

    def show_det_post(p):
        page.clean(); l=ft.Column(); tf=ft.TextField(hint_text="Scrivi...", expand=True)
        def ric(): 
            l.controls.clear()
            for c in cloud.leggi_commenti(p['id']):
                cmds = ft.Row()
                if user['is_admin']: cmds = ft.Row([ft.IconButton(icon="delete", icon_color="red", icon_size=16, on_click=lambda e, x=c['id']: (cloud.elimina_commento(x), ric())), ft.IconButton(icon="block", icon_color="red", icon_size=16, on_click=lambda e, x=c['autore']: (cloud.banna_utente(x), page.update()))])
                l.controls.append(ft.Container(bgcolor="#222222", padding=5, margin=2, content=ft.Row([ft.Column([ft.Text(c['autore'], color="green"), ft.Text(c['testo'])]), cmds], alignment="spaceBetween")))
            page.update()
        def inv(e): 
            if tf.value: cloud.scrivi_commento(p['id'], user['name'], tf.value, p['autore']); tf.value=""; ric()
        ric()
        page.add(ft.Container(padding=10, content=ft.Column([ft.IconButton(icon="arrow_back", on_click=lambda _: aggiorna_nav()), ft.Image(src=f"{STORAGE_URL}/{p['image_path']}"), ft.Text(p['descrizione']), ft.Text("Commenti:"), l, ft.Row([tf, ft.IconButton(icon="send", on_click=inv)])], scroll="auto"))); page.update()

    def show_notifiche():
        lv = ft.Column(scroll="auto", expand=True)
        for n in cloud.leggi_notifiche(user['name']):
            bg = "#333333" if not n['letto'] else "#1e1e1e"
            def vai(e, pid=n.get('post_id')): 
                if pid and cloud.get_post_by_id(pid): show_det_post(cloud.get_post_by_id(pid))
            lv.controls.append(ft.Container(bgcolor=bg, padding=15, margin=5, border_radius=10, on_click=vai, content=ft.Row([ft.Icon("mark_email_unread" if not n['letto'] else "check", color="yellow" if not n['letto'] else "grey"), ft.Text(n['testo'], expand=True)])))
        page.add(ft.Container(padding=10, expand=True, content=ft.Column([ft.Row([ft.Text("NOTIFICHE"), ft.IconButton(icon="done_all", on_click=lambda e: (cloud.segna_tutte_lette(user['name']), aggiorna_nav()))], alignment="spaceBetween"), lv])))

    def show_upload():
        desc = ft.TextField(label="Descrizione")
        def pub(e):
            if path_box[0]: 
                fn=f"{int(time.time())}_{user['name']}.jpg"
                if cloud.upload_foto(path_box[0], fn): cloud.nuovo_post(user['name'], user['comune'], desc.value, fn); page.show_snack_bar(ft.SnackBar(ft.Text("Fatto!"))); page.navigation_bar.selected_index=4; show_forum(); page.add(page.navigation_bar)
        page.add(ft.Container(padding=20, content=ft.Column([ft.Text("NUOVO"), ft.ElevatedButton("FOTO", on_click=lambda _: file_picker.pick_files()), img_temp, desc, ft.ElevatedButton("PUBBLICA", on_click=pub)], horizontal_alignment="center")))

    show_login()

ft.app(target=main)
