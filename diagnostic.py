import sys
import os
import importlib

print("--- 1. DIAGNOSTYKA ŚRODOWISKA ---")
print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print(f"Aktualny katalog: {os.getcwd()}")

print("\n--- 2. SPRAWDZANIE LANGCHAIN ---")
try:
    import langchain
    print(f"LangChain Version: {langchain.__version__}")
    print(f"LangChain Path: {langchain.__file__}")
except ImportError as e:
    print(f"BŁĄD: Nie można zaimportować 'langchain'. Szczegóły: {e}")
    sys.exit(1)
except AttributeError:
    print("BŁĄD: Zainstalowany pakiet langchain nie ma atrybutu __version__. To może oznaczać uszkodzoną instalację.")

print("\n--- 3. ANALIZA 'langchain.agents' ---")
try:
    import langchain.agents
    print(f"Ścieżka do agents: {langchain.agents.__file__}")
    
    # Sprawdzamy co jest w środku modułu
    attributes = dir(langchain.agents)
    
    if "AgentExecutor" in attributes:
        print("✅ SUKCES: 'AgentExecutor' JEST dostępny w 'langchain.agents'.")
    else:
        print("❌ PORAŻKA: 'AgentExecutor' NIE ZOSTAŁ znaleziony w 'langchain.agents'.")
        print("\nDostępne atrybuty w 'langchain.agents' (pierwsze 20):")
        print(attributes[:20]) # Wypiszmy, co tam w ogóle jest
        
except ImportError as e:
    print(f"BŁĄD: Nie można zaimportować 'langchain.agents'. Szczegóły: {e}")

print("\n--- 4. PRÓBA BEZPOŚREDNIEGO IMPORTU ---")
try:
    from langchain.agents import AgentExecutor
    print("✅ Udało się zaimportować: from langchain.agents import AgentExecutor")
except ImportError as e:
    print(f"❌ Błąd importu standardowego: {e}")

try:
    from langchain.agents.agent import AgentExecutor
    print("✅ Udało się zaimportować: from langchain.agents.agent import AgentExecutor")
except ImportError as e:
    print(f"❌ Błąd importu z .agent: {e}")