# devteam_runner.py
import json
import re
from coder_agent import run_coder_agent
from tools import write_code_file, list_project_files, system_log, get_project_knowledge_base

def extract_json_from_text(text):
    """Wyciąga JSON z odpowiedzi LLM (nawet jak doda jakieś śmieci dookoła)"""
    try:
        # Szukamy klamer [] lub {}
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except: pass
    return []

def run_devteam_pipeline(initial_task: str) -> str:
    system_log(f"⚡ START OPTYMALIZACJI: {initial_task}")
    
    # --- FAZA 1: PLANOWANIE JSON ---
    system_log("🧠 [1/2] Planowanie strukturalne...")
    knowledge = get_project_knowledge_base()
    
    # Wymuszamy format JSON dla łatwego parsowania
    plan_prompt = (
        f"Jesteś Tech Leadem. Zadanie: '{initial_task}'.\n"
        f"STAN PROJEKTU:\n{knowledge}\n"
        "Zwróć plan w czystym formacie JSON (lista stringów).\n"
        "Przykład: [\"Stwórz plik config.py\", \"Zaktualizuj main.py o funkcję X\"]\n"
        "Maksymalnie 3-5 kroków. Bądź precyzyjny co do nazw plików."
    )
    
    # Krótki limit kroków, bo to tylko generacja JSON
    agent_result = run_coder_agent(plan_prompt, max_steps=10)
    raw_output = agent_result.get('output', '')
    
    steps = extract_json_from_text(raw_output)
    
    if not steps:
        system_log("⚠️ Fallback: Model nie zwrócił JSON. Używam trybu bezpośredniego.")
        steps = [f"Zrealizuj zadanie: {initial_task}"]
    else:
        # Zapisujemy plan dla wglądu
        try: write_code_file.invoke({"filepath": "PLAN_JSON.md", "content": json.dumps(steps, indent=2), "description": "Plan JSON"})
        except: pass

    system_log(f"📋 Plan: {len(steps)} kroków.")

    # --- FAZA 2: SZYBKA EGZEKUCJA ---
    system_log("🚀 [2/2] Kodowanie...")
    execution_log = ""
    
    for i, step in enumerate(steps, 1):
        # Pobieramy mapę TYLKO RAZ na krok (oszczędność I/O)
        current_knowledge = get_project_knowledge_base()
        
        system_log(f"👉 Krok {i}: {step}")
        
        # Uruchamiamy Codera bezpośrednio (Weryfikator jest wbudowany w jego Prompt)
        res = run_coder_agent(step, current_knowledge, max_steps=50)
        out = res.get('output', 'Zrobione.')
        
        execution_log += f"#### Krok {i}: {step}\n{out}\n\n"

    # --- RAPORT ---
    system_log("🏁 Finalizacja...")
    try:
        final_map = get_project_knowledge_base()
    except:
        final_map = "Błąd odczytu mapy."

    return f"""
    # 🚀 Raport DevTeam (Optimized)
    ## Zadanie: {initial_task}
    
    ## 🗺️ Mapa Projektu
    ```text
    {final_map}
    ```
    ## 📝 Logi
    {execution_log}
    """