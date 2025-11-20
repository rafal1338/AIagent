# coder_agent.py
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
# Importujemy tools i naszą funkcję logowania
from tools import coder_tools, system_log

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

CODER_PROMPT = """Jesteś Senior Developerem.
ZASADY KRYTYCZNE:
1. **NAZWY PLIKÓW**: Używaj nazw podanych w zadaniu.
2. **EDYCJA**: Nadpisuj istniejące pliki, nie twórz duplikatów.
3. **SAMOKONTROLA**: Pisz kod kompletny.
4. **TOOLS**: Zapisuj pliki na dysku.
"""

VERIFIER_PROMPT = """Jesteś Architektem Systemu.
Twój cel: Unikanie duplikatów plików.
Jeśli zadanie to "Zrób X", a plik już jest -> Zmień na "Edytuj plik X".
Zwróć TYLKO treść zadania.
"""

coder_app = create_react_agent(llm, all_tools)
verifier_app = create_react_agent(llm, all_tools) 

def run_coder_agent(task: str, max_steps: int = 40):
    system_log(f"🚀 [Coder] Start pracy: {task[:40]}...")
    try:
        result = coder_app.invoke(
            {"messages": [SystemMessage(content=CODER_PROMPT), HumanMessage(content=task)]}, 
            config={"recursion_limit": max_steps}
        )
        output = result["messages"][-1].content
        system_log(f"✅ [Coder] Zadanie zakończone.")
        return {"output": output}
    except Exception as e:
        system_log(f"❌ [Coder] Błąd: {e}")
        return {"output": f"❌ Błąd: {e}"}

def run_verifier_agent(original_task: str, current_structure: str):
    system_log("🧐 [Verifier] Analiza spójności plików...")
    msg = f"ZADANIE: {original_task}\nOBECNE PLIKI:\n{current_structure}\nZwróć poprawione zadanie."
    try:
        result = verifier_app.invoke(
            {"messages": [SystemMessage(content=VERIFIER_PROMPT), HumanMessage(content=msg)]}, 
            config={"recursion_limit": 5} 
        )
        refined = result["messages"][-1].content
        # Jeśli zadanie zostało zmienione, logujemy to
        if refined != original_task:
             system_log(f"💡 [Verifier] Korekta zadania -> {refined[:40]}...")
        return refined
    except Exception:
        return original_task