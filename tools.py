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
    """Generuje czytelny opis struktury dla Agenta"""
    data = load_project_map()
    if not data:
        return "(Brak mapy projektu - projekt jest pusty)"
    
    report = "🗺️ MAPA PROJEKTU (Istniejące pliki i ich role):\n"
    for path, info in data.items():
        desc = info.get('description', 'Brak opisu')
        report += f"- {path}: {desc}\n"
    return report

# --- NARZĘDZIA ---

@tool
def write_code_file(filepath: str, content: str, description: str = "Kod źródłowy") -> str:
    """
    Zapisuje kod do pliku ORAZ aktualizuje mapę projektu.
    Args:
        filepath: ścieżka (np. 'src/main.py')
        content: treść pliku
        description: KRÓTKI opis, za co ten plik odpowiada (np. 'Logika logowania', 'Główny widok HTML'). TO JEST WAŻNE DLA UNIKANIA DUPLIKATÓW.
    """
    full_path = os.path.join(PROJECT_DIR, filepath)
    directory = os.path.dirname(full_path)
    
    try:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Aktualizacja mapy
        current_map = load_project_map()
        current_map[filepath] = {
            "description": description,
            "type": filepath.split('.')[-1] if '.' in filepath else 'unknown'
        }
        save_project_map(current_map)
        
        system_log(f"💾 Zapisano: {filepath} ({description})")
        return f"✅ Zapisano i zindeksowano: {filepath}"
    except Exception as e:
        system_log(f"❌ Błąd zapisu {filepath}: {e}")
        return f"❌ Błąd zapisu: {e}"

@tool
def read_project_spec(filepath: str) -> str:
    """Odczytuje plik."""
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
    """
    Zwraca strukturę plików.
    Dla Agenta lepiej używać get_project_knowledge_base (które jest wewnętrzne), 
    ale to narzędzie zostawiamy dla kompatybilności.
    """
    # Zwracamy mapę wiedzy zamiast surowej listy, bo jest bardziej wartościowa
    return get_project_knowledge_base()

coder_tools = [write_code_file, read_project_spec, list_project_files]