from langchain_google_vertexai import ChatVertexAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel
from typing import Type
import outlines
from config import (
    MAIN_AGENT,
    CODE_MODEL,
    CRITIC_MODEL,
    PROJECT_ID,
    LOCATION
)

# Sekcja 1: Fabryki dla Bazowych Klientów LLM
# Te funkcje tworzą standardowe, "surowe" klienty LangChain.
# Wzorzec "singleton" (zmienna globalna _...) zapewnia, że każdy
# klient jest tworzony tylko raz, co oszczędza zasoby.
# ======================================================================


_main_llm_client = None
def get_main_llm():
    global _main_llm_client
    if _main_llm_client is None:
        _main_llm_client = ChatVertexAI(
            model_name=MAIN_AGENT,
            temperature=0.0,
            project=PROJECT_ID,
            location=LOCATION
        )
    return _main_llm_client


_code_llm_client = None
def get_code_llm():
    global _code_llm_client
    if _code_llm_client is None:
        _code_llm_client = ChatAnthropic(
            model_name=CODE_MODEL,
            temperature=0.0,
            max_tokens=4096
        )
    return _code_llm_client

_critic_llm_client = None
def get_critic_llm():
    global _critic_llm_client
    if _critic_llm_client is None:
        _critic_llm_client = ChatAnthropic(
            model_name=CRITIC_MODEL,
            temperature=0.0,
            max_tokens=2048
        )
    return _critic_llm_client


# ======================================================================
# Sekcja 2: "Wzmacniacz" z Biblioteki Outlines
# Ta funkcja jest sercem Twojego nowego, niezawodnego systemu.
# ======================================================================

def get_enforced_llm_generator(base_llm_client, pydantic_schema: Type[BaseModel]):
    """
    Uniwersalna funkcja, która bierze dowolnego klienta LangChain i "opakowuje"
    go w mechanizm wymuszania schematu Pydantic za pomocą biblioteki Outlines.

    Args:
        base_llm_client: Obiekt klienta LangChain (np. z get_main_llm()).
        pydantic_schema: Klasa Pydantic, której format ma być wymuszony.

    Returns:
        Funkcja-generator gotowa do wywołania z promptem.
    """
    # 1. Tworzymy model kompatybilny z Outlines na bazie klienta LangChain
    model = outlines.models.langchain(base_llm_client)
    
    # 2. Tworzymy generator, który wymusza konkretny schemat Pydantic
    generator = outlines.generate.json(model, pydantic_schema)
    
    # 3. Zwracamy gotową do użycia funkcję-generator
    return generator
