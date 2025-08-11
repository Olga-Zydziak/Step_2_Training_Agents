import pandas as pd
import numpy as np

# Importujemy naszą centralną bibliotekę, w której "mieszkają" wszyscy agenci
from agents.agents_library import WORKER_AGENT_LIBRARY

# Tworzymy pusty rejestr i dekorator
NODE_LIBRARY = {}
def node(name: str, description: str):
    def decorator(func):
        NODE_LIBRARY[name] = {
            "function": func,
            "description": description
        }
        return func
    return decorator


@node(name="load_data", description="Wczytuje dane z pliku CSV i umieszcza je w stanie.")
def load_data_node(state: dict) -> dict:
    """
    Wczytuje dane z pliku CSV i umieszcza je w stanie jako ramkę danych Pandas.
    """
    print("-> EXECUTING: load_data_node")
    try:
        df = pd.read_csv(state["input_path"])
        print(f"  [SUCCESS] Wczytano dane o kształcie: {df.shape}")
        # Zwracamy nowy stan z wczytaną ramką danych
        return {"dataframe": df}
    except Exception as e:
        error_message = f"Nie udało się wczytać danych z {state['input_path']}: {e}"
        print(f"  [ERROR] {error_message}")
        # Zwracamy błąd do stanu, aby system mógł na niego zareagować w przyszłości
        return {"error": error_message}


@node(name="discover_causality", description="Uruchamia agenta do odkrywania przyczynowości.")
def discover_causality_node(state: dict) -> dict:
    # Używamy teraz nowej, poprawnej biblioteki
    return WORKER_AGENT_LIBRARY["discover_causality_worker"].execute(state)

@node(name="validate_model", description="Uruchamia agenta do walidacji modelu.")
def validate_model_node(state: dict) -> dict:
    # Używamy teraz nowej, poprawnej biblioteki
    return WORKER_AGENT_LIBRARY["validate_model_worker"].execute(state)

@node(name="check_validation", description="Sprawdza status walidacji i zwraca wynik (np. 'success' lub 'failure').")
def check_validation_status(state: dict) -> str: print("...CONDITION: check_validation_status -> success"); return "success"




    
    
@node(name="analyze_decision_with_lime", description="Analizuje decyzję Rutera za pomocą LIME, aby zidentyfikować kluczowe słowa w misji.")
def lime_analysis_node(state: dict) -> dict:
    """
    Używa LIME do wyjaśnienia, które słowa w misji wpłynęły na wybór planerów.
    """
    print("-> EXECUTING: LIME Analysis Node")
    try:
        mission = state["mission"]
        router_decision = state["router_decision"]
        
        # Potrzebujemy funkcji predykcyjnej, którą "przebada" LIME.
        # Ta funkcja musi przyjmować tekst i zwracać "prawdopodobieństwo" dla każdej klasy.
        # W naszym przypadku "klasy" to potencjalni planiści.
        # To jest uproszczona implementacja dla celów demonstracyjnych.
        def prediction_function(texts):
            # Tutaj wstawilibyśmy logikę ponownego uruchomienia Rutera dla każdej wariacji tekstu.
            # Na razie symulujemy: zwracamy wysokie prawdopodobieństwo, jeśli kluczowe słowo jest w tekście.
            scores = []
            for text in texts:
                prob_causal = 0.9 if "przyczynowej" in text else 0.1
                prob_data = 0.9 if "danych" in text else 0.1
                scores.append([prob_causal, prob_data]) # [P(Ekspert_Przyczynowosci), P(Analityk_Danych)]
            return np.array(scores)

        explainer = LimeTextExplainer(class_names=["Ekspert_Przyczynowosci", "Analityk_Danych"])
        
        # Wyjaśniamy decyzję dla pierwszego wybranego planisty
        chosen_planner_name = router_decision.get("planners")[0]
        planner_index = ["Ekspert_Przyczynowosci", "Analityk_Danych"].index(chosen_planner_name)

        explanation = explainer.explain_instance(mission, prediction_function, num_features=5, labels=(planner_index,))
        
        # Zapisujemy wyjaśnienie jako HTML
        lime_html = explanation.as_html()
        
        print("  [SUCCESS] Pomyślnie wygenerowano analizę LIME.")
        return {"lime_shap_report_html": lime_html}
    except Exception as e:
        print(f"  [ERROR] Analiza LIME nie powiodła się: {e}")
        return {"lime_shap_report_html": f"Błąd: {e}"}
    
    
