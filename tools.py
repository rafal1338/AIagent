# tools.py
import os
import queue
import json
from langchain_core.tools import tool

PROJECT_DIR = "program"
MAP_FILE = os.path.join(PROJECT_DIR, "project_map.json")

os.makedirs(PROJECT_DIR, exist_ok=True)

msg_queue = queue.Queue()

def system_log(message: str, event_type: str = "log"):
    """
    Wysyła wiadomość do UI.
    event_type: 'log' (tekst) lub 'refresh' (sygnał do odświeżenia drzewa)
    """
    if event_type == "log":
        print(f"[SERVER LOG] {message}")
    msg_queue.put({"type": event_type, "content": message})

IGNORE_DIRS = {
    '__pycache__', 'node_modules', 'venv', '.git', '.vscode', 
    'bin', 'obj', 'Debug', 'Release', '.idea'
}

def load_project_map():
    if os.path.exists(MAP_FILE):
        try:
            with open(MAP_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def save_project_map(data):
    try:
        with open(MAP_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except: pass

def get_project_knowledge_base():
    data = load_project_map()
    if not data: return "(PROJEKT JEST PUSTY)"
    report = "🧠 MAPA PLIKÓW:\n"
    for path, info in data.items():
        report += f"- {path}: {info.get('description', '')}\n"
    return report

@tool
def write_code_file(filepath: str, content: str, description: str) -> str:
    """
    Zapisuje kod i aktualizuje mapę.
    """
    full_path = os.path.join(PROJECT_DIR, filepath)
    directory = os.path.dirname(full_path)
    
    if not description or len(description) < 3:
        return "❌ BŁĄD: Podaj parametr 'description'."

    try:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        current_map = load_project_map()
        current_map[filepath] = {"description": description}
        save_project_map(current_map)
        
        system_log(f"💾 Zapisano: {filepath}")
        # OPTYMALIZACJA: Wysyłamy sygnał do UI, żeby odświeżyło drzewko TERAZ
        system_log("", event_type="refresh") 
        
        return f"✅ Zapisano: {filepath}"
    except Exception as e:
        return f"❌ Błąd: {e}"

@tool
def read_project_spec(filepath: str) -> str:
    """
    Odczytuje treść pliku z projektu.
    """
    full_path = os.path.join(PROJECT_DIR, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f: return f.read()
    except: return f"❌ Błąd odczytu: {filepath}"

@tool
def list_project_files() -> str:
    """
    Zwraca listę plików w projekcie wraz z ich opisami z mapy projektu.
    """
    return get_project_knowledge_base()

coder_tools = [write_code_file, read_project_spec, list_project_files]