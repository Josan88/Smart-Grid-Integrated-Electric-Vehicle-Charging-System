import matlab.engine
import os
import sys
from typing import Dict, Any, List, Optional

# --- Constants ---
SIMULATION_STOP_TIME_S = 50


def start_matlab_engine() -> Optional[matlab.engine.MatlabEngine]:
    """Starts the MATLAB engine and changes the working directory."""
    try:
        print("Starting MATLAB engine...")
        mle = matlab.engine.start_matlab()
        print("MATLAB engine started successfully.")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        mle.cd(script_dir, nargout=0)
        print(f"Changed MATLAB working directory to: {script_dir}")
        return mle
    except Exception as e:
        print(
            f"Error starting MATLAB engine or changing directory: {e}", file=sys.stderr
        )
        return None


def run_simulation(
    mle: matlab.engine.MatlabEngine,
    params: Dict[str, Any],
    configure_for_deployment: bool = False,
    stop_time: int = SIMULATION_STOP_TIME_S,
    simulation_speed: float = 1.0,
) -> Optional[Dict[str, Any]]:
    """
    Runs the Simulink model simulation using the provided MATLAB engine and parameters.

    Args:
        mle: MATLAB engine instance
        params: Dictionary containing the input parameters for the simulation.
        configure_for_deployment: Flag for configuring the model for deployment.
        stop_time: Simulation time in seconds.
        simulation_speed: Speed multiplier for the simulation (higher values = faster simulation,
                         implemented by reducing the simulation time inversely).

    Returns:
        Dictionary containing simulation results or None if an error occurs.
    """
    if mle is None:
        print("MATLAB engine not available. Cannot run simulation.", file=sys.stderr)
        return None

    print(f"Running simulation with speed factor: {simulation_speed}")

    try:
        results = mle.sim_the_model(
            "TunableParameters",
            params,
            "ConfigureForDeployment",
            configure_for_deployment,
            "StopTime",
            stop_time * simulation_speed,
        )
        return results
    except Exception as e:
        print(f"Error during simulation: {e}", file=sys.stderr)
        return None


def stop_matlab_engine(mle: Optional[matlab.engine.MatlabEngine]):
    """Stops the MATLAB engine."""
    if mle:
        try:
            print("Stopping MATLAB engine...")
            mle.quit()
            print("MATLAB engine stopped.")
        except Exception as e:
            print(f"Error stopping MATLAB engine: {e}", file=sys.stderr)


def _extract_data_from_result(
    result: Dict[str, Any], key: str, expected_length: Optional[int] = None
) -> Optional[List[float]]:
    """Safely extracts time series data from the MATLAB result structure."""
    if key not in result:
        print(f"Warning: Key '{key}' not found in result.", file=sys.stderr)
        return None

    data_item = result[key]

    if isinstance(data_item, dict) and "Data" in data_item:
        data_list = data_item["Data"]
        extracted_data = []
        try:
            # Check if data_list is iterable (unless expected_length is 0)
            if not hasattr(data_list, "__iter__"):
                raise ValueError("Data list is not iterable")
            # Allow empty list if expected_length is 0 or None initially
            if not data_list and expected_length is not None and expected_length > 0:
                raise ValueError("Data list is unexpectedly empty")

            for item in data_list:
                # Check if item is indexable and has at least one element
                if not hasattr(item, "__getitem__") or len(item) < 1:
                    raise ValueError(
                        f"Invalid item format in data list for key '{key}': {item}"
                    )
                # Try converting the first element to float
                extracted_data.append(float(item[0]))

            # Check length after successful extraction
            if expected_length is not None and len(extracted_data) != expected_length:
                print(
                    f"Warning: Data length mismatch for key '{key}'. Expected {expected_length}, got {len(extracted_data)}.",
                    file=sys.stderr,
                )
                # Pad or truncate with NaNs to match expected length
                if len(extracted_data) < expected_length:
                    extracted_data.extend(
                        [float("nan")] * (expected_length - len(extracted_data))
                    )
                else:
                    extracted_data = extracted_data[
                        :expected_length
                    ]  # Truncate if too long
            return extracted_data

        except (TypeError, ValueError, IndexError) as e:
            print(
                f"Warning: Unexpected format or error processing data for key '{key}'. Data: {data_list}. Error: {e}",
                file=sys.stderr,
            )
            # Return NaNs of expected length if extraction fails and length is known
            return (
                [float("nan")] * expected_length
                if expected_length is not None
                else None
            )

    elif isinstance(data_item, (int, float)):  # Handle single value case
        print(
            f"Warning: Key '{key}' returned a single value, not time series. Value: {data_item}",
            file=sys.stderr,
        )
        # Cannot determine length, return None or handle as appropriate
        return None  # Or potentially [float(data_item)] * expected_length if that makes sense
    else:  # Handle other unexpected types
        print(
            f"Warning: Unexpected data type or structure for key '{key}'. Type: {type(data_item)}",
            file=sys.stderr,
        )
        # Return NaNs of expected length if known
        return [float("nan")] * expected_length if expected_length is not None else None


