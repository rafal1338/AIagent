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
    1. Język: Python / Odpowiedni dla zadania (Angular/.NET w zależności od opisu)
    2. Główny plik wynikowy: 'main_app.py' (lub odpowiedni plik startowy)
    3. Kod musi być kompletny.
    """
    
    # NAPRAWA: Używamy .invoke() zamiast bezpośredniego wywołania funkcji
    # Ponieważ write_code_file jest obiektem @tool, wymaga słownika argumentów.
    write_result = write_code_file.invoke({
        "filename": "specyfikacja.md", 
        "content": spec_content
    })
    print(f"   -> Specyfikacja zapisana: {write_result}")
    
    # --- KROK 2: Coder (LangGraph Agent) ---
    print("🤖 [DevTeam 2/3] Przekazywanie zadania do Programisty...")
    
    coder_task = (
        "Przeczytaj plik 'specyfikacja.md'. "
        "Następnie napisz wymagany kod aplikacji i zapisz go jako 'main_app.py' (lub inny główny plik). "
        "Upewnij się, że kod jest poprawny."
    )
    
    # Uruchamiamy agenta (tutaj jest OK, bo agent sam wie jak używać narzędzi)
    coder_result = run_coder_agent(coder_task)
    
    # --- KROK 3: Raportowanie ---
    print("🤖 [DevTeam 3/3] Generowanie raportu końcowego...")
    
    # Próbujemy odczytać wygenerowany plik
    try:
        # NAPRAWA: Tutaj również używamy .invoke() dla narzędzia odczytu
        generated_code = read_project_spec.invoke({"filename": "main_app.py"})
    except Exception:
        generated_code = "⚠️ BŁĄD: Nie znaleziono pliku 'main_app.py'. Agent mógł użyć innej nazwy lub wystąpił błąd."

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