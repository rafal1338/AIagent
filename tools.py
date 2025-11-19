import os
from langchain_core.tools import tool

# Folder główny projektu
PROJECT_DIR = "program"
os.makedirs(PROJECT_DIR, exist_ok=True)

@tool
def write_code_file(filepath: str, content: str) -> str:
    """
    Zapisuje kod do pliku. Automatycznie tworzy foldery, jeśli podano ścieżkę.
    Args:
        filepath: ścieżka do pliku (np. 'src/utils/helper.py' lub 'README.md')
        content: pełna treść pliku
    """
    # Łączymy folder główny ze ścieżką podaną przez agenta
    full_path = os.path.join(PROJECT_DIR, filepath)
    
    # Pobieramy folder z pełnej ścieżki (np. 'program/src/utils')
    directory = os.path.dirname(full_path)
    
    try:
        # Jeśli folder nie istnieje, tworzymy go (wraz z nadrzędnymi)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Zapisano plik: {filepath}"
    except Exception as e:
        return f"❌ Błąd zapisu pliku {filepath}: {e}"

@tool
def read_project_spec(filepath: str) -> str:
    """
    Odczytuje zawartość pliku z projektu.
    Args:
        filepath: ścieżka do pliku (np. 'src/main.rs')
    """
    full_path = os.path.join(PROJECT_DIR, filepath)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"❌ Nie znaleziono pliku: {filepath}"
    except Exception as e:
        return f"❌ Błąd odczytu: {e}"

@tool
def list_project_files() -> str:
    """
    Zwraca listę wszystkich plików i folderów w obecnym projekcie.
    Używaj tego, aby zobaczyć strukturę stworzonego projektu.
    """
    file_structure = ""
    try:
        for root, dirs, files in os.walk(PROJECT_DIR):
            # Obliczamy poziom zagłębienia dla ładnego wyświetlania
            level = root.replace(PROJECT_DIR, '').count(os.sep)
            indent = ' ' * 4 * (level)
            folder_name = os.path.basename(root)
            if folder_name:
                file_structure += f"{indent}📁 {folder_name}/\n"
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                file_structure += f"{subindent}📄 {f}\n"
                
        if not file_structure:
            return "Folder projektu jest pusty."
        return file_structure
    except Exception as e:
        return f"❌ Błąd listowania plików: {e}"

# Eksportujemy listę narzędzi (teraz z list_project_files)
coder_tools = [write_code_file, read_project_spec, list_project_files]