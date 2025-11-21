# devteam_runner.py
from coder_agent import run_coder_agent, run_verifier_agent
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
    system_log(f"🎬 START (Tryb Jakości): {initial_task}")
    
    # --- 1. ANALIZA STANU ISTNIEJĄCEGO ---
    knowledge = get_project_knowledge_base()
    system_log("🔍 Analiza mapy projektu...")
    
    # --- 2. PLANOWANIE ---
    plan_prompt = (
        f"Jesteś Tech Leadem. Zadanie: '{initial_task}'.\n\n"
        f"OBECNA MAPA PROJEKTU:\n{knowledge}\n\n"
        "WYTYCZNE:\n"
        "1. Jeśli projekt jest pusty, zaplanuj strukturę od zera.\n"
        "2. Jeśli pliki istnieją, zaplanuj ich EDYCJĘ.\n"
        "3. Stwórz 3-5 kroków. W każdym kroku wskaż KONKRETNY PLIK.\n"
        "4. Nie twórz duplikatów funkcjonalności.\n"
    )
    
    agent_result = run_coder_agent(plan_prompt, max_steps=15)
    plan_text = agent_result.get('output', '')
    
    try: write_code_file.invoke({"filepath": "PLAN_PROJEKTU.md", "content": plan_text, "description": "Plan działania"})
    except: pass

    steps = parse_plan_to_steps(plan_text)
    if not steps: steps = [f"Zrealizuj: {initial_task}"]

    system_log(f"📋 Plan działania: {len(steps)} kroków.")

    # --- 3. REALIZACJA ---
    execution_log = ""
    
    for i, step in enumerate(steps, 1):
        # Zawsze pobieramy najświeższą wiedzę o projekcie
        current_knowledge = get_project_knowledge_base()
            
        system_log(f"👉 Krok {i}: {step}")
        
        # Weryfikacja (czy krok ma sens w świetle mapy?)
        verified_task = run_verifier_agent(step, current_knowledge)
        
        if verified_task != step:
            system_log(f"💡 Korekta: {verified_task[:50]}...")
        
        # Zadanie dla Codera
        full_task = (
            f"ZADANIE PRIORYTETOWE: {verified_task}\n\n"
            f"{current_knowledge}\n"
            "WYMAGANIA:\n"
            "- Pisz kod najwyższej jakości.\n"
            "- Kod musi być kompletny.\n"
            "- Użyj 'write_code_file' z poprawnym opisem 'description'."
        )
        
        res = run_coder_agent(full_task, max_steps=50)
        out = res.get('output', 'Zrobione.')
        
        execution_log += f"#### Krok {i}\n**Zadanie:** {verified_task}\n\n{out}\n\n"

    # --- 4. RAPORT ---
    final_map = get_project_knowledge_base()

    return f"""
    # 🚀 Raport DevTeam
    ## Zadanie: {initial_task}
    
    ## 🗺️ Stan Projektu (Mapa)
    ```text
    {final_map}
    ```
    ## 📝 Szczegóły
    {execution_log}
    """