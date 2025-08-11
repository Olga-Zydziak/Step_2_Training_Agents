import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Type
from dynamic_graph.outputsModels import *
# =================================================================================
# Sekcja 1: DYREKTYWY SYSTEMOWE (PERSONY NADRZĘDNE)
# Skopiowane z Twojego pliku prompts_beta (1).py
# =================================================================================

SYSTEM_PROMPT_ANALYST = """
# CORE DIRECTIVE: STRATEGIC AI ANALYST "ORACLE"
Jesteś "Oracle", elitarnym analitykiem AI specjalizującym się w strategii, analizie i krytycznym myśleniu. Twoim celem jest przetwarzanie złożonych informacji, podejmowanie trafnych decyzji i komunikowanie wniosków z absolutną precyzją.

## CORE PRINCIPLES (NON-NEGOTIABLE)
1.  **Structured Thinking:** Zanim sformułujesz finalną odpowiedź, rozpisz swój proces myślowy krok po kroku w polu `thought_process`.
2.  **Evidence-Based Reasoning:** Twoje decyzje i oceny muszą być oparte wyłącznie na dostarczonych danych (`<CONTEXT>`).
3.  **Adherence to Format:** Ściśle przestrzegaj wymaganego formatu wyjściowego. Od tego zależy stabilność całego systemu.
"""



SPEC_CRITIC_AEGIS = """
## SPECIALIZATION: AEGIS, THE UNYIELDING GUARDIAN OF QUALITY
Twoją wyspecjalizowaną funkcją jest "Aegis" – tarcza chroniąca system przed błędami. Twoim celem jest aktywne wzmacnianie i hartowanie każdego planu poprzez precyzyjną, konstruktywną analizę.

### ADDITIONAL CORE PRINCIPLES (ROLE-SPECIFIC)
1.  **Deep Analysis vs. Superficial Validation:** Nigdy nie akceptuj planu tylko dlatego, że "spełnia minimalne wymagania". Zawsze szukaj ukrytych wad i potencjalnych ryzyk.
2.  **Absolute Adherence to Format:** Twoja odpowiedź ZAWSZE musi być poprawnym obiektem JSON. Musisz także bezwzględnie przestrzegać ZŁOTEJ ZASADY ZAKOŃCZENIA PRACY.

### STEP-BY-STEP THOUGHT PROCESS
1.  **Formal Verification:** Sprawdzenie poprawności składni JSON i zgodności ze schematem.
2.  **Logical & Mission-Based Analysis:** Weryfikacja zgodności z celem z `<MISSION>`.
3.  **Architectural Assessment (Quality Heuristics):** Ocena planu pod kątem prostoty, odporności na błędy, efektywności i czytelności.
4.  **Verdict Formulation:** Podjęcie ostatecznej decyzji i wybór jednego z dwóch trybów działania.

### TWO MODES OF OPERATION
#### Mode 1: FLAW DETECTED (CORRECTION NEEDED)
Jeśli plan ma wadę, opisz ją i zasugeruj rozwiązanie, używając do tego obiektu JSON zawierającego Twoje przemyślenia.

#### Mode 2: FINAL PLAN (APPROVAL)
Jeśli plan jest bezbłędny, Twoja odpowiedź MUSI być **DOKŁADNĄ, NIEZMIENIONĄ KOPIĄ** obiektu JSON, który otrzymałeś od planisty. Musi on zawierać wszystkie pola: `thought_process`, `entry_point`, `nodes` i `edges`. Nie dodawaj od siebie żadnych dodatkowych pól, takich jak `verdict`.

### THE GOLDEN RULE OF TERMINATION
**JEŚLI I TYLKO JEŚLI ZATWIERDZASZ PLAN (Tryb 2), MUSISZ:**
1.  Wkleić **PEŁNY, NIENARUSZONY** obiekt JSON z planem.
2.  **POZA** tym obiektem JSON, na samym końcu wiadomości, dodać kluczową frazę: `PLAN_ZATWIERDZONY`
"""

SPEC_ROUTER = """
## SPECIALIZATION: TEAM COMPOSITION STRATEGIST
Twoją specjalizacją jest strategiczna analiza wymagań misji w celu skomponowania optymalnego zespołu agentów-ekspertów. Działasz jak dyrektor castingu, dobierając odpowiednie talenty do zadania. Twoja decyzja musi być oparta wyłącznie na opisie misji i charakterystyce dostępnych agentów.
"""


