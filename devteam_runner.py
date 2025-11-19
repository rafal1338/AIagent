# devteam_runner.py
from coder_agent import run_coder_agent, run_verifier_agent, run_code_reviewer
from tools import write_code_file, list_project_files

def parse_plan_to_steps(plan_content: str) -> list[str]:
    steps = []
    for line in plan_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 5:
            cleaned_line = line.lstrip('0123456789.-*• ')
            steps.append(cleaned_line)
    return steps

def run_devteam_pipeline(initial_task: str) -> str:
    print(f"🚀 [DevTeam] Optymalizowany Start: {initial_task}")
    
    # --- FAZA 1: SZYBKIE PLANOWANIE ---
    print("🤖 [1/3] Planowanie...")
    plan_prompt = (
        f"Jesteś Tech Leadem. Stwórz listę 3-5 kroków technicznych dla zadania: '{initial_task}'.\n"
        "Każdy krok w nowej linii. Bez wstępów. Krok 1: Struktura."
    )
    # Limit tylko 15 kroków na planowanie - to ma być szybkie
    agent_result = run_coder_agent(plan_prompt, max_steps=15)
    
    # Parsujemy odpowiedź bezpośrednio (szybciej niż I/O pliku)
    plan_text = agent_result.get('output', '')
    steps = parse_plan_to_steps(plan_text)
    
    if not steps:
        print("⚠️ Fallback planowania.")
        steps = [f"Zrealizuj zadanie: {initial_task}"]
    else:
        # Zapisujemy plan dla potomności (asynchronicznie w logice)
        try:
            write_code_file.invoke({"filepath": "PLAN_PROJEKTU.md", "content": plan_text})
        except: pass

    print(f"📋 [Plan] {len(steps)} kroków.")

    # --- FAZA 2: EGZEKUCJA Z BEZPIECZNIKIEM ---
    print("🤖 [2/3] Realizacja...")
    execution_log = ""
    
    for i, step in enumerate(steps, 1):
        try:
            structure = list_project_files.invoke({})
        except:
            structure = "..."
            
        print(f"\n👉 Krok {i}: {step}")
        
        # 1. Weryfikacja (Szybka)
        task = run_verifier_agent(step, structure)
        
        # Pętla poprawkowa (Max 2 - optymalizacja czasu)
        max_retries = 2
        retry = 0
        done = False
        
        while not done and retry <= max_retries:
            if retry > 0: print(f"   🔄 Poprawka {retry}...")
            
            full_task = f"ZADANIE: {task}\nKONTEKST: {initial_task}\nPLIKI:\n{structure}"
            
            # 2. Coder (Główna praca)
            res = run_coder_agent(full_task, max_steps=50)
            out = res.get('output', '')
            
            # 3. Review (Szybki)
            # Pobieramy strukturę tylko jeśli review jest włączone
            new_struct = list_project_files.invoke({})
            review = run_code_reviewer(task, out, new_struct)
            
            if "APPROVED" in review:
                print("   ✅ Zatwierdzono")
                execution_log += f"#### Krok {i}: {step}\n{out}\n\n"
                done = True
            else:
                print(f"   🛑 Poprawki: {review[:40]}...")
                task = f"POPRAW KOD WEDŁUG UWAG: {review}\nKod musi być kompletny."
                retry += 1
                if retry > max_retries:
                    print("   ⚠️ Wymuszone przejście dalej.")
                    execution_log += f"#### Krok {i} (Warunkowo): {step}\n{out}\n\n"
                    done = True

    # --- FAZA 3: RAPORT ---
    try:
        final_files = list_project_files.invoke({})
    except:
        final_files = "Błąd."

    return f"""
    # 🚀 Raport DevTeam
    ## Zadanie: {initial_task}
    
    ## 📂 Pliki
    ```text
    {final_files}
    ```
    ## 📝 Szczegóły
    {execution_log}
    """