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

llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_URL,
    temperature=0.1, # Lekko zwiększona kreatywność, ale niska dla stabilności kodu
    client_kwargs={
        "verify": SSL_VERIFY,
        "headers": {"Authorization": f"Bearer {OLLAMA_TOKEN}"}
    }
)

# --- ULEPSZONY PROMPT ---
SYSTEM_PROMPT = """Jesteś Senior Developerem. Budujesz kompletne, działające oprogramowanie.

ZASADY PRACY Z PLIKAMI:
1. **BRAK DUPLIKATÓW**: Zanim stworzysz nowy plik, sprawdź w treści zadania "OBECNA STRUKTURA PLIKÓW". Jeśli plik o podobnej nazwie istnieje (np. `app.py` vs `main.py`), użyj istniejącego.
2. **NADPISYWANIE**: Narzędzie `write_code_file` NADPISUJE plik. Jeśli chcesz zmienić kod, po prostu zapisz go w całości pod tą samą nazwą. Nie twórz plików `_final`, `_v2`.
3. **KOMPLETNOŚĆ**: Nie zostawiaj w kodzie komentarzy typu `# ... reszta kodu ...`. Pisz pełny, działający kod.
4. **STRUKTURA**: Grupuj pliki w foldery logiczne (src, tests, docs).

Twoim celem jest dostarczenie gotowego do uruchomienia projektu.
"""

agent_app = create_react_agent(llm, all_tools)

def run_coder_agent(task: str, max_steps: int = 60):
    print(f"🚀 [Agent] Start zadania (limit kroków: {max_steps})...")
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=task)
    ]
    
    try:
        # Recursion limit określa ile razy agent może użyć narzędzia w jednej sesji
        result = agent_app.invoke(
            {"messages": messages}, 
            config={"recursion_limit": max_steps}
        )
        last_message = result["messages"][-1]
        return {"output": last_message.content}
    except Exception as e:
        if "recursion limit" in str(e):
            return {"output": "⚠️ Przekroczono limit kroków. Część pracy została zapisana."}
        return {"output": f"❌ Błąd krytyczny agenta: {e}"}

if __name__ == "__main__":
    # Test
    run_coder_agent("Stwórz plik testowy i sprawdź czy nie duplikujesz.")