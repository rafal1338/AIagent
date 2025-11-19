# devteam_runner.py
# Importujemy dodatkowo run_verifier_agent
from coder_agent import run_coder_agent, run_verifier_agent
from tools import write_code_file, read_project_spec, list_project_files

def parse_plan_to_steps(plan_content: str) -> list[str]:
    steps = []
    for line in plan_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 5:
            cleaned_line = line.lstrip('0123456789.-*• ')
            steps.append(cleaned_line)
    return steps

def run_devteam_pipeline(initial_task: str) -> str:
    print(f"🚀 [DevTeam] Start: {initial_task}")
    
    # --- FAZA 1: PLANOWANIE ---
    print("🤖 [1/3] Planowanie...")
    
    plan_prompt = (
        f"Jesteś Tech Leadem. Zaplanuj zadanie: '{initial_task}'.\n"
        "1. Zapisz 'PLAN_PROJEKTU.md'.\n"
        "2. Wypisz 3-6 kroków.\n"
        "3. Pierwszy krok: 'Inicjalizacja struktury'.\n"
        "4. Kolejne kroki: Implementacja kolejnych modułów.\n"
        "5. Ostatni krok: Integracja i weryfikacja."
    )
    
    agent_result = run_coder_agent(plan_prompt, max_steps=20)
    
    # --- FAZA 2: ODCZYT PLANU ---
    try:
        plan_content = read_project_spec.invoke({"filepath": "PLAN_PROJEKTU.md"})
        if "❌" in plan_content or not plan_content.strip():
            # Fallback jeśli plik nie powstał
            plan_content = agent_result.get('output', '')
            write_code_file.invoke({"filepath": "PLAN_PROJEKTU.md", "content": plan_content})

        steps = parse_plan_to_steps(plan_content)
        if not steps: steps = [initial_task]
        print(f"📋 [Plan] Kroki: {len(steps)}")
        
    except Exception:
        steps = [initial_task]

    # --- FAZA 3: INTELIGENTNA EGZEKUCJA ---
    print("🤖 [2/3] Realizacja...")
    execution_log = ""
    
    for i, step in enumerate(steps, 1):
        # 1. Pobieramy aktualny stan projektu
        try:
            current_structure = list_project_files.invoke({})
        except:
            current_structure = "(pusty folder)"
            
        print(f"\n👉 Krok {i}/{len(steps)} (Oryginał): {step}")
        
        # 2. WERYFIKACJA: Czy ten krok ma sens w kontekście istniejących plików?
        # To tutaj zapobiegamy duplikatom "backend" vs "backend_v2"
        verified_step = run_verifier_agent(step, current_structure)
        
        # 3. EGZEKUCJA: Coder dostaje już poprawione, bezpieczne zadanie
        step_task = (
            f"WYKONAJ ZADANIE: {verified_step}\n"
            f"KONTEKST CAŁEGO PROJEKTU: {initial_task}\n"
            f"OBECNE PLIKI:\n{current_structure}\n\n"
            "Pamiętaj: Edytuj istniejące pliki, nie twórz duplikatów."
        )
        
        result = run_coder_agent(step_task, max_steps=60)
        output = result.get('output', 'Zrobione.')
        
        execution_log += f"### Krok {i}: {step}\n*Status weryfikacji:* Zadanie zoptymalizowane.\n\n{output}\n\n"

    # --- FAZA 4: RAPORT ---
    try:
        final_structure = list_project_files.invoke({})
    except:
        final_structure = "Błąd odczytu."

    return f"""
    # 🚀 Raport DevTeam (Smart Optimizer)
    
    ## 🎯 Zadanie
    {initial_task}
    
    ## 🧠 Optymalizacja
    Zastosowano Agenta Weryfikatora do sprawdzania spójności plików przed każdym krokiem.
    
    ## 📂 Finalna Struktura
    ```text
    {final_structure}
    ```
    
    ## 📝 Przebieg
    {execution_log}
    """