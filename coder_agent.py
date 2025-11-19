# coder_agent.py
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import coder_tools
# Importujemy pamięć (jeśli jej używasz, jeśli nie - usuń ten import i "+ memory_tools_list")
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

# --- NOWY PROMPT WIELOJĘZYCZNY ---
SYSTEM_PROMPT = """Jesteś Ekspertem Architektem Oprogramowania (Polyglot Developer).
Twoim celem jest tworzenie kompletnych projektów programistycznych w DOWOLNYM języku (Python, JS, C#, Go, HTML/CSS itp.).

ZASADY:
1. STRUKTURA: Nie bój się tworzyć folderów. Używaj ścieżek typu 'src/main.py' lub 'public/index.html' w narzędziu 'write_code_file'.
2. KOMPLETNOŚĆ: Projekt musi mieć pliki konfiguracyjne (np. requirements.txt, package.json, CMakeLists.txt) jeśli są potrzebne.
3. PAMIĘĆ: Sprawdzaj 'search_memory' przed pracą i zapisuj ciekawe rozwiązania 'save_to_memory'.
4. ZAWSZE zapisuj kod na dysku.
5. Nie pytaj o zgodę. Działaj autonomicznie.
"""

# Łączymy narzędzia
all_tools = coder_tools + memory_tools_list

agent_app = create_react_agent(llm, all_tools)

def run_coder_agent(task: str):
    print(f"🚀 [LangGraph] Agent buduje projekt: {task}")
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=task)
    ]
    
    try:
        # Zwiększamy limit rekurencji, bo tworzenie wielu plików zajmuje więcej kroków
        result = agent_app.invoke({"messages": messages}, config={"recursion_limit": 50})
        last_message = result["messages"][-1]
        return {"output": last_message.content}
    except Exception as e:
        return {"output": f"❌ Błąd Agenta: {e}"}

if __name__ == "__main__":
    # Test wielojęzyczności
    run_coder_agent("Stwórz prostą stronę HTML w folderze 'www' z plikiem style.css")