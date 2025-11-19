# devteam_runner.py
from coder_agent import run_coder_agent
# Importujemy narzędzie do listowania plików
from tools import write_code_file, list_project_files

def run_devteam_pipeline(initial_task: str) -> str:
    """
    Orkiestrator tworzenia całych projektów wieloplikowych.
    """
    
    # --- KROK 1: Specyfikacja Projektu ---
    print("🤖 [DevTeam] Analiza wymagań projektu...")
    
    spec_content = f"""
    # Specyfikacja Projektu
    Zadanie Użytkownika: {initial_task}
    
    Wytyczne:
    1. Dobierz odpowiedni język i technologie do zadania.
    2. Zaplanuj strukturę folderów (np. src/, tests/, assets/).
    3. Utwórz WSZYSTKIE niezbędne pliki.
    """
    
    # Zapis specyfikacji
    write_code_file.invoke({
        "filepath": "SPECYFIKACJA_PROJEKTU.md", 
        "content": spec_content
    })
    
    # --- KROK 2: Generowanie Projektu ---
    print("🤖 [DevTeam] Budowanie struktury projektu...")
    
    coder_task = (
        "Zapoznaj się z 'SPECYFIKACJA_PROJEKTU.md'. "
        "Następnie stwórz kompletny projekt. "
        "Utwórz odpowiednie foldery i pliki z kodem źródłowym. "
        "Pamiętaj o plikach konfiguracyjnych (np. package.json, requirements.txt)."
    )
    
    coder_result = run_coder_agent(coder_task)
    
    # --- KROK 3: Raport Końcowy ---
    print("🤖 [DevTeam] Generowanie podsumowania...")
    
    # Pobieramy strukturę plików, żeby pokazać użytkownikowi co powstało
    try:
        project_structure = list_project_files.invoke({})
    except Exception as e:
        project_structure = f"Błąd pobierania struktury: {e}"

    final_report = f"""
    # 🚀 Raport DevTeam: Nowy Projekt
    
    ## 🎯 Zadanie
    {initial_task}
    
    ## 📂 Struktura Utworzonego Projektu
    Poniżej znajduje się lista plików i folderów utworzonych w katalogu `program/`:
    
    ```text
    {project_structure}
    ```
    
    ## 💬 Komentarz Agenta
    {coder_result.get('output', 'Zadanie zakończone.')}
    
    ---
    *Pliki znajdują się w folderze 'program' w katalogu aplikacji.*
    """
    
    return final_report