"""
MATLAB-Python interface for running Simulink simulations.
This module provides functionality to start/stop the MATLAB engine,
run simulations, and extract/process results.
"""

import logging
import matlab.engine
import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union, Iterator, NamedTuple, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("matlab_simulation")

# --- Constants ---
SIMULATION_STOP_TIME_S = 50
DEFAULT_SIMULATION_SPEED = 1.0
SIMULATION_MODEL_NAME = "CompleteV1"

# --- Data Structures ---
@dataclass
class SimulationParameters:
    """Represents parameters for the simulation."""

    bay1_occupied: float = 0.0  # boolean (0.0/1.0)
    bay2_occupied: float = 0.0  # boolean (0.0/1.0)
    bay3_occupied: float = 0.0  # boolean (0.0/1.0)
    bay4_occupied: float = 0.0  # boolean (0.0/1.0)
    bay1_percentage: float = 0.0  # percentage (0.0-100.0)
    bay2_percentage: float = 0.0  # percentage (0.0-100.0)
    bay3_percentage: float = 0.0  # percentage (0.0-100.0)
    bay4_percentage: float = 0.0  # percentage (0.0-100.0)
    PVOutput: float = 10.0  # kW per hour (DC)
    battery_soc: float = 0.0  # percentage (0.0-100.0)
    GridPeak: float = 0.0  # boolean (0.0/1.0) - Peak time indicator for grid pricing
    BatteryOutput: float = 30.0  # kW

    def to_dict(self) -> Dict[str, float]:
        """Convert parameters to a dictionary."""
        return {field: getattr(self, field) for field in self.__dataclass_fields__}


class SimulationResults(NamedTuple):
    """Container for processed simulation results."""

    time_vector: List[float]
    batt_values: List[float]
    batt_recharge: List[float]
    ev_recharge: List[float]
    grid_request: List[float]
    vehicle1_battery_level: List[float]
    vehicle2_battery_level: List[float]
    vehicle3_battery_level: List[float]
    vehicle4_battery_level: List[float]

    @property
    def data_length(self) -> int:
        """Returns the length of the time vector."""
        return len(self.time_vector) if self.time_vector else 0


# --- Helper Functions ---
def _handle_exception(exc: Exception, message: str) -> None:
    """Helper function to log exceptions."""
    logger.error(f"{message}: {exc}")
    if logging.getLogger().level <= logging.DEBUG:
        logger.exception("Detailed traceback:")


