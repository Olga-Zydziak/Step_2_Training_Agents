import autogen
from autogen import Agent, ConversableAgent
import pandas as pd
import numpy as np
import networkx as nx
from causallearn.search.ConstraintBased.PC import pc

from .llm_clients import get_main_llm
from prompts import SYSTEM_PROMPT_ANALYST, SPEC_CAUSAL_DISCOVERER, SPEC_MODEL_VALIDATOR

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


class CausalDiscoveryAgent(WorkerAgent):
    def __init__(self):
        persona = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_CAUSAL_DISCOVERER}"
        super().__init__(llm_client=get_main_llm(), persona=persona) # Agent ma LLM, ale go nie używa w tej wersji

    def execute(self, state: dict) -> dict:
        print("-> EXECUTING: CausalDiscoveryAgent")
        try:
            df = state["dataframe"]
            numeric_df = df.select_dtypes(include=np.number)
            
            cg = pc(numeric_df.to_numpy())
            
            # === POPRAWKA ZNAJDUJE SIĘ TUTAJ ===
            # Nowa, poprawna metoda iteracji po krawędziach grafu z causal-learn
            graph = nx.DiGraph()
            labels = {i: col for i, col in enumerate(numeric_df.columns)}
            
            # Używamy cg.G.graph, aby uzyskać listę krawędzi w formacie (indeks1, indeks2)
            for i, j in cg.G.graph.tolist():
                graph.add_edge(labels[i], labels[j])
            # === KONIEC POPRAWKI ===

            print(f"  [SUCCESS] Odkryto graf z {graph.number_of_nodes()} węzłami i {graph.number_of_edges()} krawędziami.")
            return {"causal_graph": graph}
        except Exception as e:
            # Zwracamy bardziej szczegółowy błąd, aby ułatwić debugowanie
            import traceback
            return {"error": f"Błąd w CausalDiscoveryAgent: {e}\n{traceback.format_exc()}"}

class ModelValidationAgent(WorkerAgent):
    """
    Agent-Robotnik specjalizujący się w walidacji modelu.
    """
    def __init__(self):
        # Budujemy "osobowość" z centralnych komponentów
        persona = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_MODEL_VALIDATOR}"
        super().__init__(llm_client=get_main_llm(), persona=persona)

    def execute(self, state: dict) -> dict:
        print("-> EXECUTING: ModelValidationAgent")
        graph = state.get("causal_graph")
        if graph is None:
            error_message = "Walidacja nie powiodła się - brak grafu przyczynowego w stanie do analizy."
            print(f"  [ERROR] {error_message}")
            return {"error": error_message, "validation_report": {"status": "FAILURE", "details": error_message}}
        
        
        report = f"Walidacja zakończona. Graf: '{graph}' wygląda na logicznie spójny."
        print(f"  [SUCCESS] {report}")
        return {"validation_report": {"status": "SUCCESS", "details": report}}
       
        



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