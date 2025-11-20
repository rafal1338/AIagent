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

# --- PROMPTY ---

CODER_PROMPT = """Jesteś Głównym Architektem (Senior Developer).
Twoim celem jest budowa spójnego systemu, a nie zbioru przypadkowych plików.

ZASADY KRYTYCZNE:
1. **MAPA PROJEKTU**: Zawsze analizuj dostarczoną "MAPĘ PROJEKTU". Jeśli funkcjonalność już istnieje w jakimś pliku (nawet o innej nazwie), EDYTUJ GO.
2. **ZAPIS (WAŻNE)**: Używając `write_code_file`, MUSISZ podać parametr `description`. Opisz krótko, za co odpowiada plik (np. "Logika bazy danych", "Komponent nawigacji"). To buduje pamięć projektu.
3. **CZYSTOŚĆ**: Nie twórz duplikatów (np. `auth.py` i `login_service.py`). Trzymaj logiczne grupy razem.
4. **JAKOŚĆ**: Kod musi być kompletny.

Działaj jak profesjonalista.
"""

VERIFIER_PROMPT = """Jesteś Strażnikiem Spójności (Project Guard).

TWOJE ZADANIE:
Analizujesz zadanie w kontekście MAPY PROJEKTU.
Jeśli użytkownik prosi o "Stworzenie X", a w mapie widzisz, że plik Y już za to odpowiada -> Zmień zadanie na "Zaktualizuj plik Y".

Formatuj zadanie tak, aby było jednoznaczne dla programisty.
"""

coder_app = create_react_agent(llm, all_tools)
verifier_app = create_react_agent(llm, all_tools) 

def run_coder_agent(task: str, max_steps: int = 40):
    # Nie logujemy tutaj printem, bo orkiestrator to robi
    try:
        result = coder_app.invoke(
            {"messages": [SystemMessage(content=CODER_PROMPT), HumanMessage(content=task)]}, 
            config={"recursion_limit": max_steps}
        )
        return {"output": result["messages"][-1].content}
    except Exception as e:
        return {"output": f"❌ Błąd: {e}"}

def run_verifier_agent(original_task: str, current_structure: str):
    msg = f"ZADANIE: {original_task}\n\nMAPA PROJEKTU (Istniejące pliki):\n{current_structure}\n\nZwróć bezpieczne zadanie (edytuj istniejące zamiast tworzyć nowe)."
    try:
        result = verifier_app.invoke(
            {"messages": [SystemMessage(content=VERIFIER_PROMPT), HumanMessage(content=msg)]}, 
            config={"recursion_limit": 5} 
        )
        return result["messages"][-1].content
    except Exception:
        return original_task