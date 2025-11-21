# tools.py
import os
import queue
import json
from langchain_core.tools import tool

PROJECT_DIR = "program"
MAP_FILE = os.path.join(PROJECT_DIR, "project_map.json")

os.makedirs(PROJECT_DIR, exist_ok=True)

# --- SYSTEM LOGOWANIA ---
msg_queue = queue.Queue()

def system_log(message: str):
    print(f"[SERVER LOG] {message}")
    msg_queue.put(message)

# Foldery ignorowane
IGNORE_DIRS = {
    '__pycache__', 'node_modules', 'venv', '.git', '.vscode', 
    'bin', 'obj', 'Debug', 'Release', '.idea'
}

# --- OBSŁUGA MAPY PROJEKTU ---
def load_project_map():
    if os.path.exists(MAP_FILE):
        try:
            with open(MAP_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_project_map(data):
    try:
        with open(MAP_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except: pass

def get_project_knowledge_base():
    """
    Generuje BOGATY opis struktury dla Agenta.
    To jest kluczowe, żeby agent nie tworzył duplikatów.
    """
    data = load_project_map()
    if not data:
        return "(PROJEKT JEST PUSTY)"
    
    report = "🧠 WIEDZA O PROJEKCIE (Istniejące moduły):\n"
    for path, info in data.items():
        desc = info.get('description', 'Brak opisu')
        report += f"📄 PLIK: {path}\n   Opis: {desc}\n"
    
    report += "\nZASADA: Jeśli musisz zmienić logikę opisaną powyżej, EDYTUJ ten plik. NIE TWORZ NOWEGO."
    return report

# --- NARZĘDZIA ---

@tool
def write_code_file(filepath: str, content: str, description: str) -> str:
    """
    Zapisuje kompletny kod do pliku. WYMAGA PODANIA OPISU (description).
    
    Args:
        filepath: ścieżka (np. 'src/auth_service.py')
        content: PEŁNY, działający kod (bez skrótów).
        description: Co ten kod robi? (np. "Logika logowania i rejestracji użytkowników").
    """
    full_path = os.path.join(PROJECT_DIR, filepath)
    directory = os.path.dirname(full_path)
    
    if not description or len(description) < 5:
        return "❌ BŁĄD: Musisz podać sensowny opis pliku w parametrze 'description', aby zaktualizować mapę projektu."

    try:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Aktualizacja mapy wiedzy
        current_map = load_project_map()
        current_map[filepath] = {
            "description": description,
            "last_modified": "Teraz"
        }
        save_project_map(current_map)
        
        system_log(f"💾 Zapisano: {filepath}")
        return f"✅ Sukces. Plik '{filepath}' został zapisany i zindeksowany w mapie projektu."
    except Exception as e:
        system_log(f"❌ Błąd zapisu {filepath}: {e}")
        return f"❌ Błąd zapisu: {e}"

@tool
def read_project_spec(filepath: str) -> str:
    """Odczytuje treść pliku."""
    full_path = os.path.join(PROJECT_DIR, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"❌ Brak pliku: {filepath}"
    except Exception as e:
        return f"❌ Błąd odczytu: {e}"

@tool
def list_project_files() -> str:
    """Zwraca mapę wiedzy (zamiast surowej listy)."""
    return get_project_knowledge_base()

coder_tools = [write_code_file, read_project_spec, list_project_files]