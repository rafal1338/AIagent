# coder_agent.py
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import coder_tools
# Importujemy pamięć (jeśli używasz)
from memory_tools import memory_tools_list

load_dotenv()

# Konfiguracja Ollama
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2-coder:30b")
OLLAMA_TOKEN = os.getenv("OLLAMA_TOKEN", "")
SSL_VERIFY_STR = os.getenv("OLLAMA_VERIFY_SSL", "True")
SSL_VERIFY = SSL_VERIFY_STR.lower() in ('true', '1', 't')

llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_URL,
    temperature=0,
    client_kwargs={
        "verify": SSL_VERIFY,
        "headers": {"Authorization": f"Bearer {OLLAMA_TOKEN}"}
    }
)

# --- PROMPT Z NACISKIEM NA ITERACJE ---
SYSTEM_PROMPT = """Jesteś Ekspertem Architektem Oprogramowania (Polyglot Developer).
Twoim celem jest tworzenie kompletnych, złożonych projektów.

ZASADY DZIAŁANIA:
1. **WIELE KROKÓW**: Nie bój się używać narzędzi wielokrotnie. Jeśli masz stworzyć 5 plików, wywołaj 'write_code_file' 5 razy.
2. **STRUKTURA**: Twórz pełną strukturę folderów (np. src/, public/, tests/).
3. **WERYFIKACJA**: Jeśli coś pójdzie nie tak, spróbuj to naprawić w kolejnym kroku.
4. **PAMIĘĆ**: Używaj 'save_to_memory' dla kluczowych funkcji.
5. Działaj autonomicznie aż do pełnego zakończenia zadania.
"""

# Łączymy narzędzia
all_tools = coder_tools + memory_tools_list

agent_app = create_react_agent(llm, all_tools)

def run_coder_agent(task: str, max_steps: int = 100):
    print(f"🚀 [LangGraph] Agent buduje projekt (Limit kroków: {max_steps})...")
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=task)
    ]
    
    try:
        # Zwiększamy limit rekurencji (domyślnie jest niski, ok. 25)
        # recursion_limit=100 pozwala na stworzenie dużego projektu w jednym podejściu
        result = agent_app.invoke(
            {"messages": messages}, 
            config={"recursion_limit": max_steps}
        )
        last_message = result["messages"][-1]
        return {"output": last_message.content}
    except Exception as e:
        # Obsługa błędu przekroczenia limitu
        if "recursion limit" in str(e).lower():
            return {"output": "⚠️ Agent osiągnął limit kroków. Projekt może być niekompletny, ale część plików została zapisana."}
        return {"output": f"❌ Błąd Agenta: {e}"}

if __name__ == "__main__":
    run_coder_agent("Stwórz rozbudowany projekt w Pythonie z 3 plikami w folderze src")