# AI Agent 
## Spis treśći 
 * [Koncept](#koncept)
---
<details>
  <summary id="koncept">Koncept</summary>
  # 🚀 Koncept Sieci Agentów Programistycznych (DevTeam)

## 💡 Diagram Architektury Mermaid
```mermaid
graph TD
    %% Definicja Stylów
    classDef llm fill:#e0f7fa,stroke:#00bcd4,stroke-width:2px;
    classDef db fill:#fff3e0,stroke:#ff9800,stroke-width:2px;
    classDef agent fill:#e8f5e9,stroke:#4caf50,stroke-width:2px;
    classDef tool fill:#f3e5f5,stroke:#9c27b0,stroke-width:1px;
    classDef io fill:#fbe9e7,stroke:#ff5722,stroke-width:2px;

    %% Węzły
    subgraph Core Technologies
        O[Ollama LLMs]:::llm
        C(ChromaDB\nPamięć Długoterminowa):::db
       
    end

    subgraph LangChain Agents
        PM(1. PM - Menadżer Projektu):::agent
        ARC(2. Architekt/Projektant):::agent
        COD(3. Programista/Koder):::agent
        DOC(4. Dokumentalista):::agent
        QA(5. Tester/QA):::agent
    end

    subgraph Narzędzia (LangChain Tools)
        FT[FileManagementTool]:::tool
    end

    %% Połączenia Komunikacji (LLM)
    O --- PM
    O --- ARC
    O --- COD
    O --- DOC
    O --- QA

    %% Połączenia RAG (Pamięć)
    PM -->|Zapisuje: Plan| C
    C -->|Pobiera: Plan| ARC
    ARC -->|Zapisuje: Specyfikacja| C
    C -->|Pobiera: Specyfikacja/Kod| COD
    COD -->|Zapisuje: Wygenerowany Kod| C
    C -->|Pobiera: Wszystko| DOC
    QA -->|Zapisuje: Raporty Błędów| C

    %% Połączenia Narzędzia (I/O)
    PM -->|`create_directory`| FT
    ARC -->|`create_directory` / `write_file`| FT
    COD -->|`write_file`| FT
    QA -->|`read_file` / `write_file`| FT
    DOC -->|`read_file` / `write_file`| FT

    FT --> FS
```
</details>

---
