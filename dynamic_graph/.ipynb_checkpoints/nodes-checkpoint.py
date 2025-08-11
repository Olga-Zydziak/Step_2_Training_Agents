import pandas as pd

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


@node(name="load_data", description="Wczytuje dane z pliku CSV i umieszcza je w stanie.")
def load_data_node(state: dict) -> dict:
    """
    Wczytuje dane z pliku CSV i umieszcza je w stanie jako ramkę danych Pandas.
    """
    print("-> EXECUTING: load_data_node")
    try:
        df = pd.read_csv(state["input_path"])
        print(f"  [SUCCESS] Wczytano dane o kształcie: {df.shape}")
        # Zwracamy nowy stan z wczytaną ramką danych
        return {"dataframe": df}
    except Exception as e:
        error_message = f"Nie udało się wczytać danych z {state['input_path']}: {e}"
        print(f"  [ERROR] {error_message}")
        # Zwracamy błąd do stanu, aby system mógł na niego zareagować w przyszłości
        return {"error": error_message}

@node(name="discover_causality", description="Uruchamia algorytm odkrywania przyczynowości.")
def discover_causality_node(state: dict) -> dict:
    """
    ZAŚLEPKA: W przyszłości ten węzeł uruchomi algorytm odkrywania przyczynowości.
    """
    print("-> EXECUTING: discover_causality_node (TODO: Implementacja logiki)")
    # Na razie symulujemy działanie, przekazując dane dalej
    print("  [INFO] Odkrywanie przyczynowości... (symulacja)")
    return {} # Nie zmieniamy stanu

@node(name="validate_model", description="Przeprowadza testy walidacyjne na modelu przyczynowym.")
def validate_model_node(state: dict) -> dict:
    """
    ZAŚLEPKA: W przyszłości ten węzeł uruchomi testy walidacyjne dla modelu.
    """
    print("-> EXECUTING: validate_model_node (TODO: Implementacja logiki)")
    # Na razie symulujemy działanie
    print("  [INFO] Walidacja modelu... (symulacja)")
    return {} # Nie zmieniamy stanu

@node(name="check_validation", description="Sprawdza status walidacji i zwraca wynik (np. 'success' lub 'failure').")
def check_validation_status(state: dict) -> str: print("...CONDITION: check_validation_status -> success"); return "success"