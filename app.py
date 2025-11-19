# app.py
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from devteam_runner import run_devteam_pipeline

# Wczytujemy konfigurację przy starcie
load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    task = ""
    error = None

    if request.method == "POST":
        task = request.form.get("task_input")
        if task:
            try:
                # Uruchamiamy pipeline DevTeam
                result = run_devteam_pipeline(task)
            except Exception as e:
                error = f"Błąd aplikacji: {str(e)}"
                print(f"ERROR: {e}")
        else:
            error = "Podaj treść zadania!"

    return render_template("base_template.html", result=result, task=task, error=error)

if __name__ == "__main__":
    # Upewnij się, że foldery istnieją
    os.makedirs("templates", exist_ok=True)
    os.makedirs("program", exist_ok=True)
    
    # Pobieramy konfigurację serwera z .env (z domyślnymi wartościami)
    port = int(os.getenv("FLASK_PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() in ('true', '1', 't')
    
    print(f"✅ Serwer Flask startuje na http://127.0.0.1:{port}")
    print(f"   Tryb Debug: {debug_mode}")
    print("ℹ️  Uwaga: Auto-reload wyłączony ze względu na kompatybilność z Windows/Python 3.13")
    
    # NAPRAWA BŁĘDU WinError 10038:
    # Ustawiamy use_reloader=False, aby uniknąć konfliktu gniazd na Windowsie.
    app.run(debug=debug_mode, host="127.0.0.1", port=port, use_reloader=False)