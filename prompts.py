import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Type

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
    def for_router(mission: str, agent_library_descriptions: str) -> PromptConfig:
        """Tworzy konfigurację promptu dla Agenta-Rutera."""
        return PromptConfig(
            system_prompt=SYSTEM_PROMPT_ANALYST,
            task_description="Twoim zadaniem jest zmontowanie idealnego zespołu (1-2 planistów, 1 krytyk) do przeprowadzenia burzy mózgów na zadany temat.",
            context={
                "mission": mission,
                "available_experts": agent_library_descriptions
            },
            output_schema=AgentSelection
        )

    @staticmethod
    def for_architect(mission: str, node_library_descriptions: str) -> PromptConfig:
        """Tworzy konfigurację promptu dla Agenta-Architekta, który ma stworzyć plan grafu."""
        return PromptConfig(
            system_prompt=SYSTEM_PROMPT_ANALYST,
            task_description="Twoim zadaniem jest zaprojektowanie kompletnego i odpornego na błędy przepływu pracy (workflow) w formacie JSON, który realizuje zadaną misję, korzystając z dostępnych narzędzi.",
            context={
                "mission": mission,
                "available_tools": node_library_descriptions
            },
            output_schema=WorkflowPlan
        )
