# devteam_runner.py
from coder_agent import run_coder_agent
# Importujemy narzędzia do sprawdzania plików
from tools import write_code_file, list_project_files, read_project_spec

def run_devteam_pipeline(initial_task: str) -> str:
    """
    Orkiestrator z pętlą weryfikacji (Self-Correction Loop).
    """
    
    # --- KROK 1: Specyfikacja ---
    print("🤖 [DevTeam] Analiza wymagań...")
    spec_content = f"""
    # Specyfikacja
    Zadanie: {initial_task}
    Cel: Stworzyć działający kod.
    Wymagane: Kompletna struktura plików.
    """
    write_code_file.invoke({"filepath": "SPECYFIKACJA.md", "content": spec_content})
    
    # --- KROK 2: Pętla Realizacji (Max 3 próby) ---
    max_attempts = 3
    attempt = 1
    success = False
    coder_output = ""
    
    # Definiujemy główny cel (zakładamy, że agent powinien stworzyć cokolwiek w folderze)
    current_task = (
        f"Zrealizuj zadanie: {initial_task}. "
        "Stwórz wszystkie niezbędne pliki w folderze 'program'. "
        "Upewnij się, że kod jest kompletny."
    )

    while attempt <= max_attempts:
        print(f"🤖 [DevTeam] Próba {attempt}/{max_attempts}...")
        
        # Uruchamiamy agenta (z dużym limitem kroków)
        result_dict = run_coder_agent(current_task, max_steps=100)
        coder_output = result_dict.get('output', '')
        
        # --- KROK 3: Weryfikacja ---
        print("🤖 [DevTeam] Weryfikacja efektów pracy...")
        
        # Sprawdzamy strukturę plików
        files_list = list_project_files.invoke({})
        
        # Prosta heurystyka: Czy powstały jakieś pliki poza specyfikacją?
        # (Możesz to rozbudować o sprawdzanie konkretnego pliku np. main.py)
        if "📄" in files_list and ("main" in files_list or "app" in files_list or "index" in files_list):
            print("✅ [DevTeam] Wygląda na to, że projekt został utworzony.")
            success = True
            break
        else:
            print("⚠️ [DevTeam] Nie znaleziono głównych plików kodu. Zlecam poprawkę.")
            current_task = (
                f"Poprzednia próba nie powiodła się lub brakuje kluczowych plików. "
                f"Obecna struktura to:\n{files_list}\n"
                f"Twoim zadaniem jest STWORZYĆ brakujące pliki kodu dla zadania: {initial_task}."
            )
            attempt += 1

    # --- KROK 4: Raport ---
    status_icon = "✅" if success else "⚠️"
    
    final_report = f"""
    # {status_icon} Raport DevTeam (Po {attempt} iteracjach)
    
    ## 🎯 Zadanie
    {initial_task}
    
    ## 📂 Struktura Projektu
    ```text
    {files_list}
    ```
    
    ## 💬 Ostatni Komentarz Agenta
    {coder_output}
    
    ---
    *System wykonał {attempt} pętle(i) weryfikacji.*
    """
    
    return final_report