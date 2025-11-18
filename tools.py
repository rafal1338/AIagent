import os
from langchain.tools import tool

# Ustawia folder wyjściowy na 'program'
PROJECT_DIR = "program"
# Tworzy folder 'program', jeśli nie istnieje
os.makedirs(PROJECT_DIR, exist_ok=True)

@tool
def write_code_file(filename: str, content: str) -> str:
    """
    Zapisuje podany kod do pliku w katalogu projektu ('program').
    Używaj tylko, gdy jesteś gotowy zapisać kompletny fragment kodu.
    """
    path = os.path.join(PROJECT_DIR, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Sukces! Plik '{filename}' został zapisany w ścieżce: {path}"
    except Exception as e:
        return f"Błąd podczas zapisu pliku '{filename}': {e}"

@tool
def read_project_spec(filename: str) -> str:
    """
    Czyta zawartość pliku specyfikacji lub innego artefaktu
    z katalogu projektu ('program').
    """
    path = os.path.join(PROJECT_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"Zawartość pliku '{filename}':\n---\n{content}\n---"
    except FileNotFoundError:
        return f"Błąd: Plik '{filename}' nie został znaleziony w katalogu projektu."
    except Exception as e:
        return f"Błąd odczytu pliku '{filename}': {e}"

# Lista narzędzi dostępnych dla Agenta
coder_tools = [write_code_file, read_project_spec]