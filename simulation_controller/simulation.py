import logging
import shutil
import uuid
from pathlib import Path

from marketplace_standard_app_api.models.transformation import (
    TransformationState,
)

from models.transformation import TransformationInput

from .matcalc_process import MatCalcProcess

SIMULATIONS_FOLDER_PATH = "/root/app/simulation_files"


class Simulation:
    """Manage a single simulation."""

    def __init__(self, simulation_input: TransformationInput):
        self.id: str = str(uuid.uuid4())
        self.parameters = simulation_input
        self.simulationPath = Path(SIMULATIONS_FOLDER_PATH, self.id)
        self.simulationPath.mkdir()
        self._process = MatCalcProcess(simulation_input, self.simulationPath)
        logging.info(
            f"Simulation '{self.id}' with "
            f"payload {simulation_input} created."
        )
        self._status: TransformationState = TransformationState.CREATED

    @property
    def status(self) -> TransformationState:
        """Getter for the status.

        If the simulation is running, the process is checked for completion.

        Returns:
            TransformationState: status of the simulation
        """
        if self._status == TransformationState.RUNNING:
            if not self._process.is_alive():
                return_code = self._process.exit_code
                if not return_code:
                    logging.info(f"Simulation '{self.id}' is now completed.")
                    self.status = TransformationState.COMPLETED
                else:
                    logging.error(f"Error occurred in simulation '{self.id}'.")
                    self.status = TransformationState.FAILED
        return self._status

    @status.setter
    def status(self, value: TransformationState):
        self._status = value

    def run(self):
        """
        Start running a simulation.

        A new process that calls the MatCalc functions,
        and the output is stored in a separate directory

        Raises:
            RuntimeError: when the simulation is already in progress
        """
        if self.status == TransformationState.RUNNING:
            msg = f"Simulation '{self.id}' already in progress."
            logging.error(msg)
            raise RuntimeError(msg)
        self._process.start()
        self.status = TransformationState.RUNNING
        logging.info(f"Simulation '{self.id}' started successfully.")

    def stop(self):
        """Stop a running process.

        Raises:
            RuntimeError: if the simulation is not running
        """
        if self.process is None:
            msg = f"No process to stop. Is simulation '{self.id}' running?"

            logging.error(msg)
            raise RuntimeError(msg)
        self.process.terminate()
        self.status = TransformationState.STOPPED
        self.process = None
        logging.info(f"Simulation '{self.id}' stopped successfully.")

    def delete(self):
        """
        Delete all the simulation folders and files.

        Raises:
            RuntimeError: if deleting a running simulation
        """
        if self.status == TransformationState.RUNNING:
            msg = f"Simulation '{self.id}' is running."
            logging.error(msg)
            raise RuntimeError(msg)
        shutil.rmtree(self.simulationPath)
        logging.info(f"Simulation '{self.id}' and related files deleted.")

    def get_output_path(self):
        """Return the zipped file with the simulation results."""
        if self.status == TransformationState.COMPLETED:
            return self.simulationPath / "results.zip"
