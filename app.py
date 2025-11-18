from flask import Flask, render_template, request
from devteam_runner import run_devteam_pipeline
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        task = request.form.get("task_input")
        
        if task:
            try:
                # Uruchomienie pipeline'u agentów
                print(f"Otrzymano zadanie: {task}")
                result_report = run_devteam_pipeline(task)
                
                return render_template("base_template.html", result=result_report, task=task)
            except Exception as e:
                error_msg = f"Wystąpił krytyczny błąd w pipeline agentów: {e}"
                print(f"[BŁĄD APLIKACJI FLASK]: {e}")
                return render_template("base_template.html", error=error_msg, task=task)
        else:
            return render_template("base_template.html", error="Proszę podać zadanie.", task=task)
            
    # Domyślne wyświetlanie strony GET
    return render_template("base_template.html")

if __name__ == "__main__":
    # Upewnij się, że katalog dla szablonów istnieje
    os.makedirs("templates", exist_ok=True)
    
    print("🤖 Uruchamiam serwer Flask na http://127.0.0.1:5000")
    print("Upewnij się, że serwer Ollama działa.")
    app.run(debug=True, host="127.0.0.1", port=5000)