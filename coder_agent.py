# coder_agent.py
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import coder_tools
# Opcjonalnie import pamięci
try:
    from memory_tools import memory_tools_list
    all_tools = coder_tools + memory_tools_list
except ImportError:
    all_tools = coder_tools

load_dotenv()

# Konfiguracja
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2-coder:30b")
OLLAMA_TOKEN = os.getenv("OLLAMA_TOKEN", "")
SSL_VERIFY = os.getenv("OLLAMA_VERIFY_SSL", "True").lower() in ('true', '1', 't')

# Model
llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_URL,
    temperature=0.1,
    client_kwargs={
        "verify": SSL_VERIFY,
        "headers": {"Authorization": f"Bearer {OLLAMA_TOKEN}"}
    }
)

# --- PROMPTY ---

CODER_PROMPT = """Jesteś Senior Developerem. Budujesz kompletne oprogramowanie.

ZASADY PRACY:
1. **BRAK DUPLIKATÓW**: Nie twórz plików `_v2`, `_final`, `_new`. Zawsze edytuj istniejący plik (nadpisz go ulepszoną wersją).
2. **ROZWÓJ (INCREMENTAL)**: Jeśli plik istnieje, nie usuwaj jego kluczowych funkcji, chyba że to konieczne. Rozwijaj go.
3. **STRUKTURA**: Trzymaj się ustalonej struktury (np. backend/ w jednym miejscu). Nie twórz `backend_app` jeśli istnieje `backend`.
4. **KOD**: Pisz pełny, działający kod. Bez skrótów.

Twoim celem jest dostarczenie gotowego kodu.
"""

VERIFIER_PROMPT = """Jesteś Architektem Systemu (Verifier). 
Twoim zadaniem jest ochrona projektu przed chaosem i duplikatami.

Analizujesz ZADANIE oraz OBECNĄ STRUKTURĘ PLIKÓW.
Decydujesz, jak zmodyfikować zadanie, aby programista nie robił głupot.

SCENARIUSZE:
1. Zadanie: "Stwórz backend". Struktura: istnieje folder `backend/`.
   -> REAKCJA: Zmień zadanie na "Zaktualizuj i rozwiń istniejący kod w folderze backend/".
2. Zadanie: "Napisz main.py". Struktura: istnieje `app.py`.
   -> REAKCJA: Zmień zadanie na "Zaktualizuj istniejący plik app.py (zamiast tworzyć main.py)".
3. Zadanie: "Stwórz styles.css". Struktura: brak pliku.
   -> REAKCJA: Zostaw zadanie bez zmian.

Zwracasz TYLKO treść skorygowanego zadania.
"""

# --- Agenci ---
coder_app = create_react_agent(llm, all_tools)
# Weryfikator nie potrzebuje narzędzi do pisania, tylko mózgu, ale dajemy mu tools żeby mógł sprawdzić pliki sam w razie wątpliwości
verifier_app = create_react_agent(llm, all_tools) 

def run_coder_agent(task: str, max_steps: int = 60):
    """Uruchamia głównego programistę."""
    print(f"🚀 [Coder] Start (limit: {max_steps})...")
    messages = [SystemMessage(content=CODER_PROMPT), HumanMessage(content=task)]
    try:
        result = coder_app.invoke({"messages": messages}, config={"recursion_limit": max_steps})
        return {"output": result["messages"][-1].content}
    except Exception as e:
        return {"output": f"❌ Błąd Codera: {e}"}

def run_verifier_agent(original_task: str, current_structure: str):
    """
    Uruchamia weryfikatora, który sprawdza czy zadanie nie dubluje pracy.
    """
    print(f"🧐 [Verifier] Analiza pod kątem duplikatów...")
    
    verification_task = (
        f"ZADANIE ORYGINALNE: {original_task}\n"
        f"OBECNE PLIKI W PROJEKCIE:\n{current_structure}\n\n"
        "Jeśli zadanie sugeruje stworzenie czegoś, co już istnieje, przepisz je na polecenie EDYCJI/ROZWOJU. "
        "Jeśli zadanie jest bezpieczne (nowa funkcjonalność), zwróć je bez zmian. "
        "Odpowiedz TYLKO treścią zadania dla programisty."
    )
    
    messages = [SystemMessage(content=VERIFIER_PROMPT), HumanMessage(content=verification_task)]
    
    try:
        # Weryfikator ma mało kroków, bo tylko myśli
        result = verifier_app.invoke({"messages": messages}, config={"recursion_limit": 10})
        refined_task = result["messages"][-1].content
        print(f"✅ [Verifier] Zadanie po weryfikacji: {refined_task[:100]}...")
        return refined_task
    except Exception as e:
        print(f"⚠️ Błąd weryfikatora: {e}. Używam oryginału.")
        return original_task

if __name__ == "__main__":
    # Test
    pass