# --- Main Classes ---
class ResultsParser:
    """Responsible for parsing and extracting data from MATLAB simulation results."""

    @staticmethod
    def extract_time_vector(
        result: Dict[str, Any], time_key: str = "Batt"
    ) -> Optional[List[float]]:
        """
        Extracts the time vector from the result, assuming it's present and consistent.

        Args:
            result: The raw simulation results dictionary from MATLAB
            time_key: Key in results that contains the time vector

        Returns:
            List of time values or None if extraction fails
        """
        if (
            time_key not in result
            or not isinstance(result[time_key], dict)
            or "Time" not in result[time_key]
        ):
            logger.warning(f"Could not find time vector using key '{time_key}'.")
            return None

        time_data = result[time_key]["Time"]
        extracted_times = []
        try:
            # Check if time_data is iterable and not empty
            if not hasattr(time_data, "__iter__"):
                raise ValueError("Time data is not iterable")

            if not time_data:
                logger.warning(f"Time vector for key '{time_key}' is empty.")
                return []  # Return empty list

            # Extract all data points
            for item in time_data:
                # Check if item is indexable and has at least one element
                if not hasattr(item, "__getitem__") or len(item) < 1:
                    raise ValueError(f"Invalid item format in time data: {item}")
                # Try converting the first element to float
                extracted_times.append(float(item[0]))
                
            logger.info(f"Extracted {len(extracted_times)} time points")
            return extracted_times

        except (TypeError, ValueError, IndexError) as e:
            logger.warning(
                f"Unexpected format or error processing time vector for key '{time_key}'. "
                f"Data: {time_data}. Error: {e}"
            )
            return None

    @staticmethod
    def extract_data_from_result(
        result: Dict[str, Any], key: str, expected_length: Optional[int] = None
    ) -> Optional[List[float]]:
        """
        Safely extracts time series data from the MATLAB result structure.

        Args:
            result: The raw simulation results dictionary from MATLAB
            key: The key to extract data for
            expected_length: Expected length of the output data list

        Returns:
            List of data values or None if extraction fails
        """
        if key not in result:
            logger.warning(f"Key '{key}' not found in result.")
            return None

        data_item = result[key]

        if isinstance(data_item, dict) and "Data" in data_item:
            data_list = data_item["Data"]
            extracted_data = []
            try:
                # Check if data_list is iterable
                if not hasattr(data_list, "__iter__"):
                    raise ValueError("Data list is not iterable")

                # Allow empty list if expected_length is 0 or None initially
                if not data_list and expected_length is not None and expected_length > 0:
                    raise ValueError("Data list is unexpectedly empty")

                # Process all data points
                for item in data_list:
                    # Check if item is indexable and has at least one element
                    if not hasattr(item, "__getitem__") or len(item) < 1:
                        raise ValueError(
                            f"Invalid item format in data list for key '{key}': {item}"
                        )
                    # Try converting the first element to float
                    extracted_data.append(float(item[0]))

                logger.info(f"Extracted {len(extracted_data)} data points for key '{key}'")

                # Check length after successful extraction
                if expected_length is not None and len(extracted_data) != expected_length:
                    logger.warning(
                        f"Data length mismatch for key '{key}'. Expected {expected_length}, "
                        f"got {len(extracted_data)}."
                    )
                    # Pad or truncate with NaNs to match expected length
                    if len(extracted_data) < expected_length:
                        extracted_data.extend(
                            [float("nan")] * (expected_length - len(extracted_data))
                        )
                    else:
                        extracted_data = extracted_data[:expected_length]  # Truncate if too long

                return extracted_data

            except (TypeError, ValueError, IndexError) as e:
                logger.warning(
                    f"Unexpected format or error processing data for key '{key}'. "
                    f"Data: {data_list}. Error: {e}"
                )
                # Return NaNs of expected length if extraction fails and length is known
                return (
                    [float("nan")] * expected_length
                    if expected_length is not None
                    else None
                )

        elif isinstance(data_item, (int, float)):  # Handle single value case
            logger.warning(
                f"Key '{key}' returned a single value, not time series. Value: {data_item}"
            )
            # Cannot determine length, return None
            return None

        else:  # Handle other unexpected types
            logger.warning(
                f"Unexpected data type or structure for key '{key}'. Type: {type(data_item)}"
            )
            # Return NaNs of expected length if known
            return [float("nan")] * expected_length if expected_length is not None else None

    @staticmethod
    def _filter_zero_datapoints(
        time_vector: List[float],
        batt_values: List[float],
        batt_recharge: List[float],
        ev_recharge: List[float],
        grid_request: List[float],
        vehicle1_battery_level: List[float],
        vehicle2_battery_level: List[float],
        vehicle3_battery_level: List[float],
        vehicle4_battery_level: List[float],
    ) -> Tuple[List[float], List[float], List[float], List[float], List[float], 
               List[float], List[float], List[float], List[float]]:
        """
        Filters out simulation startup artifacts and meaningless data points.
        
        This method removes:
        1. Time points where all activity values (non-state values) are zero
        2. Early time points (t=0, t=1) that represent simulation initialization
           when no meaningful activity is occurring
        
        Args:
            time_vector: Time points
            All data series as separate lists
            
        Returns:
            Tuple of filtered lists (time_vector, all data series)
        """
        if not time_vector:
            return ([], [], [], [], [], [], [], [], [])
            
        # Create lists to store filtered data
        filtered_time = []
        filtered_batt = []
        filtered_batt_recharge = []
        filtered_ev_recharge = []
        filtered_grid_request = []
        filtered_vehicle1 = []
        filtered_vehicle2 = []
        filtered_vehicle3 = []
        filtered_vehicle4 = []
        
        zero_points_removed = 0
        
        # Check each data point
        for i in range(len(time_vector)):
            time_val = time_vector[i]
            
            # Get activity values (values that indicate actual system activity)
            # These exclude static state values like initial battery levels
            activity_values = [
                batt_recharge[i] if i < len(batt_recharge) else 0,
                ev_recharge[i] if i < len(ev_recharge) else 0,
                grid_request[i] if i < len(grid_request) else 0,
            ]
            
            # Get all data values for complete check
            all_data_values = [
                batt_values[i] if i < len(batt_values) else 0,
                batt_recharge[i] if i < len(batt_recharge) else 0,
                ev_recharge[i] if i < len(ev_recharge) else 0,
                grid_request[i] if i < len(grid_request) else 0,
                vehicle1_battery_level[i] if i < len(vehicle1_battery_level) else 0,
                vehicle2_battery_level[i] if i < len(vehicle2_battery_level) else 0,
                vehicle3_battery_level[i] if i < len(vehicle3_battery_level) else 0,
                vehicle4_battery_level[i] if i < len(vehicle4_battery_level) else 0,
            ]
            
            # Filtering logic:
            # 1. Always keep if time > 1.0 (meaningful simulation time)
            # 2. For t <= 1.0, filter out if no meaningful activity is occurring
            should_keep = True
            
            if time_val <= 1.0:  # Early simulation time
                # Check if there's any meaningful activity
                has_activity = any(abs(value) > 1e-10 for value in activity_values 
                                 if not (isinstance(value, float) and value != value))  # Exclude NaN
                
                # Also check if ALL values are zero (original strict condition)
                all_zero = all(abs(value) < 1e-10 for value in all_data_values 
                             if not (isinstance(value, float) and value != value))  # Exclude NaN
                
                # Filter out if no activity AND (all zero OR just initialization)
                if not has_activity or all_zero:
                    should_keep = False
            
            if should_keep:
                # Keep this data point
                filtered_time.append(time_vector[i])
                filtered_batt.append(batt_values[i] if i < len(batt_values) else float("nan"))
                filtered_batt_recharge.append(batt_recharge[i] if i < len(batt_recharge) else float("nan"))
                filtered_ev_recharge.append(ev_recharge[i] if i < len(ev_recharge) else float("nan"))
                filtered_grid_request.append(grid_request[i] if i < len(grid_request) else float("nan"))
                filtered_vehicle1.append(vehicle1_battery_level[i] if i < len(vehicle1_battery_level) else float("nan"))
                filtered_vehicle2.append(vehicle2_battery_level[i] if i < len(vehicle2_battery_level) else float("nan"))
                filtered_vehicle3.append(vehicle3_battery_level[i] if i < len(vehicle3_battery_level) else float("nan"))
                filtered_vehicle4.append(vehicle4_battery_level[i] if i < len(vehicle4_battery_level) else float("nan"))
            else:
                zero_points_removed += 1
        
        if zero_points_removed > 0:
            logger.info(f"Filtered out {zero_points_removed} startup/inactive data points")
        
        return (
            filtered_time, filtered_batt, filtered_batt_recharge, 
            filtered_ev_recharge, filtered_grid_request, filtered_vehicle1,
            filtered_vehicle2, filtered_vehicle3, filtered_vehicle4
        )

    @classmethod
    def parse_simulation_results(
        cls, raw_results: Dict[str, Any]
    ) -> Optional[SimulationResults]:
        """
        Parses the raw simulation results into a structured SimulationResults object.

        Args:
            raw_results: Raw simulation results from MATLAB

        Returns:
            SimulationResults object or None if parsing fails
        """
        if not raw_results:
            logger.error("Cannot parse empty results")
            return None

        try:
            # Extract time vector first
            time_vector = cls.extract_time_vector(raw_results)
            if time_vector is None:
                logger.error("Failed to extract time vector from results")
                return None

            time_len = len(time_vector)

            # Extract all required data series
            batt_values = cls.extract_data_from_result(
                raw_results, "Batt", expected_length=time_len
            ) or [float("nan")] * time_len
            batt_recharge = cls.extract_data_from_result(
                raw_results, "BattRecharge", expected_length=time_len
            ) or [float("nan")] * time_len
            ev_recharge = cls.extract_data_from_result(
                raw_results, "EVRecharge", expected_length=time_len
            ) or [float("nan")] * time_len
            grid_request = cls.extract_data_from_result(
                raw_results, "GridRequest", expected_length=time_len
            ) or [float("nan")] * time_len
            vehicle1_battery_level = cls.extract_data_from_result(
                raw_results, "Vehicle1BatteryLevel", expected_length=time_len
            ) or [float("nan")] * time_len
            vehicle2_battery_level = cls.extract_data_from_result(
                raw_results, "Vehicle2BatteryLevel", expected_length=time_len
            ) or [float("nan")] * time_len
            vehicle3_battery_level = cls.extract_data_from_result(
                raw_results, "Vehicle3BatteryLevel", expected_length=time_len
            ) or [float("nan")] * time_len
            vehicle4_battery_level = cls.extract_data_from_result(
                raw_results, "Vehicle4BatteryLevel", expected_length=time_len
            ) or [float("nan")] * time_len

            # Filter out data points where all data values are 0
            filtered_results = cls._filter_zero_datapoints(
                time_vector, batt_values, batt_recharge, ev_recharge, 
                grid_request, vehicle1_battery_level, vehicle2_battery_level,
                vehicle3_battery_level, vehicle4_battery_level
            )

            return SimulationResults(
                time_vector=filtered_results[0],
                batt_values=filtered_results[1],
                batt_recharge=filtered_results[2],
                ev_recharge=filtered_results[3],
                grid_request=filtered_results[4],
                vehicle1_battery_level=filtered_results[5],
                vehicle2_battery_level=filtered_results[6],
                vehicle3_battery_level=filtered_results[7],
                vehicle4_battery_level=filtered_results[8],
            )

        except Exception as e:
            _handle_exception(e, "Error parsing simulation results")
            return None


