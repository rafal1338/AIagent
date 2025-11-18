import os
# Importujemy load_dotenv do wczytania pliku .env
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from tools import coder_tools

# --- 0. Ładowanie Konfiguracji ---
# Wczytuje zmienne z pliku .env do os.environ
load_dotenv()

# Pobieramy zmienne z bezpiecznymi wartościami domyślnymi
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2-coder:30b")
OLLAMA_TOKEN = os.getenv("OLLAMA_TOKEN", "")
# Konwersja stringa z .env na boolean (np. "False" -> False)
SSL_VERIFY_STR = os.getenv("OLLAMA_VERIFY_SSL", "True")
SSL_VERIFY = SSL_VERIFY_STR.lower() in ('true', '1', 't')

# Sprawdzenie czy token został podany (dla bezpieczeństwa)
if not OLLAMA_TOKEN:
    print("⚠️ OSTRZEŻENIE: Brak OLLAMA_TOKEN w pliku .env. Autoryzacja może się nie powieść.")

# --- 1. Konfiguracja Modelu ---
llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_URL,
    temperature=0,
    # Przekazujemy argumenty do klienta HTTP (httpx)
    client_kwargs={
        "verify": SSL_VERIFY,  # Używa wartości z .env (False dla self-signed)
        "headers": {
            "Authorization": f"Bearer {OLLAMA_TOKEN}"  # Pobiera token z .env
        }
    }
)

# --- 2. Prompt Systemowy ---
SYSTEM_PROMPT = """Jesteś Ekspertem Programistą (Coder Agent).
Twoim celem jest pisanie działającego, czystego kodu Python na podstawie poleceń.

ZASADY KRYTYCZNE:
1. Jeśli otrzymasz zadanie napisania kodu, MUSISZ go zapisać używając narzędzia 'write_code_file'.
2. Jeśli zadanie odwołuje się do specyfikacji, najpierw ją przeczytaj używając 'read_project_spec'.
3. Nie pytaj użytkownika o zdanie. Działaj autonomicznie.
4. Jeśli napotkasz błąd podczas zapisu, spróbuj ponownie.
5. ZAWSZE nadpisuj plik, jeśli tworzysz nową wersję.
"""

# --- 3. Tworzenie Agenta (LangGraph) ---
agent_app = create_react_agent(llm, coder_tools)

def run_coder_agent(task: str):
    """
    Funkcja wrapper uruchamiająca agenta LangGraph z podanym zadaniem.
    """
    print(f"🚀 [LangGraph] Agent Programista otrzymał zadanie: {task}")
    print(f"   (Model: {OLLAMA_MODEL}, URL: {OLLAMA_URL}, SSL Verify: {SSL_VERIFY})")
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=task)
    ]
    
    inputs = {"messages": messages}
    
    try:
        # Uruchamiamy graf agenta
        result = agent_app.invoke(inputs)
        
        # Ostatnia wiadomość w historii to odpowiedź końcowa modelu
        last_message = result["messages"][-1]
        return {"output": last_message.content}
        
    except Exception as e:
        error_msg = f"❌ Błąd krytyczny Agenta LangGraph: {e}"
        print(error_msg)
        # Jeśli błąd dotyczy SSL, dajemy podpowiedź
        if "SSLError" in str(e):
            print("💡 Podpowiedź: Sprawdź ustawienie OLLAMA_VERIFY_SSL w pliku .env")
        return {"output": error_msg}

# --- Testowanie ---
if __name__ == "__main__":
    print("Testowanie Agenta z konfiguracją ENV...")
    res = run_coder_agent("Napisz plik 'env_test.py' wypisujący 'Konfiguracja działa!'")
    print(res['output'])