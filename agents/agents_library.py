from prompts import SYSTEM_PROMPT_ANALYST
from config import PROJECT_ID, LOCATION, MEMORY_ENGINE_DISPLAY_NAME, INPUT_FILE_PATH,MAIN_AGENT,CRITIC_MODEL,CODE_MODEL, API_TYPE_GEMINI,API_TYPE_SONNET, ANTHROPIC_API_KEY,basic_config_agent
from .agents import *
# --- Konfiguracja czatu grupowego ---
main_agent_configuration={"cache_seed": 42,"seed": 42,"temperature": 0.0,
                        "config_list": basic_config_agent(agent_name=MAIN_AGENT, api_type=API_TYPE_GEMINI, location=LOCATION, project_id=PROJECT_ID)}
critic_agent_configuration ={"cache_seed": 42,"seed": 42,"temperature": 0.0,
                        "config_list": basic_config_agent(api_key=ANTHROPIC_API_KEY,agent_name=CRITIC_MODEL, api_type=API_TYPE_SONNET)}

#---WYWOŁANIE AGENTÓW
casual_agent = CasualAgent(llm_config=main_agent_configuration, prompt=SYSTEM_PROMPT_ANALYST + "\nSpecjalizacja: Tworzenie planów dla modeli przyczynowych.")
data_scientist_agent = DataScientistAgent(llm_config=main_agent_configuration, prompt=SYSTEM_PROMPT_ANALYST + "\nSpecjalizacja: Plany czyszczenia i walidacji danych.") # 
critic_agent = CriticAgent(llm_config=critic_agent_configuration, prompt=SYSTEM_PROMPT_ANALYST + "\nSpecjalizacja: Konstruktywna krytyka planów.")



AGENT_LIBRARY = {
    "Ekspert_Przyczynowosci": casual_agent,
    "Analityk_Danych": data_scientist_agent,
    "Krytyk_Jakosci": critic_agent,
}