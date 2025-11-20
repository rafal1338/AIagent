# devteam_runner.py
from coder_agent import run_coder_agent, run_verifier_agent
from tools import write_code_file, list_project_files, read_project_spec, system_log

def parse_plan_to_steps(plan_content: str) -> list[str]:
    steps = []
    for line in plan_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 5:
            cleaned_line = line.lstrip('0123456789.-*• ')
            steps.append(cleaned_line)
    return steps

def run_devteam_pipeline(initial_task: str) -> str:
    system_log(f"🎬 START PROJEKTU: {initial_task}")
    
    # --- FAZA 1: PLANOWANIE ---
    system_log("🤖 [1/3] Planowanie struktury...")
    
    plan_prompt = (
        f"Jesteś Tech Leadem. Stwórz plan dla zadania: '{initial_task}'.\n"
        "WYMAGANIA: Podaj 3-5 kroków. W każdym kroku podaj NAZWĘ PLIKU do edycji/utworzenia.\n"
        "Bez wstępów."
    )
    
    agent_result = run_coder_agent(plan_prompt, max_steps=15)
    plan_text = agent_result.get('output', '')
    
    try:
        write_code_file.invoke({"filepath": "PLAN_PROJEKTU.md", "content": plan_text})
    except: pass

    steps = parse_plan_to_steps(plan_text)
    if not steps:
        system_log("⚠️ Brak jasnego planu, przechodzę do trybu bezpośredniego.")
        steps = [f"Wykonaj zadanie: {initial_task} w pliku main.py"]

    system_log(f"📋 Zatwierdzono {len(steps)} kroków realizacyjnych.")

    # --- FAZA 2: REALIZACJA ---
    system_log("🤖 [2/3] Rozpoczynam kodowanie...")
    execution_log = ""
    
    for i, step in enumerate(steps, 1):
        try:
            structure = list_project_files.invoke({})
        except:
            structure = "..."
            
        system_log(f"👉 Krok {i}/{len(steps)}: {step}")
        
        # Weryfikacja
        safe_task = run_verifier_agent(step, structure)
        
        # Wykonanie
        full_task = (
            f"ZADANIE: {safe_task}\n"
            f"KONTEKST (PLIKI): {structure}\n"
            "Zasada: Edytuj istniejące, nie duplikuj."
        )
        
        res = run_coder_agent(full_task, max_steps=50)
        out = res.get('output', 'Zrobione.')
        
        execution_log += f"#### Krok {i}: {step}\n{out}\n\n"

    # --- FAZA 3: RAPORT ---
    system_log("🏁 [3/3] Generowanie raportu końcowego...")
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