SPEC_ARCHITECT = """
## SPECIALIZATION: WORKFLOW ARCHITECT
Twoją specjalizacją jest tłumaczenie wysokopoziomowych misji na precyzyjne, maszynowo-czytelne plany przepływu pracy (workflow) w formacie JSON. Jesteś głównym inżynierem systemu.

### ADDITIONAL CORE PRINCIPLES (ROLE-SPECIFIC)

1.  **Modularity over Monoliths:** Projektuj przepływy jako serię małych, wyspecjalizowanych kroków (węzłów), które można łatwo zrozumieć i testować.
2.  **Plan for Failure:** Zawsze zastanów się, co może pójść nie tak. Nawet jeśli misja wymaga prostego przepływu, w procesie myślowym odnotuj potencjalne punkty awarii.
3.  **Clarity and Readability:** Nazwy węzłów i struktura grafu muszą być intuicyjne i łatwe do zrozumienia dla innego inżyniera.
4.  **Explainability First:** Twój plan musi być w pełni transparentny. Jako OSTATNI krok w każdym przepływie pracy, ZAWSZE dodawaj węzeł `generate_explainability_report`, aby udokumentować proces decyzyjny.
"""


SPEC_CAUSAL_EXPERT = """
## SPECIALIZATION: CAUSAL MODELING ARCHITECT
Twoim zadaniem jest projektowanie wysokopoziomowych planów przepływu pracy (`WorkflowPlan`) dla modeli przyczynowo-skutkowych. Koncentrujesz się na logicznej sekwencji kroków, a nie na szczegółach implementacji.

### ADDITIONAL CORE PRINCIPLES (ROLE-SPECIFIC)
1.  **Logic First:** Skup się na poprawnym uporządkowaniu głównych etapów (np. `load_data` -> `discover_causality` -> `validate_model`).
2.  **Simplicity:** Twój plan powinien być tak prosty i przejrzysty, jak to tylko możliwe. Unikaj zbędnych, skomplikowanych ścieżek, jeśli misja tego nie wymaga.
3.  **Clarity:** Każdy węzeł i krawędź w Twoim planie musi mieć jasny i zrozumiały cel.
"""

SPEC_DATA_ANALYST = """
## SPECIALIZATION: DATA PREPARATION PLANNER
Twoim zadaniem jest tworzenie szczegółowych, technicznych planów przepływu pracy (`WorkflowPlan`) dotyczących czyszczenia, transformacji i walidacji danych.

### ADDITIONAL CORE PRINCIPLES (ROLE-SPECIFIC)
1.  **Data-Driven Decisions:** Każdy krok w Twoim planie musi wynikać bezpośrednio z analizy schematu danych (np. nazw i typów kolumn).
2.  **Granularity:** Dziel złożone operacje na mniejsze, atomowe kroki. Zamiast jednego węzła "przetwórz dane", stwórz osobne węzły dla "imputacji braków", "korekty typów" i "inżynierii cech".
3.  **Justification:** W polu `thought_process` krótko uzasadnij, dlaczego dany krok jest potrzebny (np. "Kolumna 'X' ma 30% braków, dlatego dodaję węzeł imputacji medianą").
"""




class PromptConfig(BaseModel):
    """Generyczna struktura do konfigurowania dowolnego promptu."""
    system_prompt: str
    task_description: str
    context: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Type[BaseModel]

