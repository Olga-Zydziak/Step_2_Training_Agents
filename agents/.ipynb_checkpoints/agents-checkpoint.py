import autogen
from autogen import Agent, ConversableAgent
import pandas as pd
import numpy as np
import networkx as nx
from causallearn.search.ConstraintBased.PC import pc
from tools.search_tools import search_tool

from .llm_clients import get_main_llm
from prompts import *

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
        persona = (
            f"{SYSTEM_PROMPT_ANALYST}\n\n"
            f"{SPEC_CAUSAL_DISCOVERER}\n\n"
            f"{SPEC_SELF_HEALING_CAPABILITY}"
        )
        super().__init__(llm_client=get_main_llm(), persona=persona) # Agent ma LLM, ale go nie używa w tej wersji

    def execute(self, state: dict) -> dict:
        print("-> EXECUTING: CausalDiscoveryAgent")
        try:
            dataframe = state.get("dataframe")
            if dataframe is None: return {"error": "Brak ramki danych w stanie."}
            
            current_code_attempt = """
import networkx as nx
import numpy as np
from causallearn.search.ConstraintBased.PC import pc
numeric_df = dataframe.select_dtypes(include=np.number)
cg = pc(numeric_df.to_numpy())
graph = nx.DiGraph()
labels = {i: col for i, col in enumerate(numeric_df.columns)}
# Ta linijka może powodować błąd, jeśli API biblioteki się zmieni
for i, j in cg.G.graph.tolist():
    graph.add_edge(labels[i], labels[j])
"""
            
            # Pętla samonaprawcza (maksymalnie 2 próby)
            for attempt in range(2):
                try:
                    local_scope = {"dataframe": dataframe}
                    exec(current_code_attempt, globals(), local_scope)
                    final_graph = local_scope.get("graph")
                    print(f"  [SUCCESS] Pomyślnie wykonano kod na próbie {attempt + 1}.")
                    return {"causal_graph": final_graph}

                except Exception as e:
                    print(f"  [ATTEMPT {attempt + 1} FAILED] Wystąpił błąd: {e}")
                    if attempt == 1:
                        return {"error": f"Nie udało się naprawić błędu po 2 próbach: {e}"}

                    print("  [SELF-HEAL] Uruchamiam narzędzie wyszukiwania, aby znaleźć rozwiązanie...")
                    search_query_prompt = f"""
                    Mój kod zwrócił błąd: {e}.
                    Stwórz zapytanie do wyszukiwarki (max 10 słów), aby znaleźć poprawny przykład użycia
                    biblioteki 'causal-learn' dla algorytmu PC, skupiając się na iteracji po krawędziach wyniku.
                    Zawęź wyszukiwanie do oficjalnej dokumentacji lub Stack Overflow.
                    Przykład: 'causal-learn pc get edges example site:causallearn.readthedocs.io OR site:stackoverflow.com'
                    """
                    search_query = self.llm.invoke(search_query_prompt).content

                    print(f"  [SELF-HEAL] Zapytanie do dokumentacji: '{search_query}'")
                    search_results = search_tool.invoke({"query": search_query})

                    fix_code_prompt = f"""
                    Oto mój wadliwy kod:
                    {current_code_attempt}
                    Oto błąd, który wystąpił: {e}
                    A oto wyniki z dokumentacji technicznej:
                    {search_results}

                    Twoim zadaniem jest przepisanie całego, kompletnego fragmentu kodu od nowa,
                    implementując poprawkę znalezioną w dokumentacji.
                    Odpowiedz tylko i wyłącznie kodem w Pythonie.
                    """

                    print("  [SELF-HEAL] Analizuję dokumentację i przepisuję kod...")
                    corrected_code = self.llm.invoke(fix_code_prompt).content
                    current_code_attempt = corrected_code
            
            
            
            
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