# devteam_runner.py
from coder_agent import run_coder_agent, run_verifier_agent
from tools import write_code_file, list_project_files, read_project_spec

def parse_plan_to_steps(plan_content: str) -> list[str]:
    steps = []
    for line in plan_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 5:
            cleaned_line = line.lstrip('0123456789.-*• ')
            steps.append(cleaned_line)
    return steps

def run_devteam_pipeline(initial_task: str) -> str:
    print(f"🚀 [DevTeam] Start Szybki: {initial_task}")
    
    # --- FAZA 1: PRECYZYJNE PLANOWANIE ---
    print("🤖 [1/3] Planowanie struktury...")
    
    # Kluczowa zmiana: Wymuszamy na Szefie podawanie nazw plików w planie
    plan_prompt = (
        f"Jesteś Tech Leadem. Stwórz plan dla zadania: '{initial_task}'.\n"
        "WYMAGANIA KRYTYCZNE:\n"
        "1. W każdym kroku MUSISZ podać nazwę pliku, na którym programista ma pracować.\n"
        "2. Przykład dobrego kroku: 'Stwórz logikę kalkulatora w pliku calc.py'.\n"
        "3. Przykład złego kroku: 'Napisz logikę'.\n"
        "4. Ogranicz się do 3-5 kroków.\n"
        "5. Nie używaj wstępów, tylko lista kroków."
    )
    
    # Szybki strzał do modelu (max 15 kroków)
    agent_result = run_coder_agent(plan_prompt, max_steps=15)
    plan_text = agent_result.get('output', '')
    
    # Zapisujemy plan dla porządku
    try:
        write_code_file.invoke({"filepath": "PLAN_PROJEKTU.md", "content": plan_text})
    except: pass

    steps = parse_plan_to_steps(plan_text)
    if not steps:
        print("⚠️ Fallback: Brak planu, wykonuję zadanie w całości.")
        steps = [f"Wykonaj pełne zadanie: {initial_task} w pliku main.py"]

    print(f"📋 [Plan] {len(steps)} kroków.")

    # --- FAZA 2: SZYBKA REALIZACJA ---
    print("🤖 [2/3] Kodowanie...")
    execution_log = ""
    
    for i, step in enumerate(steps, 1):
        # Szybkie sprawdzenie struktury (bez zbędnych folderów dzięki tools.py)
        try:
            structure = list_project_files.invoke({})
        except:
            structure = "..."
            
        print(f"\n👉 Krok {i}: {step}")
        
        # 1. Weryfikator (Deduplikacja)
        # Sprawdza, czy krok nie każe tworzyć duplikatu (np. main.py vs app.py)
        safe_task = run_verifier_agent(step, structure)
        
        # 2. Coder (Wykonanie)
        # Dajemy mu kontekst struktury, żeby wiedział co ma importować
        full_task = (
            f"ZADANIE: {safe_task}\n"
            f"KONTEKST PROJEKTU (Istniejące pliki):\n{structure}\n"
            "WYMAGANIE: Jeśli plik istnieje, edytuj go. Nie twórz nowych plików o podobnych nazwach."
        )
        
        # Uruchamiamy raz, porządnie. Bez pętli poprawkowej (dla szybkości).
        res = run_coder_agent(full_task, max_steps=50)
        out = res.get('output', 'Zrobione.')
        
        execution_log += f"#### Krok {i}: {step}\n{out}\n\n"

    # --- FAZA 3: RAPORT ---
    try:
        final_files = list_project_files.invoke({})
    except:
        final_files = "Błąd."

    return f"""
    # 🚀 Raport DevTeam
    ## Zadanie: {initial_task}
    
    ## 📂 Wynikowa Struktura Plików
    ```text
    {final_files}
    ```
    ## 📝 Szczegóły Realizacji
    {execution_log}
    """