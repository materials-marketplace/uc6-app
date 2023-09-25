import logging

from models.transformation import TransformationInput
from simulation_controller.simulation import Simulation


class SimulationManager:
    def __init__(self):
        self.simulations: dict[str, Simulation] = {}

    def _get_simulation(self, id: str) -> Simulation:
        """
        Get the simulation corresponding to the id.

        Args:
            id (str): unique id of he simulation

        Raises:
            KeyError: if there is no simulation matching the id

        Returns:
            Simulation instance
        """
        try:
            simulation = self.simulations[id]
            return simulation
        except KeyError as ke:
            message = f"Simulation with id '{id}' not found"
            logging.error(message)
            raise KeyError(message) from ke

    def _add_simulation(self, simulation: Simulation) -> str:
        """Append a simulation to the internal datastructure.

        Args:
            simulation (Simulation): Object to add

        Returns:
            str: ID of the added object
        """
        id: str = simulation.id
        self.simulations[id] = simulation
        return id

    def _delete_simulation(self, id: str):
        """Remove a simulation from the internal datastructure.

        Args:
            id (str): id of the simulation to remove
        """
        del self.simulations[id]

    def create_simulation(self, request_obj: TransformationInput) -> str:
        """Create a new simulation given the arguments.

        Args:
           requestObj: dictionary containing input configuration

        Returns:
            str: unique job id
        """
        return self._add_simulation(Simulation(request_obj))

    def get_simulation(self, id) -> dict:
        """Return information of one simulation.

        Args:
            id (str): id of the simulation

        Returns:
            list: list of simulation ids
        """
        simulation = self._get_simulation(id)
        return {
            "id": simulation.id,
            "parameters": simulation.parameters,
            "state": simulation.status,
        }

    def run_simulation(self, id):
        """Execute a simulation.

        Args:
            id (str): unique simulation id
        """
        self._get_simulation(id).run()

    def stop_simulation(self, id: str) -> dict:
        """Force terminate a simulation.

        Args:
            id (str): unique id of the simulation
        """
        self._get_simulation(id).stop()

    def delete_simulation(self, id: str) -> dict:
        """Delete all the simulation information.

        Args:
            id (str): unique id of simulation
        """
        self._get_simulation(id).delete()
        self._delete_simulation(id)

    def get_simulation_state(self, id: str):
        """Return the status of a particular simulation.

        Args:
            id (str): id of the simulation

        Returns:
            TransformationState: status of the simulation
        """
        return self._get_simulation(id).status

    def get_simulation_output_path(self, id: str) -> str:
        """Get the path to a simulation's output.

        Args:
            id (str): unique simulation id

        Returns:
            str: path to the simulation output
        """
        return self._get_simulation(id).get_output_path()

    def get_simulations(self) -> list:
        """Return information of all simulations.

        Returns:
            list: list of simulation ids
        """
        items = []
        for simulation in self.simulations.values():
            items.append(
                {
                    "id": simulation.id,
                    "parameters": simulation.parameters,
                    "state": simulation.status,
                }
            )
        return items
