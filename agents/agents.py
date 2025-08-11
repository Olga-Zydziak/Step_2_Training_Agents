import autogen
from autogen import Agent, ConversableAgent

# NOWA KLASA BAZOWA DLA AGENTÓW WYKONAWCZYCH
class WorkerAgent:
    """
    Klasa bazowa dla agentów, które działają jako węzły w grafie LangGraph.
    Każdy taki agent ma swoją osobowość (prompt) i jedną metodę `execute`.
    """
    def __init__(self, llm_client, persona: str):
        self.llm = llm_client
        self.persona = persona

    def execute(self, state: dict) -> dict:
        """Ta metoda będzie wywoływana przez LangGraph."""
        # Domyślnie, jeśli agent nie ma logiki, zgłasza błąd.
        # Każdy agent-robotnik musi nadpisać tę metodę.
        raise NotImplementedError("Każdy WorkerAgent musi mieć zaimplementowaną metodę execute.")




class CasualAgent(ConversableAgent):
    """Agent decydujący, czy dane nadają się do dalszego przetwarzania."""
    def __init__(self, llm_config, prompt):
        super().__init__(
            name="CasualAgent",
            llm_config=llm_config,
            system_message=prompt
        )

#PLANNER AGENT        
class DataScientistAgent(ConversableAgent):
    """Agent tworzący szczegółowy plan przygotowania danych."""
    def __init__(self, llm_config, prompt):
        super().__init__(
            name="DataScientistAgent",
            llm_config=llm_config,
            system_message=prompt
        )

#CRITIC AGENT
class CriticAgent(ConversableAgent):
    """Agent oceniający plan i dbający o jego jakość."""
    def __init__(self, llm_config, prompt):
        super().__init__(
            name="CriticAgent",
            llm_config=llm_config,
            system_message=prompt
        )