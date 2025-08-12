import json
import os
import io
import autogen
from langgraph.graph import StateGraph, END 
from typing import List, Dict, Any, Optional, Type
from .router import get_structured_response,select_team
from agents.agents_library import DISCUSSION_AGENT_LIBRARY,main_agent_configuration
from agents.agents import CausalExpertAgent, DataScientistAgent
from .outputsModels import WorkflowPlan
from .nodes import NODE_LIBRARY
from prompts import *
import sys
from contextlib import redirect_stdout, redirect_stderr
LOGS_DIR = "reports"
LOG_FILE_PATH = os.path.join(LOGS_DIR, "planning_brainstorm.log")


PROMPT_FACTORY_MAP = {
    CausalExpertAgent: PromptEngine.for_causal_expert,
    DataScientistAgent: PromptEngine.for_data_analyst,
    # Można tu dodawać kolejne typy planerów w przyszłości
}


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
    team = select_team(mission, DISCUSSION_AGENT_LIBRARY, router_llm_config)
    planners = team["planners"]
    critic = team["critic"]

    # --- Krok 2: Przygotowanie Środowiska Dyskusji (AutoGen GroupChat) ---
    # Konfigurujemy agenta proxy oraz zasady "ruchu" w rozmowie.
    user_proxy = autogen.UserProxyAgent(
        name="Menedzer_Projektu",
        human_input_mode="NEVER",
        # === POPRAWKA 1: Nasłuchujemy na DOKŁADNĄ, wielkimi literami pisaną frazę ===
        is_termination_msg=lambda x: "PLAN_ZATWIERDZONY" in x.get("content", ""),
        code_execution_config=False
    )
    
    def custom_speaker_selection(last_speaker, groupchat):
        """Wymusza cykl debaty i zatrzymuje go po zatwierdzeniu planu."""
        messages = groupchat.messages
        planner_names = [p.name for p in planners]
        # Jeśli ostatnia wiadomość od Krytyka zawiera zatwierdzenie, zakończ dyskusję
        if last_speaker.name == critic.name and "PLAN_ZATWIERDZONY" in messages[-1].get("content", ""):
            return None # Zwrócenie None elegancko kończy rozmowę

        if last_speaker.name == "Menedzer_Projektu":
            return planners[0]
        
        # Po recenzji krytyka, pętla wraca do pierwszego planisty.
        if last_speaker.name == critic.name:
            return planners[0]

        # Jeśli ostatnio mówił planista...
        if last_speaker.name in planner_names:
            # Znajdź ostatnią turę krytyka.
            last_critic_turn_index = -1
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("name") == critic.name:
                    last_critic_turn_index = i
                    break
            
            # Zbierz, którzy planiści już mówili od ostatniej tury krytyka.
            speakers_since_critic = {msg.get("name") for msg in messages[last_critic_turn_index + 1:]}
            
            # Znajdź tych, którzy jeszcze nie mówili w tej rundzie.
            unspoken_planners = [p for p in planners if p.name not in speakers_since_critic]
            
            if unspoken_planners:
                # Jeśli są planiści, którzy jeszcze nie mówili, oddaj głos pierwszemu z nich.
                return unspoken_planners[0]
            else:
                # Jeśli wszyscy planiści już się wypowiedzieli, czas na krytyka.
                return critic
        
        # Domyślny fallback
        return planners[0]

    all_agents = [user_proxy] + planners + [critic]
    groupchat = autogen.GroupChat(
        agents=all_agents, 
        messages=[], 
        max_round=15, 
        speaker_selection_method=custom_speaker_selection
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=main_agent_configuration)
    
    descriptions = [f"- {name}: {details['description']}" for name, details in NODE_LIBRARY.items()]
    node_descriptions = "Dostępne narzędzia:\n" + "\n".join(descriptions)

    task_config = PromptEngine.for_architect(mission, node_descriptions)
    task_message = PromptEngine.build(task_config)
    
    planner_instance = planners[0]
    prompt_factory_method = PROMPT_FACTORY_MAP.get(type(planner_instance))

    # Zabezpieczenie: jeśli dla agenta (np. GPT) nie ma mapy, użyj ogólnego architekta
    if not prompt_factory_method:
        prompt_factory_method = PromptEngine.for_architect

    task_config = prompt_factory_method(mission, node_descriptions)
    task_message = PromptEngine.build(task_config)

    print("\n--- URUCHAMIANIE BURZY MÓZGÓW ---")
    
    user_proxy.initiate_chat(manager, message=task_message)
    
    # --- Krok 4: Zapis Logów i Ekstrakcja Finalnego Planu ---
    
    # Zapisujemy pełną konwersację do analizy
    os.makedirs(LOGS_DIR, exist_ok=True)

    # NOWA, BARDZIEJ CZYTELNA METODA ZAPISU LOGU Z MYŚLAMI AGENTÓW:
    with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("### ZAPIS PRZEBIEGU DYSKUSJI AGENTÓW (Z PROCESEM MYŚLOWYM) ###\n")
        f.write("="*60 + "\n\n")

        for i, msg in enumerate(groupchat.messages):
            speaker = msg.get("name", "Nieznany")
            content = msg.get("content", "").strip()

            f.write(f"---[ TURA {i+1}: Mówca: {speaker} ]---\n\n")

            try:
                # Spróbuj wyodrębnić JSON z wiadomości
                json_str = content[content.find('{'):content.rfind('}')+1]
                if not json_str: raise ValueError("Brak JSON w wiadomości")
                
                data = json.loads(json_str)
                
                # Jeśli jest proces myślowy, wyodrębnij go i sformatuj
                if "thought_process" in data:
                    thoughts = data.pop("thought_process") # Wyjmij myśli z danych
                    f.write("--- Myśli Agenta ---\n")
                    f.write(thoughts)
                    f.write("\n\n--- Oficjalna Odpowiedź ---\n")
                
                # Zapisz resztę JSON-a (czyli sam plan lub werdykt)
                f.write(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Sprawdź, czy poza JSON-em jest tekst (np. PLAN_ZATWIERDZONY)
                extra_text = content[content.rfind('}')+1:].strip()
                if extra_text:
                    f.write("\n\n" + extra_text)

            except (json.JSONDecodeError, ValueError, IndexError):
                # Jeśli to nie jest JSON, zapisz jako zwykły komunikat
                f.write("--- Komunikat ---\n")
                f.write(content if content else "[Pusta wiadomość]")

            f.write("\n\n" + "="*60 + "\n\n")

    print(f"\nINFO: Pełen, sformatowany log z procesem myślowym zapisano w {LOG_FILE_PATH}")
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






def build_and_run_graph(plan: WorkflowPlan, state_schema: Type, initial_state: Dict, stream_config: Dict = None):
    """
    Buduje graf, uruchamia go i GWARANTUJE zapis pełnego logu z wykonania do pliku,
    nawet w przypadku wystąpienia błędu krytycznego.
    """
    if stream_config is None:
        stream_config = {}

    log_file_path = os.path.join("reports", "graph_execution.log")
    os.makedirs("reports", exist_ok=True)
    
    # Używamy bufora w pamięci do przechwytywania logów w czasie rzeczywistym
    log_buffer = io.StringIO()
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Zaczynamy główny blok try...finally, aby zagwarantować wykonanie zapisu
    try:
        # Przekierowujemy standardowe wyjście (print) i błędy do naszego bufora
        sys.stdout = log_buffer
        sys.stderr = log_buffer

        print("--- ROZPOCZĘCIE BUDOWY I WYKONANIA GRAFU ---")
        
        workflow = StateGraph(state_schema)

        for node_def in plan.nodes:
            node_function = NODE_LIBRARY[node_def.implementation]['function']
            workflow.add_node(node_def.name, node_function)

        for edge_def in plan.edges:
            source = edge_def.source
            if edge_def.condition:
                condition_function = NODE_LIBRARY[edge_def.condition]['function']
                routes = {k: (END if v == "__end__" else v) for k, v in edge_def.routes.items()}
                workflow.add_conditional_edges(source, condition_function, routes)
            elif edge_def.target:
                target = END if edge_def.target == "__end__" else edge_def.target
                workflow.add_edge(source, target)
        
        workflow.set_entry_point(plan.entry_point)
        app = workflow.compile()

        print("\n--- STRUKTURA ZBUDOWANEGO GRAFU ---")
        app.get_graph().print_ascii()
        
        print("\n--- URUCHOMIENIE GRAFU ---")
        for event in app.stream(initial_state, stream_config):
            print(json.dumps(event, indent=2, ensure_ascii=False))

    except Exception as e:
        # Jeśli wystąpi JAKIKOLWIEK błąd, również go zapisujemy do bufora
        print(f"\n--- BŁĄD KRYTYCZNY: PRZERWANO WYKONANIE ---")
        import traceback
        traceback.print_exc()

    finally:
        # Ten blok wykona się ZAWSZE, niezależnie od tego, czy był błąd, czy nie.
        
        # 1. Przywracamy oryginalne wyjścia, aby konsola znowu działała normalnie
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        # 2. Pobieramy całą zawartość z bufora
        log_content = log_buffer.getvalue()
        
        # 3. Zapisujemy zawartość bufora do pliku
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        # 4. Wyświetlamy ostateczny log w konsoli
        print("\n" + "="*60)
        print(f"INFO: Pełen log z wykonania grafu został zapisany w: {log_file_path}")
        print("--- KONSOLA: Poniżej znajduje się ostateczna zawartość logu ---")
        print("="*60)
        print(log_content)

