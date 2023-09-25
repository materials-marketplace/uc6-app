from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from marketplace_standard_app_api.models.transformation import (
    TransformationCreateResponse,
    TransformationId,
    TransformationListResponse,
    TransformationModel,
    TransformationState,
    TransformationStateResponse,
    TransformationUpdateModel,
    TransformationUpdateResponse,
)
from marketplace_standard_app_api.routers import object_storage

from models.transformation import TransformationInput
from simulation_controller.simulation_manager import SimulationManager

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
simulation_manager = SimulationManager()


@app.get(
    path="/health",
    summary="Check if application is running.",
)
def heartbeat():
    """Checks if the application is running and available"""
    return "MatCalc app is up and running"


@app.post(
    "/transformations",
    operation_id="newTransformation",
    summary="Create a new transformation",
    response_model=TransformationCreateResponse,
)
async def create_transformation(
    payload: TransformationInput,
) -> TransformationCreateResponse:
    """Create a new transformation."""
    id = simulation_manager.create_simulation(payload)
    return {"id": id}


@app.get(
    "/transformations/{transformation_id}",
    summary="Get a transformation",
    response_model=TransformationModel,
    operation_id="getTransformation",
    responses={
        404: {"description": "Not Found."},
        400: {"description": "Error executing get operation"},
    },
)
def get_simulation(transformation_id: TransformationId):
    try:
        return simulation_manager.get_simulation(str(transformation_id))
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke))
    except RuntimeError as re:
        raise HTTPException(status_code=400, detail=str(re))


@app.patch(
    "/transformations/{transformation_id}",
    operation_id="updateTransformation",
    summary="Update the state of the simulation.",
    response_model=TransformationUpdateResponse,
    responses={
        404: {"description": "Not Found."},
        409: {"description": "Requested state not available"},
        400: {"description": "Error executing update operation"},
    },
)
def update_simulation(
    transformation_id: TransformationId, payload: TransformationUpdateModel
) -> TransformationUpdateResponse:
    """Update an existing simulation.

    Args:
        transformation_id (TransformationId): ID of the transformation to be updated.
        payload (TransformationUpdateModel): State to which transformation is to be updated to.

    Returns:
        TransformationUpdateResponse: Returns ID and updated state of the transformation.
    """  # noqa: E501
    state = payload.state
    try:
        if state == TransformationState.RUNNING:
            simulation_manager.run_simulation(str(transformation_id))
        elif state == TransformationState.STOPPED:
            simulation_manager.stop_simulation(str(transformation_id))
        else:
            msg = f"{state} is not a supported state."
            raise HTTPException(status_code=400, detail=msg)

        return {"id": transformation_id, "state": state}

    except KeyError as ke:
        raise HTTPException(
            status_code=404,
            detail=f"Transformation not found: {transformation_id}",
        ) from ke
    except RuntimeError as re:
        raise HTTPException(status_code=409, detail="Runtime error") from re
    except Exception as e:
        msg = f"Unexpected error while changing state of simulation \
                {transformation_id}. Error message: {e}"
        raise HTTPException(status_code=400, detail=msg) from e


@app.get(
    "/transformations/{transformation_id}/state",
    operation_id="getTransformationState",
    summary="Get the state of the simulation.",
    response_model=TransformationStateResponse,
    responses={404: {"description": "Unknown simulation"}},
)
def get_simulation_state(
    transformation_id: TransformationId,
) -> TransformationStateResponse:
    """Get the state of a simulation.

    Args:
        transformation_id (TransformationId): ID of the simulation

    Returns:
        TransformationStateResponse: The state of the simulation.
    """
    try:
        state = simulation_manager.get_simulation_state(str(transformation_id))
        return {"id": transformation_id, "state": state}

    except KeyError as ke:
        raise HTTPException(
            status_code=404, detail="Simulation not found"
        ) from ke
    except Exception as e:
        msg = (
            "Unexpected error while querying for the status of simulation "
            f"{transformation_id}. Error message: {e}"
        )
        raise HTTPException(status_code=400, detail=msg) from e


@app.get(
    "/transformations",
    operation_id="getTransformationList",
    summary="Get all simulations.",
    response_model=TransformationListResponse,
)
def get_simulations() -> TransformationListResponse:
    """Fetch all simulations

    Returns:
        TransformationListResponse: List of simulations.
    """
    try:
        items = simulation_manager.get_simulations()
        return {"items": items}
    except Exception as e:
        msg = (
            "Unexpected error while fetching the list of simulations. "
            f"Error message: {e}"
        )
        # logging.error(msg)
        raise HTTPException(status_code=400, detail=msg) from e


@app.delete(
    "/transformations/{transformation_id}",
    operation_id="deleteTransformation",
    summary="Delete a transformation",
)
def delete_simulation(transformation_id: TransformationId):
    try:
        simulation_manager.delete_simulation(str(transformation_id))
        return {
            "status": f"Simulation '{transformation_id}' deleted successfully!"
        }

    except KeyError as ke:
        raise HTTPException(
            status_code=404, detail="simulation not found"
        ) from ke
    except RuntimeError as re:
        raise HTTPException(
            status_code=400, detail="Runtime error while deleting simulation"
        ) from re
    except Exception as e:
        msg = (
            "Unexpected error while deleting simulation "
            f"{transformation_id}. Error message: {e}"
        )
        # logging.error(msg)
        raise HTTPException(status_code=400, detail=msg)


@app.get(
    "/results",
    summary="Get a simulation's result",
    operation_id="getDataset",
)
def get_results(
    collection_name: object_storage.CollectionName,
    dataset_name: object_storage.DatasetName,
):
    return FileResponse(
        simulation_manager.get_simulation_output_path(str(dataset_name))
    )
