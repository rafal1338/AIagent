# devteam_runner.py
from coder_agent import run_coder_agent
from tools import write_code_file, read_project_spec, list_project_files

def parse_plan_to_steps(plan_content: str) -> list[str]:
    """
    Parsuje plik planu na listę konkretnych kroków.
    """
    steps = []
    for line in plan_content.split('\n'):
        line = line.strip()
        # Filtrujemy nagłówki, puste linie i dziwne znaki
        if line and not line.startswith('#') and len(line) > 5:
            # Usuwamy punktory (1., -, *)
            cleaned_line = line.lstrip('0123456789.-*• ')
            steps.append(cleaned_line)
    return steps

def run_devteam_pipeline(initial_task: str) -> str:
    print(f"🚀 [DevTeam] Start projektu: {initial_task}")
    
    # --- FAZA 1: PLANOWANIE ---
    print("🤖 [1/3] Planowanie architektury...")
    
    plan_prompt = (
        f"Jesteś Tech Leadem. Stwórz plan implementacji dla zadania: '{initial_task}'.\n"
        "WYMAGANIA:\n"
        "1. Zapisz plik 'PLAN_PROJEKTU.md'.\n"
        "2. Wypisz od 3 do 6 kroków.\n"
        "3. KROK 1 to ZAWSZE: 'Inicjalizacja struktury folderów i plików konfiguracyjnych'.\n"
        "4. Ostatni krok to: 'Weryfikacja i uruchomienie'.\n"
        "5. Unikaj duplikatów w planie."
    )
    
    # Agent tworzy plan
    agent_result = run_coder_agent(plan_prompt, max_steps=25)
    
    # --- FAZA 2: ODCZYT I NAPRAWA PLANU ---
    try:
        plan_content = read_project_spec.invoke({"filepath": "PLAN_PROJEKTU.md"})
        
        # Awaryjne odzyskiwanie planu z tekstu, jeśli plik nie powstał
        if "❌" in plan_content or not plan_content.strip():
            print("⚠️ [Plan Fix] Odzyskiwanie planu z wypowiedzi agenta...")
            plan_content = agent_result.get('output', '')
            if len(plan_content) < 10:
                plan_content = "1. Stwórz kompletną aplikację w jednym podejściu."
            write_code_file.invoke({"filepath": "PLAN_PROJEKTU.md", "content": plan_content})

        steps = parse_plan_to_steps(plan_content)
        print(f"📋 [Plan] Zatwierdzono {len(steps)} kroków.")
        
    except Exception as e:
        print(f"⚠️ Błąd planowania: {e}. Tryb awaryjny.")
        steps = [f"Zrealizuj całe zadanie: {initial_task}"]

    # --- FAZA 3: INTELIGENTNA EGZEKUCJA ---
    print("🤖 [2/3] Realizacja kroków...")
    execution_log = ""
    
    for i, step in enumerate(steps, 1):
        # ! KLUCZOWE ! : Sprawdzamy co już mamy przed każdym krokiem
        try:
            current_structure = list_project_files.invoke({})
        except:
            current_structure = "(pusty folder)"
            
        print(f"\n   👉 Krok {i}/{len(steps)}: {step}")
        
        step_task = (
            f"TWOJE ZADANIE: Wykonaj krok {i} z planu: '{step}'.\n"
            f"KONTEKST PROJEKTU: {initial_task}\n\n"
            f"📂 OBECNA STRUKTURA PLIKÓW (Nie twórz duplikatów!):\n"
            f"{current_structure}\n\n"
            "ZASADY:\n"
            "1. Jeśli plik już istnieje (np. main.py), EDYTUJ GO, nie twórz 'main_v2.py'.\n"
            "2. Jeśli brakuje kodu z poprzednich kroków, uzupełnij go.\n"
            "3. ZAWSZE używaj 'write_code_file' do zapisu pracy."
        )
        
        result = run_coder_agent(step_task, max_steps=60) # Zwiększony limit dla trudnych kroków
        output = result.get('output', 'Zrobione.')
        execution_log += f"### Krok {i}\n{output}\n\n"

    # --- FAZA 4: FINALNY RAPORT ---
    print("\n🤖 [3/3] Generowanie raportu...")
    try:
        final_structure = list_project_files.invoke({})
    except:
        final_structure = "Błąd odczytu."

    return f"""
    # 🚀 Raport Wykonania
    
    ## 🎯 Zadanie
    {initial_task}
    
    ## 📂 Finalna Struktura
    ```text
    {final_structure}
    ```
    
    ## 📝 Przebieg Prac
    {execution_log}
    """