class SimulationManager:
    """Manages the MATLAB engine and simulation execution."""

    def __init__(self):
        """Initialize the simulation manager."""
        self.matlab_engine = None

    def start_engine(self) -> bool:
        """
        Starts the MATLAB engine and prepares it for simulation.

        Returns:
            True if engine was started successfully, False otherwise
        """
        try:
            logger.info("Starting MATLAB engine...")
            self.matlab_engine = matlab.engine.start_matlab()
            logger.info("MATLAB engine started successfully")

            # Change to the directory of this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.matlab_engine.cd(script_dir, nargout=0)
            logger.info(f"Changed MATLAB working directory to: {script_dir}")
            return True

        except Exception as e:
            _handle_exception(e, "Error starting MATLAB engine")
            self.matlab_engine = None
            return False

    def stop_engine(self) -> None:
        """Safely stops the MATLAB engine."""
        if self.matlab_engine:
            try:
                logger.info("Stopping MATLAB engine...")
                self.matlab_engine.quit()
                logger.info("MATLAB engine stopped")

            except Exception as e:
                _handle_exception(e, "Error stopping MATLAB engine")
            finally:
                self.matlab_engine = None

    def run_simulation(
        self,
        params: Union[Dict[str, Any], SimulationParameters],
        configure_for_deployment: bool = False,
        stop_time: int = SIMULATION_STOP_TIME_S,
        simulation_speed: float = DEFAULT_SIMULATION_SPEED,
    ) -> Optional[Dict[str, Any]]:
        """
        Runs the Simulink model simulation using the provided parameters.

        Args:
            params: Simulation parameters as dict or SimulationParameters object
            configure_for_deployment: Flag for configuring the model for deployment
            stop_time: Simulation time in seconds
            simulation_speed: Speed multiplier for the simulation

        Returns:
            Raw simulation results dictionary or None if simulation fails
        """
        if self.matlab_engine is None:
            logger.error("MATLAB engine not available. Cannot run simulation.")
            return None

        # Convert SimulationParameters to dict if needed
        if isinstance(params, SimulationParameters):
            params = params.to_dict()

        logger.info(f"Running simulation with speed factor: {simulation_speed}")

        try:
            # Use raw stop time directly without adjustment
            results = self.matlab_engine.sim_the_model(
                "TunableParameters",
                params,
                "ConfigureForDeployment",
                configure_for_deployment,
                "StopTime",
                stop_time,
            )
            return results

        except Exception as e:
            _handle_exception(e, "Error during simulation")
            return None

    def run_and_parse_simulation(
        self,
        params: Union[Dict[str, Any], SimulationParameters],
        configure_for_deployment: bool = False,
        stop_time: int = SIMULATION_STOP_TIME_S,
        simulation_speed: float = DEFAULT_SIMULATION_SPEED,
    ) -> Optional[SimulationResults]:
        """
        Runs the simulation and returns parsed results.

        Args:
            params: Simulation parameters as dict or SimulationParameters object
            configure_for_deployment: Flag for configuring the model for deployment
            stop_time: Simulation time in seconds
            simulation_speed: Speed multiplier for the simulation

        Returns:
            Parsed SimulationResults or None if simulation fails
        """
        raw_results = self.run_simulation(
            params, configure_for_deployment, stop_time, simulation_speed
        )

        if raw_results:
            return ResultsParser.parse_simulation_results(raw_results)
        return None


