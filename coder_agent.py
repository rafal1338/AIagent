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

# Używamy temperature=0 dla maksymalnej precyzji i powtarzalności
llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "qwen2-coder:30b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0, 
    client_kwargs={
        "verify": os.getenv("OLLAMA_VERIFY_SSL", "True").lower() in ('true', '1', 't'),
        "headers": {"Authorization": f"Bearer {os.getenv("OLLAMA_TOKEN", "")}"}
    }
)

# --- SUPER-PROMPT (2 w 1: Architekt + Coder) ---
CODER_SYSTEM_PROMPT = """Jesteś Głównym Architektem i Programistą (Lead Dev).
Twoim celem jest realizacja zadania przy MINIMALNEJ liczbie kroków i MAKSYMALNEJ jakości.

KRYTYCZNE ZASADY (Strict Mode):
1. **MAPA PROJEKTU**: Masz dostęp do mapy istniejących plików. 
   - Jeśli zadanie dotyczy logiki, która już istnieje -> EDYTUJ ten plik. 
   - NIE TWÓRZ DUPLIKATÓW (np. jeśli jest `auth.py`, nie rób `login.py`).
2. **PRECYZJA**: Używając `write_code_file`, parametr `description` musi być techniczny i konkretny.
3. **KOMPLETNOŚĆ**: Kod musi być gotowy do uruchomienia. Żadnych placeholderów.
4. **OSZCZĘDNOŚĆ**: Nie pytaj. Nie gadaj. Pisz kod i zapisuj.

Jeśli widzisz w zadaniu nazwę pliku, UŻYJ JEJ.
"""

agent_app = create_react_agent(llm, all_tools)

def run_coder_agent(task: str, project_context: str = "", max_steps: int = 40):
    """
    Uruchamia zoptymalizowanego agenta.
    """
    # Wstrzykujemy kontekst (mapę) bezpośrednio do promptu użytkownika
    full_prompt = (
        f"ZADANIE: {task}\n\n"
        f"KONTEKST PROJEKTU (MAPA):\n{project_context}\n\n"
        "WYKONAJ ZADANIE. Jeśli plik istnieje w mapie, zaktualizuj go."
    )
    
    try:
        result = agent_app.invoke(
            {"messages": [
                SystemMessage(content=CODER_SYSTEM_PROMPT), 
                HumanMessage(content=full_prompt)
            ]}, 
            config={"recursion_limit": max_steps}
        )
        return {"output": result["messages"][-1].content}
    except Exception as e:
        return {"output": f"❌ Critical Error: {e}"}