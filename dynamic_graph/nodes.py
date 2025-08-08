def load_data_node(state: dict) -> dict: print("-> EXECUTING: load_data_node"); return state
def discover_causality_node(state: dict) -> dict: print("-> EXECUTING: discover_causality_node"); return state
def validate_model_node(state: dict) -> dict: print("-> EXECUTING: validate_model_node"); return state
def check_validation_status(state: dict) -> str: print("...CONDITION: check_validation_status -> success"); return "success"


NODE_LIBRARY = {
    "load_data": load_data_node,
    "discover_causality": discover_causality_node,
    "validate_model": validate_model_node,
    "check_validation_status": check_validation_status
}