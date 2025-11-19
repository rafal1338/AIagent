# devteam_runner.py
from coder_agent import run_coder_agent
from tools import write_code_file, read_project_spec, list_project_files

def parse_plan_to_steps(plan_content: str) -> list[str]:
    """
    Pomocnicza funkcja, która wyciąga konkretne kroki z pliku tekstowego.
    """
    steps = []
    for line in plan_content.split('\n'):
        line = line.strip()
        # Filtrujemy puste linie, nagłówki markdown i "rozmówki" agenta
        if line and not line.startswith('#') and len(line) > 5:
            # Usuwamy numerację (np. "1. Stwórz..." -> "Stwórz...")
            cleaned_line = line.lstrip('0123456789.-*• ')
            steps.append(cleaned_line)
    return steps

def run_devteam_pipeline(initial_task: str) -> str:
    """
    Orkiestrator z podziałem zadań i zabezpieczeniem przed leniwym agentem.
    """
    
    print(f"🚀 [DevTeam] Rozpoczynam projekt: {initial_task}")
    
    # --- FAZA 1: ANALIZA I PLANOWANIE ---
    print("🤖 [Faza 1/3] Tworzenie planu implementacji...")
    
    plan_prompt = (
        f"Jesteś Tech Leadem. Twoim zadaniem jest rozpisanie planu dla programisty dla zadania: '{initial_task}'.\n"
        "1. UŻYJ narzędzia 'write_code_file', aby zapisać plik 'PLAN_PROJEKTU.md'.\n"
        "2. W tym pliku wypisz od 3 do 6 konkretnych kroków implementacji.\n"
        "3. Każdy krok w nowej linii.\n"
        "4. Pierwszym krokiem MUSI BYĆ: 'Stwórz strukturę plików i podstawową konfigurację'."
    )
    
    # Pobieramy wynik, żeby mieć dostęp do tekstu odpowiedzi w razie błędu
    agent_result = run_coder_agent(plan_prompt, max_steps=20)
    
    # --- FAZA 2: ODCZYT PLANU (Z NAPRAWĄ) ---
    try:
        # Próba 1: Odczyt z pliku (Idealny scenariusz)
        plan_content = read_project_spec.invoke({"filepath": "PLAN_PROJEKTU.md"})
        
        # Jeśli plik nie istnieje (Agent tylko "powiedział" plan, ale nie zapisał)
        if "❌" in plan_content or not plan_content.strip():
            print("⚠️ [Autokorekta] Agent nie utworzył pliku, ale mógł podać plan w tekście. Próbuję odzyskać...")
            
            agent_text_output = agent_result.get('output', '')
            if len(agent_text_output) > 10:
                # Używamy odpowiedzi agenta jako treści planu
                plan_content = agent_text_output
                # Zapisujemy go ręcznie dla porządku
                write_code_file.invoke({"filepath": "PLAN_PROJEKTU.md", "content": plan_content})
                print("✅ [Autokorekta] Plan odzyskany z rozmowy i zapisany.")
            else:
                raise Exception("Brak pliku i brak sensownej odpowiedzi od Agenta.")

        steps = parse_plan_to_steps(plan_content)
        
        if not steps:
             print("⚠️ Pusty plan. Dodaję domyślny krok.")
             steps = ["Stwórz strukturę projektu i główny kod aplikacji"]
             
        print(f"📋 [Plan] Zatwierdzono {len(steps)} kroków.")
        
    except Exception as e:
        print(f"⚠️ Błąd krytyczny planowania: {e}. Przechodzę do trybu awaryjnego.")
        steps = [initial_task]

    # --- FAZA 3: EGZEKUCJA KROK PO KROKU ---
    print("🤖 [Faza 2/3] Wykonywanie...", end="", flush=True)
    
    execution_log = ""
    
    for i, step in enumerate(steps, 1):
        print(f"\n   👉 Krok {i}: {step}")
        
        step_task = (
            f"ZREALIZUJ KROK {i}: '{step}'.\n"
            f"Kontekst projektu: {initial_task}\n"
            "WYMAGANIA:\n"
            "- Używaj 'write_code_file' do tworzenia/edycji plików.\n"
            "- Jeśli kod jest długi, podziel go na mniejsze pliki.\n"
            "- ZAWSZE zapisuj efekt pracy na dysku."
        )
        
        result = run_coder_agent(step_task, max_steps=50)
        output = result.get('output', 'Zadanie wykonane.')
        execution_log += f"### Krok {i}: {step}\n{output}\n\n"

    # --- FAZA 4: RAPORT ---
    print("\n🤖 [Faza 3/3] Raportowanie...")
    
    try:
        project_structure = list_project_files.invoke({})
    except Exception:
        project_structure = "Błąd listowania plików."

    final_report = f"""
    # 🚀 Raport DevTeam
    
    ## 🎯 Zadanie
    {initial_task}
    
    ## 📋 Wykonane Kroki
    {chr(10).join([f"- {s}" for s in steps])}
    
    ## 📂 Pliki w projekcie
    ```text
    {project_structure}
    ```
    
    ## 📝 Szczegóły
    {execution_log}
    """
    
    return final_report