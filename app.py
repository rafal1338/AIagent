# app.py
import os
import threading
import time
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request, Response, stream_with_context
from devteam_runner import run_devteam_pipeline
from tools import msg_queue, system_log, PROJECT_DIR

load_dotenv()
app = Flask(__name__)

is_running = False

def background_worker(task_input):
    global is_running
    is_running = True
    try:
        result = run_devteam_pipeline(task_input)
        system_log(f"__RESULT_START__\n{result}\n__RESULT_END__")
    except Exception as e:
        system_log(f"❌ Błąd krytyczny: {str(e)}")
    finally:
        is_running = False
        system_log("__DONE__")

def get_file_tree(path, root_path=None):
    """Rekurencyjnie buduje strukturę plików dla widoku drzewa z relatywnymi ścieżkami"""
    if root_path is None:
        root_path = path
    tree = []
    try:
        with os.scandir(path) as entries:
            entries = sorted(list(entries), key=lambda e: (not e.is_dir(), e.name.lower()))
            
            for entry in entries:
                if entry.name in {'.git', '__pycache__', 'venv', 'node_modules', '.vscode', '.idea', 'bin', 'obj'}:
                    continue
                
                # Obliczamy ścieżkę względną (np. "src/main.py") do użycia w API
                rel_path = os.path.relpath(entry.path, root_path).replace("\\", "/")
                
                if entry.is_dir():
                    tree.append({
                        "name": entry.name,
                        "type": "folder",
                        "path": rel_path,
                        "children": get_file_tree(entry.path, root_path)
                    })
                else:
                    tree.append({
                        "name": entry.name,
                        "type": "file",
                        "path": rel_path
                    })
    except Exception:
        pass
    return tree

@app.route("/", methods=["GET"])
def index():
    return render_template("base_template.html")

@app.route("/run", methods=["POST"])
def run_agent():
    global is_running
    if is_running:
        return {"status": "busy", "message": "Agent już pracuje!"}, 409
    
    data = request.json
    task = data.get("task_input", "")
    if not task: return {"status": "error", "message": "Brak zadania"}, 400

    with msg_queue.mutex:
        msg_queue.queue.clear()

    thread = threading.Thread(target=background_worker, args=(task,))
    thread.daemon = True
    thread.start()
    return {"status": "started"}

@app.route("/stream")
def stream():
    def generate():
        while True:
            try:
                msg = msg_queue.get(timeout=1.0)
                yield f"data: {json.dumps({'msg': msg})}\n\n"
                if msg == "__DONE__": break
            except:
                if not is_running and msg_queue.empty(): break
                continue
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/files")
def files():
    if not os.path.exists(PROJECT_DIR): return json.dumps([])
    return json.dumps(get_file_tree(PROJECT_DIR))

# --- NOWE ENDPOINTY DLA EDYTORA ---

@app.route("/get_file")
def get_file():
    """Pobiera treść pliku do edycji"""
    filepath = request.args.get('path')
    if not filepath: return "Brak ścieżki", 400
    
    # Zabezpieczenie Path Traversal
    safe_path = os.path.abspath(os.path.join(PROJECT_DIR, filepath))
    if not safe_path.startswith(os.path.abspath(PROJECT_DIR)):
         return "Nieprawidłowa ścieżka (Access Denied)", 403
         
    try:
        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Błąd odczytu: {str(e)}", 500

@app.route("/save_file", methods=['POST'])
def save_file_endpoint():
    """Zapisuje zmiany w pliku"""
    data = request.json
    filepath = data.get('path')
    content = data.get('content')
    
    if not filepath: return {"status": "error", "message": "Brak ścieżki"}, 400
    
    safe_path = os.path.abspath(os.path.join(PROJECT_DIR, filepath))
    if not safe_path.startswith(os.path.abspath(PROJECT_DIR)):
         return {"status": "error", "message": "Nieprawidłowa ścieżka"}, 403
         
    try:
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("program", exist_ok=True)
    
    port = int(os.getenv("FLASK_PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() in ('true', '1', 't')
    
    print(f"✅ Serwer startuje na http://127.0.0.1:{port}")
    app.run(debug=debug_mode, host="127.0.0.1", port=port, use_reloader=False)