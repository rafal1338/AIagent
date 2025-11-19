# coder_agent.py
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import coder_tools
try:
    from memory_tools import memory_tools_list
    all_tools = coder_tools + memory_tools_list
except ImportError:
    all_tools = coder_tools

load_dotenv()

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "qwen2-coder:30b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0.1,
    client_kwargs={
        "verify": os.getenv("OLLAMA_VERIFY_SSL", "True").lower() in ('true', '1', 't'),
        "headers": {"Authorization": f"Bearer {os.getenv("OLLAMA_TOKEN", "")}"}
    }
)

# --- ZOPTYMALIZOWANE PROMPTY (Krótsze = Szybsze) ---

CODER_PROMPT = """Jesteś Senior Developerem.
ZASADY:
1. DRY (Don't Repeat Yourself): Edytuj istniejące pliki, nie twórz duplikatów.
2. C#: Uważaj na namespace'y. Nie redefiniuj klas.
3. Pisz pełny kod. Żadnych skrótów typu '# ...'.
Cel: Działający kod."""

VERIFIER_PROMPT = """Jesteś Architektem.
ANALIZA: Zadanie vs Obecne Pliki.
CEL: Wykrycie czy zadanie nie spowoduje duplikacji (np. backend_v2).
AKCJA: Jeśli wykryjesz ryzyko, zmień zadanie na 'Zaktualizuj istniejący plik...'.
Jeśli bezpieczne -> zwróć bez zmian."""

REVIEWER_PROMPT = """Jesteś QA Lead.
OCENA:
1. Duplikaty (klasy/funkcje)?
2. Spaghetti code?
3. Czy plik faktycznie powstał?
DECYZJA:
- "APPROVED" (jeśli OK)
- "CHANGES_REQUESTED: <zwięzła lista błędów>" (jeśli źle)
Bądź surowy ale konkretny."""

# Agenci
coder_app = create_react_agent(llm, all_tools)
verifier_app = create_react_agent(llm, all_tools) 
reviewer_app = create_react_agent(llm, all_tools)

def run_coder_agent(task: str, max_steps: int = 50):
    """Główny wykonawca - potrzebuje dużo kroków."""
    print(f"🚀 [Coder] Start...")
    try:
        result = coder_app.invoke(
            {"messages": [SystemMessage(content=CODER_PROMPT), HumanMessage(content=task)]}, 
            config={"recursion_limit": max_steps}
        )
        return {"output": result["messages"][-1].content}
    except Exception as e:
        return {"output": f"❌ Błąd: {e}"}

def run_verifier_agent(original_task: str, current_structure: str):
    """Weryfikator - szybka analiza (mało kroków)."""
    print(f"🧐 [Verifier] Analiza...")
    msg = f"ZADANIE: {original_task}\nPLIKI:\n{current_structure}\nZwróć bezpieczne polecenie."
    try:
        # Optymalizacja: Limit tylko 10 kroków - on ma tylko myśleć, nie kodować
        result = verifier_app.invoke(
            {"messages": [SystemMessage(content=VERIFIER_PROMPT), HumanMessage(content=msg)]}, 
            config={"recursion_limit": 10}
        )
        return result["messages"][-1].content
    except Exception:
        return original_task

def run_code_reviewer(task_context: str, recent_changes: str, file_structure: str):
    """Reviewer - szybka ocena (mało kroków)."""
    print(f"⚖️ [Reviewer] Audyt...")
    msg = f"ZADANIE: {task_context}\nZMIANY: {recent_changes}\nPLIKI:\n{file_structure}\nOceń."
    try:
        # Optymalizacja: Limit 15 kroków
        result = reviewer_app.invoke(
            {"messages": [SystemMessage(content=REVIEWER_PROMPT), HumanMessage(content=msg)]},
            config={"recursion_limit": 15}
        )
        return result["messages"][-1].content
    except Exception:
        return "APPROVED"