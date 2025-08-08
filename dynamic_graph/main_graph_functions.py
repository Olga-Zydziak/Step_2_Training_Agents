import json
import os
import autogen
from typing import List, Dict, Any, Optional, Type
from .router import get_structured_response,select_team
from agents.agents_library import AGENT_LIBRARY,main_agent_configuration
from .outputsModels import WorkflowPlan
from prompts import *
LOGS_DIR = "reports"
LOG_FILE_PATH = os.path.join(LOGS_DIR, "planning_brainstorm.log")

def run_collaborative_planning(mission: str, router_llm_config: Dict) -> Optional[WorkflowPlan]:
    """
    Orkiestruje całym procesem autonomicznego planowania.

    Jako "reżyser" fazy projektowej, ta funkcja zarządza całym cyklem:
    1. Dynamicznie dobiera zespół agentów-ekspertów za pomocą inteligentnego Rutera.
    2. Konfiguruje ustrukturyzowaną "burzę mózgów" z jasno określonymi zasadami.
    3. Inicjuje dyskusję, przekazując agentom precyzyjnie zbudowany prompt.
    4. Po zakończeniu dyskusji, waliduje i wyodrębnia jej finalny produkt - obiekt WorkflowPlan.

    Args:
        mission: Wysokopoziomowy cel zdefiniowany przez użytkownika.
        router_llm_config: Konfiguracja LLM dla agenta-rutera.

    Returns:
        Obiekt Pydantic `WorkflowPlan` jeśli planowanie się powiodło, w przeciwnym razie None.
    """
    print("\n" + "="*50)
    print("### ROZPOCZYNANIE FAZY PROJEKTOWEJ ###")
    print("="*50)
    
    # --- Krok 1: Dynamiczny Wybór Zespołu przez Rutera ---
    # Delegujemy zadanie wyboru zespołu do modułu Rutera.
    # Zakładamy, że `select_team` jest niezawodny i zwróci poprawny zespół.
    team = select_team(mission, AGENT_LIBRARY, router_llm_config)
    planners = team["planners"]
    critic = team["critic"]

    # --- Krok 2: Przygotowanie Środowiska Dyskusji (AutoGen GroupChat) ---
    # Konfigurujemy agenta proxy oraz zasady "ruchu" w rozmowie.
    user_proxy = autogen.UserProxyAgent(
        name="Menedzer_Projektu",
        human_input_mode="NEVER",
        is_termination_msg=lambda x: "plan_zatwierdzony" in x.get("content", "").lower(),
        code_execution_config=False
    )
    
    def custom_speaker_selection(last_speaker, groupchat):
        """Wymusza cykl debaty: Planista -> Krytyk -> Planista."""
        if last_speaker.name == "Menedzer_Projektu": return planners[0]
        if last_speaker.name in [p.name for p in planners]: return critic
        return planners[0]

    all_agents = [user_proxy] + planners + [critic]
    groupchat = autogen.GroupChat(
        agents=all_agents, 
        messages=[], 
        max_round=12, 
        speaker_selection_method=custom_speaker_selection
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=main_agent_configuration)
    
    # --- Krok 3: Stworzenie Scenariusza i Uruchomienie "Burzy Mózgów" ---
    # Używamy `PromptEngine` do zbudowania precyzyjnego zadania dla zespołu.
    # W realnym systemie `node_descriptions` byłyby ładowane z biblioteki narzędzi.
    node_descriptions = "Dostępne narzędzia: ['load_data', 'discover_causality', 'validate_model', 'check_status']"
    architect_config = PromptEngine.for_architect(mission, node_descriptions)
    architect_prompt = PromptEngine.build(architect_config)
    
    print("\n--- URUCHAMIANIE BURZY MÓZGÓW ---")
    user_proxy.initiate_chat(manager, message=architect_prompt)
    
    # --- Krok 4: Zapis Logów i Ekstrakcja Finalnego Planu ---
    
    # Zapisujemy pełną konwersację do analizy
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(groupchat.messages, f, indent=2, ensure_ascii=False)
    print(f"\nINFO: Pełen log dyskusji zapisano w {LOG_FILE_PATH}")

    final_plan_message = None
    # Przeglądamy wiadomości od końca, aby znaleźć ostatnią wiadomość od krytyka z zatwierdzeniem
    for msg in reversed(groupchat.messages):
        content = msg.get("content", "")
        if "PLAN_ZATWIERDZONY" in content and msg.get("name") == critic.name:
            final_plan_message = content
            break

    if final_plan_message:
        try:
            # Niezawodne wyodrębnianie JSON-a, nawet jeśli LLM dodał dodatkowy tekst
            json_str = final_plan_message[final_plan_message.find('{'):final_plan_message.rfind('}')+1]
            plan_dict = json.loads(json_str)

            validated_plan = WorkflowPlan.model_validate(plan_dict)
            print("\n--- SUKCES: Plan został pomyślnie wygenerowany i zwalidowany. ---")
            return validated_plan
            
        except (json.JSONDecodeError, IndexError) as e:
            print(f"\n--- BŁĄD KRYTYCZNY: Nie udało się wyodrębnić planu z finalnej wiadomości. Błąd: {e} ---")
            return None
            
    print("\n--- ZAKOŃCZONO: Dyskusja zakończyła się bez zatwierdzonego planu. ---")
    return None






def build_and_run_graph(plan: WorkflowPlan, state_schema: Type, initial_state: Dict):
    """Buduje i uruchamia graf na podstawie planu."""
    # Tutaj wklejamy kod Fabryki Grafów, który już znamy
    workflow = StateGraph(state_schema)
    for node_def in plan.nodes:
        workflow.add_node(node_def.name, NODE_LIBRARY[node_def.implementation])
    for edge_def in plan.edges:
        source = edge_def.source
        if edge_def.condition:
            condition = NODE_LIBRARY[edge_def.condition]
            routes = {k: (END if v == "__end__" else v) for k, v in edge_def.routes.items()}
            workflow.add_conditional_edges(source, condition, routes)
        elif edge_def.target:
            target = END if edge_def.target == "__end__" else edge_def.target
            workflow.add_edge(source, target)
    workflow.set_entry_point(plan.entry_point)
    
    app = workflow.compile()
    print("\n--- STRUKTURA ZBUDOWANEGO GRAFU ---")
    app.get_graph().print_ascii()
    
    print("\n--- URUCHOMIENIE GRAFU ---")
    for event in app.stream(initial_state):
        print(event)
