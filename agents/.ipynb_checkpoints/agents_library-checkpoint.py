from prompts import (
    SYSTEM_PROMPT_ANALYST,
    SPEC_CAUSAL_EXPERT,
    SPEC_DATA_ANALYST,
    SPEC_CRITIC_AEGIS,
    SPEC_SELF_HEALING_CAPABILITY,
    SPEC_ARCHITECT_GPT
)
from config import PROJECT_ID, LOCATION, MEMORY_ENGINE_DISPLAY_NAME, INPUT_FILE_PATH,MAIN_AGENT,CRITIC_MODEL,CODE_MODEL,ARCHITECT_MODEL,API_TYPE_OPENAI, OPENAI_API_KEY, API_TYPE_GEMINI,API_TYPE_SONNET, ANTHROPIC_API_KEY,basic_config_agent
from .agents import *


# --- Konfiguracja czatu grupowego ---
main_agent_configuration={"cache_seed": 42,"seed": 42,"temperature": 0.0,
                        "config_list": basic_config_agent(agent_name=MAIN_AGENT, api_type=API_TYPE_GEMINI, location=LOCATION, project_id=PROJECT_ID)}
critic_agent_configuration ={"cache_seed": 42,"seed": 42,"temperature": 0.0,
                        "config_list": basic_config_agent(api_key=ANTHROPIC_API_KEY,agent_name=CRITIC_MODEL, api_type=API_TYPE_SONNET)}

architect_agent_configuration = critic_agent_configuration ={"cache_seed": 42,"seed": 42,"temperature": 0.0,
                        "config_list": basic_config_agent(api_key=ANTHROPIC_API_KEY,agent_name=ARCHITECT_MODEL, api_type=API_TYPE_SONNET)}
# openai_agent_configuration = {
#     "config_list": basic_config_agent(
#         agent_name=GPT_MODEL,
#         api_type=API_TYPE_OPENAI,
#         api_key=OPENAI_API_KEY),
#     "temperature": 0.0,
#     "cache_seed": 42
# }

# --- Budujemy Kompletne Persony ---
causal_expert_persona = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_CAUSAL_EXPERT}"
data_scientist_persona = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_DATA_ANALYST}"
critic_persona = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_CRITIC_AEGIS}"
architect_persona = f"{SYSTEM_PROMPT_ANALYST}\n\n{SPEC_ARCHITECT_GPT}"

# --- Tworzymy Instancje Agentów-Dyskutantów ---
planner_causal = CausalExpertAgent(llm_config=main_agent_configuration, prompt=causal_expert_persona)
planner_data = DataScientistAgent(llm_config=main_agent_configuration, prompt=data_scientist_persona)
architect = ArchitectAgent(llm_config=architect_agent_configuration, prompt=architect_persona)
critic = CriticAgent(llm_config=critic_agent_configuration, prompt=critic_persona)

# --- Biblioteka dla Rutera ---
DISCUSSION_AGENT_LIBRARY = {
    "Ekspert_Przyczynowosci": planner_causal,
    "Analityk_Danych": planner_data,
    "Architekt_GPT": architect,
    "Krytyk_Jakosci": critic,
}


# causal_discovery_worker = CausalDiscoveryAgent()
# model_validation_worker = ModelValidationAgent()

# WORKER_AGENT_LIBRARY = {
#     "discover_causality_worker": causal_discovery_worker,
#     "validate_model_worker": model_validation_worker
# }
