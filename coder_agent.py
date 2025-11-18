import os
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage # <-- Dodano SystemMessage
from tools import coder_tools

# --- 1. Konfiguracja Modelu ---
llm = ChatOllama(
    model="qwen2-coder:30b",
    base_url="http://localhost:11434",
    temperature=0,
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
# POPRAWKA: Usuwamy sporne parametry (state_modifier/messages_modifier).
# Tworzymy czystego agenta, a prompt przekażemy w wiadomościach.
agent_app = create_react_agent(llm, coder_tools)

def run_coder_agent(task: str):
    """
    Funkcja wrapper uruchamiająca agenta LangGraph z podanym zadaniem.
    """
    print(f"🚀 [LangGraph] Agent Programista otrzymał zadanie: {task}")
    
    # POPRAWKA: Przekazujemy System Prompt jako pierwszą wiadomość w liście.
    # To działa zawsze, niezależnie od wersji LangGraph.
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
        return {"output": error_msg}

# --- Testowanie ---
if __name__ == "__main__":
    print("Testowanie Agenta...")
    res = run_coder_agent("Napisz plik 'test.py' wypisujący 'Hello World'")
    print(res['output'])