import pandas as pd
import numpy as np



# Tworzymy pusty rejestr i dekorator
NODE_LIBRARY = {}
def node(name: str, description: str):
    def decorator(func):
        NODE_LIBRARY[name] = {
            "function": func,
            "description": description
        }
        return func
    return decorator


# --- Węzły-Zaślepki ---
@node(name="load_data", description="Wczytuje dane z pliku CSV.")
def load_data_node(state: dict) -> dict:
    print("-> EXECUTING: load_data_node (ZAŚLEPKA)")
    return state

@node(name="discover_causality", description="Uruchamia agenta do odkrywania przyczynowości. UWAGA: Ta operacja jest złożona i może zakończyć się błędem.")
def discover_causality_node(state: dict) -> dict:
    print("-> EXECUTING: discover_causality_node (ZAŚLEPKA)")
    return state

@node(name="validate_model", description="Przeprowadza testy walidacyjne na modelu.")
def validate_model_node(state: dict) -> dict:
    print("-> EXECUTING: validate_model_node (ZAŚLEPKA)")
    return state

@node(name="universal_debugger", description="Narzędzie do diagnozowania i naprawiania błędów, które wystąpiły w innych węzłach.")
def universal_debugger_node(state: dict) -> dict:
    print("-> EXECUTING: universal_debugger_node (ZAŚLEPKA)")
    return state

@node(name="human_escalation", description="Narzędzie do eskalacji problemu do operatora ludzkiego, gdy automatyczna naprawa zawiedzie.")
def human_escalation_node(state: dict) -> dict:
    print("-> EXECUTING: human_escalation_node (ZAŚLEPKA)")
    return state

@node(name="check_for_error", description="Węzeł warunkowy. Sprawdza, czy poprzedni krok zakończył się błędem. Zwraca 'error' lub 'success'.")
def check_for_error(state: dict) -> dict:
    print("... CONDITION: check_for_error (ZAŚLEPKA) -> 'success'")
    return state
    
    
@node(name="generate_explainability_report", description="Generuje finalny raport wyjaśnialności, podsumowujący cały proces decyzyjny.")
def generate_report_node(state: dict) -> dict:
    """
    Zbiera artefakty ze stanu i tworzy spójny raport w formacie Markdown.
    """
    return state
