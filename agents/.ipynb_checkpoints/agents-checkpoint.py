import autogen
from autogen import Agent, ConversableAgent

# --- Agenci-Dyskutanci (dla Fazy Projektowania - AutoGen) ---

class CausalExpertAgent(ConversableAgent):
    """Agent specjalizujący się w wysokopoziomowych planach przyczynowych."""
    def __init__(self, llm_config, prompt):
        super().__init__(name="Ekspert_Przyczynowosci", llm_config=llm_config, system_message=prompt)

class DataScientistAgent(ConversableAgent):
    """Agent tworzący szczegółowe, techniczne plany przygotowania danych."""
    def __init__(self, llm_config, prompt):
        super().__init__(name="Analityk_Danych", llm_config=llm_config, system_message=prompt)

class ArchitectAgent(ConversableAgent):
    """Agent-Architekt oparty na modelu GPT, specjalizujący się w projektowaniu odpornych grafów."""
    def __init__(self, llm_config, prompt):
        super().__init__(name="Architekt", llm_config=llm_config, system_message=prompt)

class CriticAgent(ConversableAgent):
    """Agent oceniający plan i dbający o jego jakość."""
    def __init__(self, llm_config, prompt):
        super().__init__(name="Krytyk_Jakosci", llm_config=llm_config, system_message=prompt)


# --- Klasa Bazowa dla "Robotników" (zostaje na przyszłość) ---
class WorkerAgent:
    """Klasa bazowa dla agentów, które działają jako węzły w grafie LangGraph."""
    def __init__(self, llm_client, persona: str):
        self.llm = llm_client
        self.persona = persona

    def execute(self, state: dict) -> dict:
        raise NotImplementedError("Każdy WorkerAgent musi mieć zaimplementowaną metodę execute.")