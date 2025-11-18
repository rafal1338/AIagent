from coder_agent import run_coder_agent
from tools import write_code_file, read_project_spec

def run_devteam_pipeline(initial_task: str) -> str:
    """
    Główna funkcja orkiestrująca proces: PM -> Coder -> Raport.
    """
    
    # --- KROK 1: PM (Project Manager) ---
    print("🤖 [DevTeam 1/3] Project Manager analizuje wymagania...")
    
    # Tworzymy specyfikację dla Agenta
    spec_content = f"""
    # Specyfikacja Projektu
    Zadanie: {initial_task}
    
    Wymagania Techniczne:
    1. Język: Python
    2. Główny plik wynikowy: 'main_app.py'
    3. Kod musi być kompletny i gotowy do uruchomienia.
    """
    
    # Zapisujemy specyfikację na dysku
    write_code_file("specyfikacja.md", spec_content)
    
    # --- KROK 2: Coder (LangGraph Agent) ---
    print("🤖 [DevTeam 2/3] Przekazywanie zadania do Programisty...")
    
    coder_task = (
        "Przeczytaj plik 'specyfikacja.md'. "
        "Następnie napisz wymagany kod Python i zapisz go jako 'main_app.py'. "
        "Upewnij się, że kod jest poprawny."
    )
    
    # Uruchamiamy agenta
    coder_result = run_coder_agent(coder_task)
    
    # --- KROK 3: Raportowanie ---
    print("🤖 [DevTeam 3/3] Generowanie raportu końcowego...")
    
    # Próbujemy odczytać wygenerowany plik
    try:
        generated_code = read_project_spec("main_app.py")
    except Exception:
        generated_code = "⚠️ BŁĄD: Nie znaleziono pliku 'main_app.py'."

    final_report = f"""
    # 🚀 Raport AI DevTeam
    
    ## 🎯 Zadanie
    {initial_task}
    
    ## 🤖 Komentarz Agenta
    {coder_result.get('output', 'Brak odpowiedzi słownej.')}
    
    ## 📄 Wygenerowany Kod (main_app.py)
    ```python
    {generated_code}
    ```
    """
    
    return final_report