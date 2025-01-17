from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from uuid import uuid4

from .domain import *
from .score_analysis import *
from .demo_data import DemoData, generate_demo_data
from .solver import create_solver_manager_from_xml, create_solution_manager
from .solver_config_constants import SOLVER_CONFIGS

app = FastAPI(docs_url='/q/swagger-ui')
data_sets: dict[str, VehicleRoutePlan] = {}
solver_managers: dict[str, object] = {}

# TODO Can use for fronted option population
# @app.get("/solver-configs")
# async def solver_configs_list():
#     return list of configs

@app.get("/demo-data")
async def demo_data_list():
    return [e.name for e in DemoData]


@app.get("/demo-data/{dataset_id}", response_model_exclude_none=True)
async def get_demo_data(dataset_id: str) -> VehicleRoutePlan:
    demo_data = generate_demo_data(getattr(DemoData, dataset_id))
    return demo_data


@app.get("/route-plans/{problem_id}", response_model_exclude_none=True)
async def get_route(problem_id: str) -> VehicleRoutePlan:
    # TODO fix this globally
    problem_id = problem_id.strip('"')

    # Retrieve the latest best solution
    route = data_sets[problem_id]

    # Retrieve the solver for this problem
    solver_manager = solver_managers.get(problem_id)
    
    if solver_manager:
        solver_status = solver_manager.get_solver_status(problem_id)
    else:
        solver_status = "NOT_SOLVING" # If teriminates early there is a problem with solver_manager

    return route.model_copy(update={
        'solver_status': solver_status,
    })


def update_route(problem_id: str, route: VehicleRoutePlan):
    global data_sets
    data_sets[problem_id] = route


def json_to_vehicle_route_plan(json: dict) -> VehicleRoutePlan:
    visits = {
        visit['id']: visit for visit in json.get('visits', [])
    }
    vehicles = {
        vehicle['id']: vehicle for vehicle in json.get('vehicles', [])
    }

    for visit in visits.values():
        if 'vehicle' in visit:
            del visit['vehicle']

        if 'previousVisit' in visit:
            del visit['previousVisit']

        if 'nextVisit' in visit:
            del visit['nextVisit']

    visits = {visit_id: Visit.model_validate(visits[visit_id]) for visit_id in visits}
    json['visits'] = list(visits.values())

    for vehicle in vehicles.values():
        vehicle['visits'] = [visits[visit_id] for visit_id in vehicle['visits']]

    json['vehicles'] = list(vehicles.values())

    return VehicleRoutePlan.model_validate(json, context={
        'visits': visits,
        'vehicles': vehicles
    })


async def setup_context(request: Request) -> VehicleRoutePlan:
    json = await request.json()
    return json_to_vehicle_route_plan(json)

# TODO add better comments
@app.post("/route-plans")
async def solve_route(request: Request,
                      route: Annotated[VehicleRoutePlan, Depends(setup_context)]) -> str:
    # Get optimizer + time limit from the request
    body = await request.json()
    solver_config_key = body.get("solverConfig")
    time_limit_seconds = int(body.get("timeLimitSeconds"))

    solver_config_path = SOLVER_CONFIGS[solver_config_key]

    # Define new optimizer job
    job_id = str(uuid4())
    data_sets[job_id] = route

    # Create a solver manager from the chosen XML file
    solver_manager = create_solver_manager_from_xml(solver_config_path, time_limit_seconds)
    # Registering it globally so other functions reference the correct one
    solver_managers[job_id] = solver_manager

    # Build the solver job
    builder = solver_manager.solve_builder()
    builder = (
        builder
        .with_problem_id(job_id)
        .with_problem(route)
        .with_best_solution_consumer(lambda best_solution: update_route(job_id, best_solution))
    )
    builder.run()
    return job_id

@app.put("/route-plans/{problem_id}/analyze", response_model_exclude_none=True)
async def analyze_route(problem_id: str) -> dict[str, list[ConstraintAnalysisDTO]]:
    # TODO fix this globally
    problem_id = problem_id.strip('"')
    # Get the route for this problem
    route = data_sets[problem_id]
    # Retrieve the solver_manager for this problem
    solver_manager = solver_managers[problem_id]
    solution_manager = create_solution_manager(solver_manager)

    analysis_result = solution_manager.analyze(route)

    # Convert the analysis results into Data Transfer Objects
    constraints_dto = []
    for constraint_analysis in analysis_result.constraint_analyses:
        matches = []
        for match in constraint_analysis.matches:
            matches.append(MatchAnalysisDTO(
                name=match.constraint_ref.constraint_name,
                score=match.score,
                justification=match.justification
            ))
        constraint_dto = ConstraintAnalysisDTO(
            name=constraint_analysis.constraint_name,
            weight=constraint_analysis.weight,
            score=constraint_analysis.score,
            matches=matches
        )
        constraints_dto.append(constraint_dto)

    return {"constraints": constraints_dto}


@app.delete("/route-plans/{problem_id}")
async def stop_solving(problem_id: str) -> None:
    # TODO fix this globally
    problem_id = problem_id.strip('"')

    solver_manager = solver_managers.get(problem_id)
    if solver_manager:
        solver_manager.terminate_early(problem_id)


app.mount("/", StaticFiles(directory="static", html=True), name="static")