@contextmanager
def simulation_session() -> Iterator[Optional[SimulationManager]]:
    """
    Context manager for handling a simulation session.

    Yields:
        SimulationManager instance or None if engine start fails
    """
    manager = SimulationManager()
    success = manager.start_engine()

    try:
        yield manager if success else None
    finally:
        manager.stop_engine()


def print_simulation_results(results: SimulationResults) -> None:
    """
    Prints simulation results to console.

    Args:
        results: Simulation results object to print
    """
    logger.info("Simulation results:")
    print(f"Time Vector: {results.time_vector}")
    print(f"Batt: {results.batt_values}")
    print(f"BattRecharge: {results.batt_recharge}")
    print(f"EVRecharge: {results.ev_recharge}")
    print(f"GridRequest: {results.grid_request}")
    print(f"Vehicle1BatteryLevel: {results.vehicle1_battery_level}")
    print(f"Vehicle2BatteryLevel: {results.vehicle2_battery_level}")
    print(f"Vehicle3BatteryLevel: {results.vehicle3_battery_level}")
    print(f"Vehicle4BatteryLevel: {results.vehicle4_battery_level}")


def get_user_simulation_speed() -> float:
    """
    Gets simulation speed from user input.

    Returns:
        Simulation speed factor
    """
    try:
        return float(
            input(
                "Enter simulation speed factor "
                "(0.5 for slower, 1.0 for normal, 2.0 or 5.0 for faster): "
            )
            or str(DEFAULT_SIMULATION_SPEED)
        )
    except ValueError:
        logger.warning("Invalid input. Using default simulation speed.")
        return DEFAULT_SIMULATION_SPEED


# --- Main Execution ---
if __name__ == "__main__":
    try:
        # Get simulation speed from user
        simulation_speed = get_user_simulation_speed()

        # Set up default parameters
        params = SimulationParameters(
            PVOutput=10.0,  # kW per hour (DC)
            BatteryOutput=30.0,  # kW
        )

        # Run simulation with context manager
        with simulation_session() as sim_manager:
            if sim_manager is None:
                logger.error("Failed to start simulation session")
                sys.exit(1)

            # Run simulation and get parsed results
            results = sim_manager.run_and_parse_simulation(
                params=params,
                configure_for_deployment=True,
                simulation_speed=simulation_speed,
            )

            # Print results if available
            if results:
                print_simulation_results(results)
            else:
                logger.error("Simulation failed to produce results")

    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    except Exception as e:
        _handle_exception(e, "An unexpected error occurred")
        sys.exit(1)
