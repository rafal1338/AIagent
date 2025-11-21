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
    temperature=0.1, # Niska temperatura dla precyzji
    client_kwargs={
        "verify": os.getenv("OLLAMA_VERIFY_SSL", "True").lower() in ('true', '1', 't'),
        "headers": {"Authorization": f"Bearer {os.getenv("OLLAMA_TOKEN", "")}"}
    }
)

# --- PROMPT CODERA (Egzekutor) ---
CODER_PROMPT = """Jesteś Elitarnym Programistą (Senior Architect).
Twoim celem jest JAKOŚĆ i OSZCZĘDNOŚĆ ZASOBÓW.

ZASADY KRYTYCZNE (ŁAMANIE ICH JEST ZABRONIONE):
1. **MAPA TO PRAWO**: Zanim stworzysz plik, sprawdź w 'MAPIE PROJEKTU' czy funkcjonalność już nie istnieje. Jeśli tak - EDYTUJ tamten plik.
2. **ZERO DUPLIKATÓW**: Nigdy nie twórz plików o nazwach `app_v2.py`, `main_new.py`. Nadpisuj oryginały.
3. **KOMPLETNY KOD**: Zabronione jest pisanie komentarzy typu `// ... reszta kodu`. Kod ma być gotowy do produkcji.
4. **OPIS**: Używając `write_code_file`, podawaj precyzyjny opis (parametr `description`), np. "Kontroler autoryzacji JWT".

Nie marnuj kroków na pytania. Analizuj -> Pisz -> Zapisz.
"""

# --- PROMPT WERYFIKATORA (Strażnik) ---
VERIFIER_PROMPT = """Jesteś Strażnikiem Spójności (Deduplication Guard).

Twoim jedynym zadaniem jest sprawdzenie, czy programista nie próbuje wyważyć otwartych drzwi.

WEJŚCIE: Zadanie + Mapa Projektu.
WYJŚCIE: Skorygowane zadanie.

LOGIKA DECYZJI:
- Jeśli zadanie brzmi "Stwórz obsługę bazy danych", a w mapie jest `db_context.py` (Opis: Połączenie z DB) ->
  Zwróć: "Zaktualizuj istniejący plik 'db_context.py' o brakujące funkcje."

- Jeśli zadanie brzmi "Stwórz main.py", a w mapie jest `app.py` ->
  Zwróć: "Zaktualizuj główny plik aplikacji 'app.py' (nie twórz main.py)."

Bądź surowy. Nie pozwalaj na bałagan.
"""

coder_app = create_react_agent(llm, all_tools)
verifier_app = create_react_agent(llm, all_tools) 

def run_coder_agent(task: str, max_steps: int = 40):
    try:
        result = coder_app.invoke(
            {"messages": [SystemMessage(content=CODER_PROMPT), HumanMessage(content=task)]}, 
            config={"recursion_limit": max_steps}
        )
        return {"output": result["messages"][-1].content}
    except Exception as e:
        return {"output": f"❌ Błąd: {e}"}

def run_verifier_agent(original_task: str, project_knowledge: str):
    msg = f"ZADANIE ORYGINALNE: {original_task}\n\nMAPA PROJEKTU:\n{project_knowledge}\n\nJeśli to duplikat, wskaż plik do edycji. Jeśli to nowość, zezwól."
    try:
        result = verifier_app.invoke(
            {"messages": [SystemMessage(content=VERIFIER_PROMPT), HumanMessage(content=msg)]}, 
            config={"recursion_limit": 5} 
        )
        return result["messages"][-1].content
    except Exception:
        return original_task