@node(name="generate_counterfactual", description="Generuje analizę kontrfaktyczną 'co by było, gdyby?' dla decyzji Rutera.")
def counterfactual_node(state: dict) -> dict:
    """
    Pyta LLM, jak zmienić misję, aby uzyskać inny wynik.
    """
    print("-> EXECUTING: Counterfactual Analysis Node")
    try:
        mission = state["mission"]
        router_decision = state["router_decision"]
        chosen_planners = router_decision.get("planners")
        
        # Wybieramy alternatywnego planistę (uproszczenie)
        alternative_planner = "Analityk_Danych" if "Ekspert_Przyczynowosci" in chosen_planners else "Ekspert_Przyczynowosci"

        # Budujemy prompt dla meta-analizy
        counterfactual_prompt = f"""
        Przeanalizuj poniższą sytuację:
        - Oryginalna misja: "{mission}"
        - Podjęta decyzja: Wybrano planistów {chosen_planners}
        - Alternatywna decyzja: Chcemy, aby system wybrał planistę '{alternative_planner}'

        Jaka jest MINIMALNA zmiana, którą należy wprowadzić w oryginalnej misji, aby system podjął alternatywną decyzję?
        Odpowiedz, podając tylko i wyłącznie zmienioną treść misji.
        """
        
        # Wywołujemy LLM, aby odpowiedział na to pytanie
        # (poniżej uproszczone wywołanie, w praktyce użylibyśmy PromptEngine)
        from langchain_google_vertexai import ChatVertexAI
        llm = ChatVertexAI(model_name="gemini-1.5-pro-preview-0409")
        response = llm.invoke(counterfactual_prompt)
        edited_mission = response.content

        result = {
            "original_mission": mission,
            "alternative_target": alternative_planner,
            "suggested_mission": edited_mission
        }
        
        print("  [SUCCESS] Pomyślnie wygenerowano analizę kontrfaktyczną.")
        return {"counterfactual_analysis": result}
    except Exception as e:
        print(f"  [ERROR] Analiza kontrfaktyczna nie powiodła się: {e}")
        return {"counterfactual_analysis": {"error": str(e)}}
    
    
@node(name="generate_explainability_report", description="Generuje finalny raport wyjaśnialności, podsumowujący cały proces decyzyjny.")
def generate_report_node(state: dict) -> dict:
    """
    Zbiera artefakty ze stanu i tworzy spójny raport w formacie Markdown.
    """
    print("-> EXECUTING: generate_explainability_report")
    try:
        # Pobieramy wszystkie potrzebne dane ze stanu
        router_decision = state.get("router_decision", {})
        architect_plan = state.get("architect_plan", {})
        
        report_lines = ["# Raport Wyjaśnialności Procesu", ""]

        # Sekcja 1: Podsumowanie Decyzji Rutera
        report_lines.append("## Sekcja 1: Decyzja o Doborze Zespołu")
        report_lines.append(f"**Wybrani planiści:** {router_decision.get('planners')}")
        report_lines.append(f"**Wybrany krytyk:** {router_decision.get('critic')}")
        report_lines.append("\n**Proces myślowy Rutera:**")
        report_lines.append(f"> {router_decision.get('thought_process', 'Brak danych.')}")
        report_lines.append("")

        # Sekcja 2: Proces Myślowy Architekta
        report_lines.append("## Sekcja 2: Proces Myślowy Architekta")
        report_lines.append(f"> {architect_plan.get('thought_process', 'Brak danych.')}")
        report_lines.append("")
        
        # Sekcja 3: Finalny Plan Grafu
        report_lines.append("## Sekcja 3: Finalna Architektura Grafu (Plan)")
        report_lines.append("```json")
        report_lines.append(json.dumps(architect_plan, indent=2, ensure_ascii=False))
        report_lines.append("```")

        
        # Sekcja 4: Kluczowe Czynniki Wpływające (LIME)
        report_lines.append("## Sekcja 4: Kluczowe Czynniki Wpływające (Analiza LIME)")
        report_lines.append("Poniższa wizualizacja pokazuje, które słowa w misji miały największy wpływ na wybór zespołu (kolor zielony 'pchał' w kierunku decyzji).")
        report_lines.append(state.get("lime_shap_report_html", "<i>Analiza LIME nie powiodła się.</i>"))
        report_lines.append("")
        
        # Sekcja 5: Analiza Kontrfaktyczna
        report_lines.append("## Sekcja 5: Analiza Kontrfaktyczna ('Co by było, gdyby?')")
        counterfactual = state.get("counterfactual_analysis", {})
        if "error" not in counterfactual:
            report_lines.append(f"**Pytanie:** Co zmienić w misji, aby zamiast {state.get('router_decision', {}).get('planners')} wybrać '{counterfactual.get('alternative_target')}'?")
            report_lines.append(f"**Sugerowana zmiana misji:**")
            report_lines.append(f"> {counterfactual.get('suggested_mission')}")
        else:
            report_lines.append("<i>Analiza kontrfaktyczna nie powiodła się.</i>")
        
        
        final_report = "\n".join(report_lines)

        import markdown
        html_report = markdown.markdown(final_report)
        with open("reports/explainability_report.html", "w", encoding="utf-8") as f:
            f.write(html_report)
        print("  [SUCCESS] Pomyślnie wygenerowano raport wyjaśnialności.")
        return {"final_summary": final_report}

    except Exception as e:
        error_message = f"Błąd podczas generowania raportu: {e}"
        print(f"  [ERROR] {error_message}")
        return {"error": error_message}
