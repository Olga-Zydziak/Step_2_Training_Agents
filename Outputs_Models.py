class AgentSelection(BaseModel):
    planners: List[str] = Field(description="Lista nazw agentów-planistów wybranych do zadania.")
    critic: str = Field(description="Nazwa agenta-krytyka wybranego do zadania.")

class NodeDefinition(BaseModel):
    name: str = Field(description="Unikalna nazwa węzła w grafie.")
    implementation: str = Field(description="Nazwa funkcji z biblioteki narzędzi, która realizuje ten węzeł.")

class EdgeDefinition(BaseModel):
    source: str = Field(alias="from", description="Nazwa węzła źródłowego.")
    target: Optional[str] = Field(alias="to", default=None, description="Nazwa węzła docelowego dla prostych krawędzi.")
    condition: Optional[str] = Field(default=None, description="Nazwa funkcji warunkowej z biblioteki narzędzi.")
    routes: Optional[Dict[str, str]] = Field(default=None, description="Mapa wyników warunku na nazwy węzłów docelowych.")

class WorkflowPlan(BaseModel):
    entry_point: str = Field(description="Nazwa węzła, od którego zaczyna się przepływ pracy.")
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
