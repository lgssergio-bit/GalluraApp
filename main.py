import flet as ft
import time
import traceback
from supabase import create_client, Client

# --- CONFIGURAZIONE ---
SUPABASE_URL = "https://zdyjwoxfqzpiexuoetyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkeWp3b3hmcXpwaWV4dW9ldHlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNTMzNDAsImV4cCI6MjA4MjcyOTM0MH0.ed0kcRIQm01BPGhLnyzBCsc3KxP82VUDo-6hytJXsn8"
STORAGE_URL = f"{SUPABASE_URL}/storage/v1/object/public/foto_funghi"

# --- DATI ---
COMUNI_GALLURA = ["Luras", "Calangianus", "Tempio", "Olbia", "Arzachena", "Santa Teresa", "Palau", "San Teodoro", "Budoni", "Badesi"]

# --- SETUP DATABASE ---
supabase = None
stato_connessione = "In attesa..."

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    stato_connessione = "Connesso ✅"
except Exception as e:
    stato_connessione = f"Errore Connessione ❌"

# --- FUNZIONI DATABASE ---
def db_registra(u, p, c):
    if not supabase: return False, "Database Offline"
    try:
        res = supabase.table("utenti").select("*").eq("username", u).execute()
        if res.data: return False, "Utente già esistente"
        supabase.table("utenti").insert({"username": u, "password": p, "comune": c}).execute()
        return True, "Registrato!"
    except Exception as e:
        return False, f"Err DB: {str(e)}"

def db_login(u, p):
    if not supabase: return None
    try:
        res = supabase.table("utenti").select("*").eq("username", u).eq("password", p).execute()
        if res.data: return res.data[0]
    except: pass
    return None

def db_classifica():
    if not supabase: return []
    punti = {c: 0 for c in COMUNI_GALLURA}
    try:
        res = supabase.table("post").select("comune").execute()
        for r in res.data:
            c = r.get('comune')
            if c in punti: punti[c] += 1
    except: pass
    return sorted(punti.items(), key=lambda x: x[1], reverse=True)

# --- INTERFACCIA ---
def main(page: ft.Page):
    page.title = "Gallura Mycelium"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.scroll = "auto"

    user_state = {"name": None, "comune": None}
    t_status = ft.Text(stato_connessione, color="yellow", size=12)

    def mostra_errore(msg):
        page.show_snack_bar(ft.SnackBar(ft.Text(f"ERRORE: {msg}"), bgcolor="red"))
        page.update()

    def vai_a_login():
        page.clean()
        
        u_box = ft.TextField(label="Utente", border_color="green")
        p_box = ft.TextField(label="Password", password=True, border_color="green")

        def azione_login(e):
            try:
                t_status.value = "Accesso..."
                page.update()
                user = db_login(u_box.value, p_box.value)
                if user:
                    user_state['name'] = user['username']
                    user_state['comune'] = user['comune']
                    vai_a_home()
                else:
                    mostra_errore("Dati errati")
            except Exception as ex: mostra_errore(str(ex))

        def azione_vai_registra(e): vai_a_registrazione()

        # FIX: Ho rimosso 'padding' dalla Column e messo tutto in un Container
        page.add(
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Container(height=50),
                    ft.Icon("forest", size=80, color="green"),
                    ft.Text("GALLURA MYCELIUM", size=30, weight="bold"),
                    t_status,
                    ft.Container(height=20),
                    u_box, p_box,
                    ft.ElevatedButton("ENTRA", on_click=azione_login, bgcolor="green", color="white", width=200),
                    ft.TextButton("Registrati", on_click=azione_vai_registra)
                ], horizontal_alignment="center", alignment="center")
            )
        )
        page.update()

    def vai_a_registrazione():
        try:
            page.clean()
            
            u_reg = ft.TextField(label="Scegli Nome Utente")
            p_reg = ft.TextField(label="Scegli Password", password=True)
            c_reg = ft.Dropdown(label="Il tuo Comune", options=[ft.dropdown.Option(x) for x in COMUNI_GALLURA])

            def azione_conferma_reg(e):
                try:
                    if not u_reg.value or not p_reg.value or not c_reg.value:
                        mostra_errore("Compila tutto")
                        return
                    
                    ok, msg = db_registra(u_reg.value, p_reg.value, c_reg.value)
                    if ok:
                        page.show_snack_bar(ft.SnackBar(ft.Text("Registrato!"), bgcolor="green"))
                        page.update()
                        time.sleep(1)
                        vai_a_login()
                    else:
                        mostra_errore(msg)
                except Exception as ex: mostra_errore(f"Crash Reg: {ex}")

            # FIX: Anche qui, Container con padding che avvolge la Colonna
            page.add(
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("REGISTRAZIONE", size=24, weight="bold"),
                        ft.Container(height=20),
                        u_reg, p_reg, c_reg,
                        ft.Container(height=20),
                        ft.ElevatedButton("REGISTRATI ORA", on_click=azione_conferma_reg, bgcolor="blue", color="white"),
                        ft.TextButton("Annulla", on_click=lambda e: vai_a_login())
                    ], horizontal_alignment="center")
                )
            )
            page.update()
        except Exception as ex:
            page.add(ft.Text(f"CRASH GRAFICO: {ex}", color="red"))
            page.update()

    def vai_a_home():
        try:
            page.clean()
            classifica = db_classifica()
            
            lista_classifica = ft.Column()
            for i, (com, pt) in enumerate(classifica[:5]):
                lista_classifica.controls.append(
                    ft.Container(
                        content=ft.Row([ft.Text(f"{i+1}. {com}"), ft.Text(f"{pt} pt", color="yellow")]),
                        bgcolor="#222222", padding=10, border_radius=5
                    )
                )

            # FIX: Container con padding
            page.add(
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text(f"Ciao {user_state['name']}!", size=24),
                        ft.Text(f"Comune: {user_state['comune']}", color="grey"),
                        ft.Divider(),
                        ft.Text("CLASSIFICA", color="yellow"),
                        lista_classifica,
                        ft.Container(height=50),
                        ft.Text("Benvenuto nella versione Cloud!", italic=True)
                    ])
                )
            )
            page.update()
        except Exception as ex: mostra_errore(f"Crash Home: {ex}")

    vai_a_login()

ft.app(target=main)