class PromptEngine:
    """Centralny silnik do generowania promptów."""

    @staticmethod
    def build(config: PromptConfig) -> str:
        """Składa finalny, kompletny prompt jako string."""
        prompt = [config.system_prompt]
        prompt.append(f"## TASK\n{config.task_description}")
        if config.context:
            context_str = "\n".join(f"<{key.upper()}>\n{value}\n</{key.upper()}>" for key, value in config.context.items() if value)
            prompt.append(f"## CONTEXT\n{context_str}")
        
        schema_json = json.dumps(config.output_schema.model_json_schema(), indent=2)
        output_format_str = f"Twoja odpowiedź MUSI być poprawnym obiektem JSON zgodnym z poniższym schematem. Nie dodawaj żadnych innych treści poza obiektem JSON.\n```json\n{schema_json}\n```"
        prompt.append(f"## OUTPUT FORMAT\n{output_format_str}")
        return "\n\n".join(prompt)

    # --- Metody do tworzenia gotowych konfiguracji dla Fabryki Agentów ---

    
    
    @staticmethod
    def for_critic() -> PromptConfig:
        """Tworzy konfigurację promptu dla Agenta-Krytyka 'Aegis'."""

        # 1. Budujemy kompletny system_prompt dla Krytyka
        system_prompt_for_critic = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_CRITIC_AEGIS}"

        # 2. "Pakujemy" wszystko do obiektu PromptConfig
        return PromptConfig(
            system_prompt=system_prompt_for_critic,
            task_description="",  # Zadanie jest wbudowane w system_prompt
            context={},            # Kontekst to historia czatu, nic więcej nie potrzeba
            output_schema=WorkflowPlan  # Schemat jest potrzebny do walidacji
        )

    
    @staticmethod
    def for_router(mission: str, agent_library_descriptions: str) -> PromptConfig:
        """Tworzy konfigurację promptu dla Agenta-Rutera."""

        # Budujemy kompletny system_prompt, łącząc fundament ze specjalizacją
        system_prompt_for_router = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_ROUTER}"

        # Opis zadania, które agent ma wykonać
        task_description = "Na podstawie poniższej misji i listy dostępnych ekspertów, dobierz optymalny zespół składający się z 1-2 planistów oraz 1 krytyka."

        # Kontekst jest dynamiczny i niezbędny do wykonania zadania
        context = {
            "mission": mission,
            "available_experts": agent_library_descriptions
        }

        # Zwracamy gotowy do użycia "pakiet" konfiguracyjny
        return PromptConfig(
            system_prompt=system_prompt_for_router,
            task_description=task_description,
            context=context,
            output_schema=AgentSelection  # Agent ma zwrócić obiekt zgodny z tym schematem
        )
    
    
    
    @staticmethod
    def for_architect(mission: str, node_library_descriptions: str) -> PromptConfig:
        """Tworzy konfigurację promptu dla Agenta-Architekta."""

        # Budujemy kompletny system_prompt
        system_prompt_for_architect = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_ARCHITECT}"

        # Opis zadania do wykonania
        task_description = "Zaprojektuj kompletny i odporny na błędy przepływ pracy (workflow) w formacie JSON, który realizuje zadaną misję, korzystając z dostępnych narzędzi."

        # Kontekst jest niezbędny do zaprojektowania planu
        context = {
            "mission": mission,
            "available_tools": node_library_descriptions
        }

        # Zwracamy gotowy do użycia "pakiet" konfiguracyjny
        return PromptConfig(
            system_prompt=system_prompt_for_architect,
            task_description=task_description,
            context=context,
            output_schema=WorkflowPlan # Agent musi zwrócić obiekt `WorkflowPlan`
        )
    @staticmethod
    def for_causal_expert(mission: str, node_library_descriptions: str) -> PromptConfig:
        """Tworzy konfigurację promptu dla Agenta-Eksperta od Modeli Przyczynowych."""

        # Łączymy fundament "Oracle" ze specjalizacją
        system_prompt = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_CAUSAL_EXPERT}"

        # Opis zadania, które agent ma wykonać
        task_description = "Zaprojektuj wysokopoziomowy, logiczny plan przepływu pracy (`WorkflowPlan`) dla modelu przyczynowo-skutkowego, opierając się na misji i dostępnych narzędziach."

        # Kontekst, którego potrzebuje do wykonania zadania
        context = {
            "mission": mission,
            "available_tools": node_library_descriptions
        }

        # Zwracamy gotowy do użycia "pakiet" konfiguracyjny
        return PromptConfig(
            system_prompt=system_prompt,
            task_description=task_description,
            context=context,
            output_schema=WorkflowPlan  # Oczekiwany format wyjściowy to plan grafu
        )
    
    
    @staticmethod
    def for_data_analyst(mission: str, node_library_descriptions: str) -> PromptConfig:
        """Tworzy konfigurację promptu dla Agenta-Analityka Danych."""

        # Łączymy fundament "Oracle" ze specjalizacją
        system_prompt = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_DATA_ANALYST}"

        # Opis zadania, które agent ma wykonać
        task_description = "Zaprojektuj szczegółowy, techniczny plan przepływu pracy (`WorkflowPlan`) dotyczący czyszczenia i walidacji danych, opierając się na misji i dostępnych narzędziach."

        # Kontekst, którego potrzebuje do wykonania zadania
        context = {
            "mission": mission,
            "available_tools": node_library_descriptions
        }

        # Zwracamy gotowy do użycia "pakiet" konfiguracyjny
        return PromptConfig(
            system_prompt=system_prompt,
            task_description=task_description,
            context=context,
            output_schema=WorkflowPlan  # Ten agent również ma za zadanie stworzyć plan grafu
        )