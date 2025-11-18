# AI Agent 
## Spis treśći 
 * [Koncept](#koncept)
---
<details>
  <summary id="koncept">Koncept</summary>
  # 🚀 Koncept Sieci Agentów Programistycznych (DevTeam)

## 💡 Diagram Architektury Mermaid
```mermaid
erDiagram
    %% RELACJE
    ApplicationUser ||--o{ Podmiot : "jest_powiazany_z_jednym"
    ApplicationUser ||--o{ Wiadomosc : "jest_autorem"
    Podmiot ||--o{ Grupa : "N{posiada_przynaleznosc}M"
    Grupa ||--o{ Watek : "1{jest_kategoria}N"
    Watek ||--o{ Wiadomosc : "1{zawiera_posty}N"
    Wiadomosc ||--o{ ApplicationUser : "N{autor}1"
    Wiadomosc ||--o{ Zalacznik : "N{zawiera}M"
    Grupa ||--o{ ApplicationUser : "N{ma_dostep_do}M"
    
    %% DEFINICJA TABEL
    ApplicationUser {
        string Id PK "PK z AspNet Identity"
        string UserName
        string Rola
        int PodmiotId FK "FK do Podmiot"
        datetime LockoutEnd
    }
    
    Podmiot {
        int Id PK
        string Nazwa
        bool IsActive
        string NIP         
        string REGON       
    }

    Grupa {
        int Id PK
        string Nazwa
        bool IsActive
    }

    Watek {
        int Id PK
        string Temat
        int GrupaId FK
    }

    Wiadomosc {
        int Id PK
        string Tresc
        datetime DataWyslania
        int WatekId FK
        string AutorId FK
    }

    Zalacznik {
        int Id PK
        string OryginalnaNazwa
        string SciezkaPliku
        string TypMIME
    }
```
</details>

---
