# devteam_runner.py
from coder_agent import run_coder_agent, run_verifier_agent
# Importujemy nową funkcję wiedzy
from tools import write_code_file, list_project_files, read_project_spec, system_log, get_project_knowledge_base

def parse_plan_to_steps(plan_content: str) -> list[str]:
    steps = []
    for line in plan_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 5:
            cleaned_line = line.lstrip('0123456789.-*• ')
            steps.append(cleaned_line)
    return steps

def run_devteam_pipeline(initial_task: str) -> str:
    system_log(f"🎬 START: {initial_task}")
    
    # --- 1. PLANOWANIE ---
    system_log("🤖 [1/3] Generowanie planu...")
    
    # Pobieramy mapę, żeby planista wiedział co już jest (przy kontynuacji pracy)
    existing_knowledge = get_project_knowledge_base()
    
    plan_prompt = (
        f"Jesteś Tech Leadem. Zadanie: '{initial_task}'.\n"
        f"OBECNY STAN PROJEKTU:\n{existing_knowledge}\n"
        "WYMAGANIA:\n"
        "1. Stwórz 3-5 konkretnych kroków.\n"
        "2. W każdym kroku podaj nazwę pliku.\n"
        "3. Jeśli plik już istnieje w mapie, użyj go.\n"
        "4. Podaj tylko listę kroków."
    )
    
    agent_result = run_coder_agent(plan_prompt, max_steps=15)
    plan_text = agent_result.get('output', '')
    
    # Zapis planu (opcjonalne)
    try: write_code_file.invoke({"filepath": "PLAN_PROJEKTU.md", "content": plan_text, "description": "Aktualny plan prac"})
    except: pass

    steps = parse_plan_to_steps(plan_text)
    if not steps:
        steps = [f"Zrealizuj: {initial_task}"]

    system_log(f"📋 Plan: {len(steps)} kroków.")

    # --- 2. REALIZACJA ---
    system_log("🤖 [2/3] Kodowanie z Mapą Wiedzy...")
    execution_log = ""
    
    for i, step in enumerate(steps, 1):
        # Pobieramy aktualną mapę wiedzy (z opisami plików!)
        knowledge = get_project_knowledge_base()
            
        system_log(f"👉 Krok {i}: {step}")
        
        # Weryfikacja z użyciem mapy
        safe_task = run_verifier_agent(step, knowledge)
        
        # Zadanie dla Codera
        full_task = (
            f"ZADANIE: {safe_task}\n"
            f"{knowledge}\n" # Wklejamy mapę
            "ZASADA: Nie duplikuj funkcjonalności. Jeśli plik ma opis pasujący do zadania, edytuj go. Pamiętaj o dodaniu opisu 'description' przy zapisie."
        )
        
        res = run_coder_agent(full_task, max_steps=50)
        out = res.get('output', 'Zrobione.')
        
        execution_log += f"#### Krok {i}: {step}\n{out}\n\n"

    # --- 3. RAPORT ---
    system_log("🏁 [3/3] Raport...")
    try:
        # Raportujemy na podstawie inteligentnej mapy
        final_structure = get_project_knowledge_base()
    except:
        final_structure = "Błąd odczytu mapy."

    return f"""
    # 🚀 Raport DevTeam
    ## Zadanie: {initial_task}
    
    ## 🗺️ Mapa Projektu
    ```text
    {final_structure}
    ```
    ## 📝 Szczegóły
    {execution_log}
    """