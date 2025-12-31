import flet as ft
import traceback

# --- TUE CHIAVI ---
SUPABASE_URL = "https://zdyjwoxfqzpiexuoetyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkeWp3b3hmcXpwaWV4dW9ldHlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxNTMzNDAsImV4cCI6MjA4MjcyOTM0MH0.ed0kcRIQm01BPGhLnyzBCsc3KxP82VUDo-6hytJXsn8"

def main(page: ft.Page):
    page.title = "TEST CONNESSIONE"
    page.bgcolor = "black"
    page.scroll = "auto"

    log_box = ft.Text("In attesa...", color="white", size=16)

    def log(msg, color="white"):
        log_box.value += f"\n[{color}] {msg}"
        log_box.update()

    def test_import(e):
        log("1. Test Import Libreria...", "yellow")
        try:
            from supabase import create_client, Client
            log("   Libreria 'supabase' TROVATA! ✅", "green")
            test_connection()
        except ImportError as ex:
            log(f"   ERRORE: Libreria mancante!\n{ex}", "red")
        except Exception as ex:
            log(f"   ERRORE GENERICO:\n{traceback.format_exc()}", "red")

    def test_connection():
        log("2. Tentativo Connessione...", "yellow")
        try:
            from supabase import create_client
            # Crea client
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            log("   Client creato. Tento lettura DB...", "yellow")
            
            # Prova a leggere la tabella utenti
            response = client.table("utenti").select("*").execute()
            
            log(f"   SUCCESSO! 🟢\n   Dati ricevuti: {len(response.data)} utenti trovati.", "green")
            log(f"   Raw Data: {response.data}", "grey")
            
        except Exception as ex:
            # Cattura l'errore esatto
            err_msg = traceback.format_exc()
            log(f"   FALLIMENTO 🔴\n   Ecco l'errore:\n{err_msg}", "red")

    btn = ft.ElevatedButton("AVVIA TEST DIAGNOSTICO", on_click=test_import, bgcolor="blue", color="white")

    page.add(
        ft.Column([
            ft.Text("DIAGNOSTICA GALLURA", size=30, weight="bold", color="white"),
            ft.Text("Premi il tasto per vedere l'errore.", color="grey"),
            btn,
            ft.Container(content=log_box, bgcolor="#111111", padding=10, border_radius=10, expand=True)
        ])
    )

ft.app(target=main)
