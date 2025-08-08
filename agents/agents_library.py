from prompts import *
from config import PROJECT_ID, LOCATION, MEMORY_ENGINE_DISPLAY_NAME, INPUT_FILE_PATH,MAIN_AGENT,CRITIC_MODEL,CODE_MODEL, API_TYPE_GEMINI,API_TYPE_SONNET, ANTHROPIC_API_KEY,basic_config_agent
from .agents import *
# --- Konfiguracja czatu grupowego ---
main_agent_configuration={"cache_seed": 42,"seed": 42,"temperature": 0.0,
                        "config_list": basic_config_agent(agent_name=MAIN_AGENT, api_type=API_TYPE_GEMINI, location=LOCATION, project_id=PROJECT_ID)}
critic_agent_configuration ={"cache_seed": 42,"seed": 42,"temperature": 0.0,
                        "config_list": basic_config_agent(api_key=ANTHROPIC_API_KEY,agent_name=CRITIC_MODEL, api_type=API_TYPE_SONNET)}



casual_agent_config = PromptEngine.for_causal_expert(mission, node_descriptions)
casual_prompt = PromptEngine.build(casual_agent_config)



data_scientist_config = PromptEngine.for_data_analyst(mission, node_descriptions)
data_scientist_prompt = PromptEngine.build(data_scientist_config)


#---WYWOŁANIE AGENTÓW
casual_agent = CasualAgent(llm_config=main_agent_configuration, prompt=casual_prompt)

data_scientist_agent = DataScientistAgent(llm_config=main_agent_configuration, prompt=data_scientist_prompt)
critic_agent = CriticAgent(llm_config=critic_agent_configuration, prompt=critic_prompt)



AGENT_LIBRARY = {
    "Ekspert_Przyczynowosci": casual_agent,
    "Analityk_Danych": data_scientist_agent,
    "Krytyk_Jakosci": critic_agent,
}