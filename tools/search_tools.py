from langchain_community.tools.tavily_search import TavilySearchResults

# Definiujemy narzędzie, ograniczając je do 3 wyników, aby było zwięzłe.
# LangChain automatycznie użyje zmiennej środowiskowej TAVILY_API_KEY.
search_tool = TavilySearchResults(max_results=3)