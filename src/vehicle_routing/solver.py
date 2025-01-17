from timefold.solver import SolverManager, SolutionManager, SolverFactory
from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig,
                                    TerminationConfig, Duration)
from pathlib import Path
from .domain import *
from .constraints import define_constraints

xml_path = Path(__file__).parent / "solver_configs" / "simulated_annealing.xml"
solver_config = SolverConfig.create_from_xml_resource(str(xml_path))

# Some overrides to the config:
termination_config = TerminationConfig(
    # Can use user input as steps
    spent_limit=Duration(seconds=30)
)
solver_config.termination_config = termination_config

score_director_config = ScoreDirectorFactoryConfig(
    constraint_provider_function=define_constraints
)
solver_config.score_director_factory_config = score_director_config

solver_manager = SolverManager.create(solver_config)
solution_manager = SolutionManager.create(solver_manager)

# Old solver config. TODO what does the optimizer use by default?
# solver_config = SolverConfig(
#     solution_class=VehicleRoutePlan,
#     entity_class_list=[Vehicle, Visit],
#     score_director_factory_config=ScoreDirectorFactoryConfig(
#         constraint_provider_function=define_constraints
#     ),
#     # Maybe we can do steps instead
#     termination_config=TerminationConfig(
#         spent_limit=Duration(seconds=30)
#     )
# )

# solver_manager = SolverManager.create(solver_config)
# solution_manager = SolutionManager.create(solver_manager)