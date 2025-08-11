from typing import TypedDict,List, Dict, Any, Optional, Type
import pandas as pd
# Definiujemy strukturę danych, które będą krążyć w naszym grafie
class WorkflowState(TypedDict):
    mission: str
    input_path: str
    dataframe: pd.DataFrame
    causal_graph: Any
    validation_report: Dict
    final_summary: str
    error: str
    # NOWE POLA DLA AGENTA-SPRAWOZDAWCY
    router_decision: Dict  # Przechowa 'thought_process' i wybór Rutera
    architect_plan: Dict   # Przechowa pełny, zwalidowany plan (WorkflowPlan)
    planning_log: List[Dict] # Przechowa pełną rozmowę z "burzy mózgów"
    lime_shap_report_html: str  # Przechowa wizualizację LIME/SHAP jako HTML
    counterfactual_analysis: Dict # Przechowa wynik analizy "co by było, gdyby?"