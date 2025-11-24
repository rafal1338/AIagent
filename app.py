# app.py
import os
import threading
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request, Response, stream_with_context
from devteam_runner import run_devteam_pipeline
from tools import msg_queue, system_log, PROJECT_DIR, get_project_knowledge_base

load_dotenv()
app = Flask(__name__)
is_running = False

def background_worker(task_input):
    global is_running
    is_running = True
    try:
        result = run_devteam_pipeline(task_input)
        # Wynik końcowy wysyłamy jako specjalny log
        system_log(f"__RESULT_START__\n{result}\n__RESULT_END__")
    except Exception as e:
        system_log(f"❌ Error: {str(e)}")
    finally:
        is_running = False
        system_log("__DONE__")

def get_file_tree_json(path):
    # (Ta sama funkcja co wcześniej, skrócona dla czytelności)
    tree = []
    try:
        with os.scandir(path) as entries:
            entries = sorted(list(entries), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.name in {'.git', '__pycache__', 'venv', 'project_map.json'}: continue
                if entry.is_dir():
                    tree.append({"name": entry.name, "type": "folder", "path": entry.path, "children": get_file_tree_json(entry.path)})
                else:
                    tree.append({"name": entry.name, "type": "file", "path": os.path.relpath(entry.path, PROJECT_DIR).replace("\\", "/")})
    except: pass
    return tree

@app.route("/")
def index(): return render_template("base_template.html")

@app.route("/run", methods=["POST"])
def run():
    global is_running
    if is_running: return {"status": "busy"}, 409
    task = request.json.get("task_input")
    if not task: return {"status": "error"}, 400
    with msg_queue.mutex: msg_queue.queue.clear()
    threading.Thread(target=background_worker, args=(task,), daemon=True).start()
    return {"status": "started"}

@app.route("/stream")
def stream():
    def generate():
        while True:
            try:
                # Pobieramy obiekt wiadomości
                msg_obj = msg_queue.get(timeout=1.0)
                
                # Serializujemy go do JSON i wysyłamy
                yield f"data: {json.dumps(msg_obj)}\n\n"
                
                if msg_obj.get("content") == "__DONE__": break
            except:
                if not is_running and msg_queue.empty(): break
                continue
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/files")
def files():
    if not os.path.exists(PROJECT_DIR): return json.dumps([])
    return json.dumps(get_file_tree_json(PROJECT_DIR))

@app.route("/get_file")
def get_file():
    filepath = request.args.get('path')
    try:
        with open(os.path.join(PROJECT_DIR, filepath), 'r', encoding='utf-8') as f: return f.read()
    except Exception as e: return str(e), 500

@app.route("/save_file", methods=['POST'])
def save_file():
    data = request.json
    try:
        with open(os.path.join(PROJECT_DIR, data['path']), 'w', encoding='utf-8') as f: f.write(data['content'])
        return {"status": "ok"}
    except Exception as e: return {"status": "error", "msg": str(e)}, 500

if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("program", exist_ok=True)
    app.run(debug=True, port=5000, use_reloader=False)