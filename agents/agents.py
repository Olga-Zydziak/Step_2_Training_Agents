import autogen
from autogen import Agent, ConversableAgent


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