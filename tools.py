# tools.py
import os
import queue
import time
from langchain_core.tools import tool

PROJECT_DIR = "program"
os.makedirs(PROJECT_DIR, exist_ok=True)

# --- SYSTEM LOGOWANIA REAL-TIME ---
# Globalna kolejka do przesyłania logów z wątku agenta do przeglądarki
msg_queue = queue.Queue()

def system_log(message: str):
    """Wysyła wiadomość do frontendu (Sidebar Console)"""
    # Wypisz w konsoli serwera (dla debugowania)
    print(f"[SERVER LOG] {message}")
    # Dodaj do kolejki dla przeglądarki
    msg_queue.put(message)

# Foldery ignorowane
IGNORE_DIRS = {
    '__pycache__', 'node_modules', 'venv', '.git', '.vscode', 
    'bin', 'obj', 'Debug', 'Release', '.idea'
}

@tool
def write_code_file(filepath: str, content: str) -> str:
    """Zapisuje kod do pliku."""
    full_path = os.path.join(PROJECT_DIR, filepath)
    directory = os.path.dirname(full_path)
    
    try:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        system_log(f"💾 Zapisano plik: {filepath}") # Logujemy akcję
        return f"✅ Zapisano: {filepath}"
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
    """Zwraca strukturę plików."""
    structure = []
    try:
        for root, dirs, files in os.walk(PROJECT_DIR):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            level = root.replace(PROJECT_DIR, '').count(os.sep)
            indent = '  ' * level
            folder = os.path.basename(root)
            if folder: structure.append(f"{indent}📁 {folder}/")
            subindent = '  ' * (level + 1)
            for f in files:
                if not f.endswith(('.pyc', '.exe', '.dll')):
                    structure.append(f"{subindent}📄 {f}")
                    
        if not structure: return "(pusty projekt)"
        return "\n".join(structure)
    except Exception as e:
        return f"❌ Błąd struktury: {e}"

coder_tools = [write_code_file, read_project_spec, list_project_files]