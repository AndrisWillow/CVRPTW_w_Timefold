from pathlib import Path

SOLVER_CONFIGS = {
    "SIMULATED_ANNEALING": Path(__file__).parent / "solver_configs" / "simulated_annealing.xml",
    "HILL_CLIMBING": Path(__file__).parent / "solver_configs" / "hill_climbing.xml",
    "TABU_SEARCH": Path(__file__).parent / "solver_configs" / "tabu_search.xml",
    "LATE_ACCEPTANCE": Path(__file__).parent / "solver_configs" / "late_acceptance.xml",
    "DIVERSIFIED_LATE_ACCEPTANCE": Path(__file__).parent / "solver_configs" / "diversified_late_acceptance.xml",
    "GREAT_DELUGE": Path(__file__).parent / "solver_configs" / "great_deluge.xml",
    "STEP_COUNTING_HILL_CLIMBING": Path(__file__).parent / "solver_configs" / "step_counting_hill_climbing.xml",
    "STRATIGIC_OSCILLATION": Path(__file__).parent / "solver_configs" / "stratigic_oscillation.xml",
    "VARIABLE_NEIGHBORHOOD_DESCENT": Path(__file__).parent / "solver_configs" / "variable_neighborhood_descent.xml",
}