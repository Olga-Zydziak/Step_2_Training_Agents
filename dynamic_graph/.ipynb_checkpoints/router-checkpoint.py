import autogen
from typing import Optional, Dict, Any,Type
from pydantic import BaseModel, ValidationError
import json
from prompts import *

def get_structured_response(
    prompt: str, 
    response_model: Type[BaseModel], 
    llm_config: Dict, 
    max_retries: int = 3
) -> Optional[BaseModel]:
    """
    Wywołuje dowolnego agenta LLM i próbuje sparsować jego odpowiedź do modelu Pydantic.
    W przypadku błędu, prosi agenta o autokorektę.
    """
    # Używamy prostego agenta jako "wykonawcy" dla dowolnej konfiguracji LLM
    executor_agent = autogen.ConversableAgent("Executor", llm_config=llm_config)
    
    current_prompt = prompt
    for attempt in range(max_retries):
        print(f"INFO [StrucRes]: Próba {attempt + 1}/{max_retries}...")
        
        reply_dict  = executor_agent.generate_reply(messages=[{"role": "user", "content": current_prompt}])
        reply_content = reply_dict.get("content", "")
        try:
            # Próbujemy znaleźć i sparsować JSON z odpowiedzi
            json_str =reply_content[reply_content.find('{'):reply_content.rfind('}')+1]
            if not json_str:
                raise json.JSONDecodeError("Nie znaleziono obiektu JSON w odpowiedzi.", reply_content, 0)
            json_obj = json.loads(json_str)
            
            # Walidujemy, czy pasuje do naszego modelu Pydantic
            validated_obj = response_model.model_validate(json_obj)
            print("INFO [StrucRes]: Odpowiedź poprawna i zwalidowana.")
            return validated_obj
            
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"OSTRZEŻENIE [StrucRes]: Odpowiedź LLM nie jest poprawnym obiektem. Błąd: {e}")
            # Tworzymy nowy prompt z prośbą o autokorektę
            current_prompt = f"{prompt}\n\nTwoja poprzednia odpowiedź była niepoprawna: '{reply}'. Proszę, popraw ją i zwróć TYLKO I WYŁĄCZNIE poprawny obiekt JSON."
    
    print("BŁĄD [StrucRes]: Nie udało się uzyskać poprawnej odpowiedzi po maksymalnej liczbie prób.")
    return None



def select_team(user_query: str, agent_library: Dict, router_llm_config: Dict) -> Dict[str, Any]:
    """Dynamicznie wybiera zespół, używając uniwersalnej funkcji do odpowiedzi strukturalnych."""
    print("--- RUTER AGENTÓW: Uruchamiam uniwersalny wybór zespołu... ---")
    
    agent_descriptions = "\n".join(
        [f"- {name}: {agent.system_message.split('Specjalizacja:')[1].strip()}" for name, agent in agent_library.items()]
    )
    # Tworzymy konfigurację i budujemy prompt tak jak poprzednio
    router_config = PromptEngine.for_router(user_query, agent_descriptions)
    router_prompt = PromptEngine.build(router_config)
    
    # NOWOŚĆ: Wywołujemy naszą uniwersalną funkcję
    selection_obj = get_structured_response(
        prompt=router_prompt,
        response_model=AgentSelection,
        llm_config=router_llm_config
    )
    
    if selection_obj:
        selection = selection_obj.model_dump()
        print(f"--- RUTER AGENTÓW: Wybrany zespół -> {selection} ---")
        return {
            "planners": [agent_library[name] for name in selection["planners"]],
            "critic": agent_library[selection["critic"]]
        }
    else:
        # Tryb awaryjny, jeśli LLM nie zwrócił poprawnej odpowiedzi
        print("--- RUTER AGENTÓW: Działam w trybie awaryjnym. Wybieram domyślny zespół. ---")
        return {
            "planners": [agent_library["Analityk_Danych"]],
            "critic": agent_library["Krytyk_Jakosci"]
        }
