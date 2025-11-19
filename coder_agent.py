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

CODER_PROMPT = """Jesteś Senior Developerem.
TWOIM CELEM JEST EFEKTYWNOŚĆ.

ZASADY KRYTYCZNE:
1. **NAZWY PLIKÓW**: Jeśli w zadaniu podano nazwę pliku (np. 'main.py'), UŻYJ JEJ. Nie wymyślaj własnych ('main_app.py').
2. **EDYCJA**: Zanim napiszesz kod, sprawdź czy plik istnieje. Jeśli tak -> NADPISZ GO ulepszoną wersją. Nie twórz duplikatów.
3. **SAMOKONTROLA**: Zanim zapiszesz plik, upewnij się, że kod jest kompletny (brak '# ...').
4. **TOOLS**: Używaj 'write_code_file' do zapisywania wyników.

Działaj szybko i precyzyjnie.
"""

# Verifier ma teraz kluczowe zadanie: mapowanie niejasnych poleceń na konkretne pliki
VERIFIER_PROMPT = """Jesteś Architektem Systemu (Deduplication Guard).

TWOJE ZADANIE:
Masz przed sobą ZADANIE i LISTĘ PLIKÓW.
Musisz przepisać zadanie tak, aby wymusić użycie istniejących plików.

PRZYKŁADY:
- Zadanie: "Stwórz backend". Pliki: ['app.py']. 
  -> Wynik: "Zaktualizuj istniejący plik 'app.py' o logikę backendu."
  
- Zadanie: "Dodaj style". Pliki: ['styles/main.css']. 
  -> Wynik: "Edytuj plik 'styles/main.css'."

- Zadanie: "Stwórz plik utils.py". Pliki: [].
  -> Wynik: "Stwórz nowy plik 'utils.py'."

Jeśli zadanie jest ogólne, SKONKRETYZUJ JE o nazwy plików z listy.
Odpowiedz TYLKO treścią nowego zadania.
"""

# Tworzymy agentów
coder_app = create_react_agent(llm, all_tools)
verifier_app = create_react_agent(llm, all_tools) 

def run_coder_agent(task: str, max_steps: int = 40):
    """Główny wykonawca - limit zmniejszony do 40 dla szybkości, ale wystarczający."""
    print(f"🚀 [Coder] Pracuję nad: {task[:50]}...")
    try:
        result = coder_app.invoke(
            {"messages": [SystemMessage(content=CODER_PROMPT), HumanMessage(content=task)]}, 
            config={"recursion_limit": max_steps}
        )
        return {"output": result["messages"][-1].content}
    except Exception as e:
        return {"output": f"❌ Błąd: {e}"}

def run_verifier_agent(original_task: str, current_structure: str):
    """Szybka analiza (max 5 kroków) mająca na celu wykrycie duplikatów."""
    print(f"🧐 [Verifier] Sprawdzam spójność plików...")
    msg = f"ZADANIE: {original_task}\nOBECNE PLIKI W PROJEKCIE:\n{current_structure}\nZwróć konkretne polecenie dla programisty."
    try:
        # Bardzo niski limit kroków - on ma tylko pomyśleć i odpisać, nie używać narzędzi
        result = verifier_app.invoke(
            {"messages": [SystemMessage(content=VERIFIER_PROMPT), HumanMessage(content=msg)]}, 
            config={"recursion_limit": 5} 
        )
        return result["messages"][-1].content
    except Exception:
        # W razie błędu zwracamy oryginał
        return original_task