def _extract_time_vector(
    result: Dict[str, Any], time_key: str = "Batt"
) -> Optional[List[float]]:
    """Extracts the time vector from the result, assuming it's present and consistent."""
    if (
        time_key not in result
        or not isinstance(result[time_key], dict)
        or "Time" not in result[time_key]
    ):
        print(
            f"Warning: Could not find time vector using key '{time_key}'.",
            file=sys.stderr,
        )
        return None

    time_data = result[time_key]["Time"]
    extracted_times = []
    try:
        # Check if time_data is iterable and not empty
        if not hasattr(time_data, "__iter__"):
            raise ValueError("Time data is not iterable")
        if not time_data:
            # Allow empty time vector? Or raise error? Let's allow it for now.
            print(
                f"Warning: Time vector for key '{time_key}' is empty.", file=sys.stderr
            )
            return []  # Return empty list

        for item in time_data:
            # Check if item is indexable and has at least one element
            if not hasattr(item, "__getitem__") or len(item) < 1:
                raise ValueError(f"Invalid item format in time data: {item}")
            # Try converting the first element to float
            extracted_times.append(float(item[0]))
        return extracted_times
    except (TypeError, ValueError, IndexError) as e:
        print(
            f"Warning: Unexpected format or error processing time vector for key '{time_key}'. Data: {time_data}. Error: {e}",
            file=sys.stderr,
        )
        return None


if __name__ == "__main__":
    # Example usage
    matlab_engine = start_matlab_engine()
    try:
        # Example parameters for the simulation
        params = {
            "bay1_occupied": 0.0,  # boolean
            "bay2_occupied": 0.0,  # boolean
            "bay3_occupied": 0.0,  # boolean
            "bay4_occupied": 0.0,  # boolean
            "bay1_percentage": 0.0,  # percentage
            "bay2_percentage": 0.0,  # percentage
            "bay3_percentage": 0.0,  # percentage
            "bay4_percentage": 0.0,  # percentage
            "PVOutput": 10.0,  # kW per hour (DC)
            "battery_soc": 0.0,  # percentage
            "GridPeak": 0.0,  # boolean,
            "BatteryOutput": 30.0,  # kW
        }

        # Get simulation speed (defaults to 1.0)
        simulation_speed = float(
            input(
                "Enter simulation speed factor (0.5 for slower, 1.0 for normal, 2.0 or 5.0 for faster): "
            )
            or "1.0"
        )

        # Run the simulation with the specified speed
        results = run_simulation(
            matlab_engine,
            params,
            configure_for_deployment=True,
            simulation_speed=simulation_speed,
        )

        if results:
            # Extract time vector and data
            time_vector = _extract_time_vector(results)
            Batt = _extract_data_from_result(
                results,
                "Batt",
                expected_length=len(time_vector),
            )
            BattRecharge = _extract_data_from_result(
                results,
                "BattRecharge",
                expected_length=len(time_vector),
            )
            EVRecharge = _extract_data_from_result(
                results,
                "EVRecharge",
                expected_length=len(time_vector),
            )
            GridRequest = _extract_data_from_result(
                results,
                "GridRequest",
                expected_length=len(time_vector),
            )
            Vehicle1BatteryLevel = _extract_data_from_result(
                results,
                "Vehicle1BatteryLevel",
                expected_length=len(time_vector),
            )
            Vehicle2BatteryLevel = _extract_data_from_result(
                results,
                "Vehicle2BatteryLevel",
                expected_length=len(time_vector),
            )
            Vehicle3BatteryLevel = _extract_data_from_result(
                results,
                "Vehicle3BatteryLevel",
                expected_length=len(time_vector),
            )
            Vehicle4BatteryLevel = _extract_data_from_result(
                results,
                "Vehicle4BatteryLevel",
                expected_length=len(time_vector),
            )

            # Print or process the results as needed
            print("Simulation results:")
            print(f"Time Vector: {time_vector}")
            print(f"Batt: {Batt}")
            print(f"BattRecharge: {BattRecharge}")
            print(f"EVRecharge: {EVRecharge}")
            print(f"GridRequest: {GridRequest}")
            print(f"Vehicle1BatteryLevel: {Vehicle1BatteryLevel}")
            print(f"Vehicle2BatteryLevel: {Vehicle2BatteryLevel}")
            print(f"Vehicle3BatteryLevel: {Vehicle3BatteryLevel}")
            print(f"Vehicle4BatteryLevel: {Vehicle4BatteryLevel}")

    except KeyboardInterrupt:
        print("Simulation interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
    finally:
        # Stop the MATLAB engine
        stop_matlab_engine(matlab_engine)
        matlab_engine = None
