# memory_tools.py
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.tools import tool
from langchain_core.documents import Document

# 1. Ładowanie konfiguracji (tak samo jak w coder_agent)
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2-coder:30b")
OLLAMA_TOKEN = os.getenv("OLLAMA_TOKEN", "")
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "devteam_memory")

SSL_VERIFY_STR = os.getenv("OLLAMA_VERIFY_SSL", "True")
SSL_VERIFY = SSL_VERIFY_STR.lower() in ('true', '1', 't')

# 2. Konfiguracja Embeddings (Musi mieć te same ustawienia SSL/Auth co Chat!)
embeddings = OllamaEmbeddings(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_URL,
    client_kwargs={
        "verify": SSL_VERIFY,
        "headers": {
            "Authorization": f"Bearer {OLLAMA_TOKEN}"
        }
    }
)

# 3. Inicjalizacja Bazy Wektorowej
vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH
)

# --- Definicja Narzędzi ---

@tool
def save_to_memory(content: str, topic: str) -> str:
    """
    Zapisuje wiedzę, fragment kodu lub ważną notatkę do pamięci długoterminowej (ChromaDB).
    Użyj tego, gdy stworzysz coś użytecznego, co warto zapamiętać na przyszłość.
    
    Args:
        content: Treść do zapamiętania (np. funkcja w Pythonie).
        topic: Krótki opis tematu (np. "obsługa CSV", "konfiguracja Flask").
    """
    try:
        doc = Document(
            page_content=content,
            metadata={"topic": topic, "source": "agent"}
        )
        vector_store.add_documents([doc])
        return f"✅ Zapisano w pamięci pod tematem: '{topic}'"
    except Exception as e:
        return f"❌ Błąd zapisu do pamięci: {e}"

@tool
def search_memory(query: str) -> str:
    """
    Przeszukuje pamięć długoterminową w poszukiwaniu podobnych rozwiązań.
    Użyj tego ZANIM zaczniesz pisać kod, aby sprawdzić, czy już tego nie robiłeś.
    
    Args:
        query: Pytanie lub opis tego, czego szukasz (np. "jak połączyć się z bazą SQL").
    """
    try:
        results = vector_store.similarity_search(query, k=3)
        if not results:
            return "Brak wyników w pamięci."
        
        output = "🔍 Znaleziono w pamięci:\n"
        for i, doc in enumerate(results):
            output += f"--- Wynik {i+1} (Temat: {doc.metadata.get('topic', 'brak')}) ---\n"
            output += doc.page_content[:500] + "...\n" # Przycinamy, żeby nie było za długie
            
        return output
    except Exception as e:
        return f"❌ Błąd przeszukiwania pamięci: {e}"

# Eksportujemy listę narzędzi pamięci
memory_tools_list = [save_to_memory, search_memory]