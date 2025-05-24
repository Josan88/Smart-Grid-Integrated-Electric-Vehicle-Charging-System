"""
Web application for MATLAB simulation dashboard with PVWatts integration.
"""

import json
import os
import random
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Tuple

# Try to import numpy, but make it optional
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Try to import eventlet
try:
    import eventlet

    eventlet.monkey_patch()
    HAS_EVENTLET = True
except ImportError:
    HAS_EVENTLET = False

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import pvwatts
from simulation import (
    SimulationManager,
    SimulationParameters,
    SimulationResults,
    SIMULATION_STOP_TIME_S,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("simulation_app")

# Initialize Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "simulation-dashboard-secret-key"
# Ensure SocketIO async_mode is compatible with threading if not using eventlet/gevent
if HAS_EVENTLET:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
elif False:  # Placeholder if gevent were an option
    # socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')
    pass
else:
    # Default to threading-based if eventlet (or gevent) is not available
    # This might be less performant for many concurrent connections but works generally.
    socketio = SocketIO(app, cors_allowed_origins="*")

# Downsampling settings
ENABLE_DOWNSAMPLING = True  # Set to False to always send full data
DOWNSAMPLING_THRESHOLD = 1000  # Number of data points before downsampling
DOWNSAMPLING_TARGET = 200  # Target number of data points after downsampling

# Global variables for simulation
simulation_manager = None
simulation_thread = None
simulation_running = False
simulation_lock = threading.Lock()

# Global variables for data
current_simulation_params = SimulationParameters()
current_pvwatts_settings = {
    # Required parameters
    "api_key": "YAwml3YOnwIHYekjGfahs7hSVx4iI0gDtTxlvwCu",
    "system_capacity": 26.02,
    "module_type": 0,
    "losses": 14.0,
    "array_type": 1,
    "lat": 1.532498597850374,
    "lon": 110.35732724037013,
    "tilt": 20.0,
    "azimuth": 180.0,
    # Optional parameters
    "dc_ac_ratio": 1.2,
    "gcr": 0.4,
    "inv_eff": 96.0,
    "radius": 100,
    "dataset": "nsrdb",
    "albedo": None,  # None means use default/auto
    "bifaciality": None,  # None means not applicable (non-bifacial)
}

# DC Watts data from PVWatts
hourly_dc_watts = []
current_dc_hour_index = 0
last_pv_update_hour = -1  # Track the last hour when PV output was updated

# Simulation state
simulation_datetime = datetime(2020, 1, 1, 0, 0, 0)  # Start from January 1, 2020
total_simulation_seconds = 0

# WebSocket optimization settings
WEBSOCKET_THROTTLE_MS = 100  # Minimum time between messages in milliseconds
last_websocket_message_time = 0  # Last time a message was sent

# Simulation speed control
# Base delay between points (in seconds). 1.0 means 1 simulation second per real second at 1x speed.
BASE_POINT_DELAY_S = 1.0
current_simulation_speed_multiplier = 1.0  # Default speed


def load_pvwatts_dc_data():
    """Load PVWatts DC data from the cached response file."""
    global hourly_dc_watts

    try:
        if os.path.exists("pvwatts_response.json"):
            with open("pvwatts_response.json", "r") as f:
                data = json.load(f)

            if "outputs" in data and "dc" in data["outputs"]:
                hourly_dc_watts = data["outputs"]["dc"]
                logger.info(
                    f"Loaded {len(hourly_dc_watts)} hourly DC watts values from cached PVWatts data"
                )
            else:
                logger.warning("No DC data found in PVWatts response")
                # Generate some dummy data if no real data available
                hourly_dc_watts = [random.uniform(5000, 15000) for _ in range(8760)]
        else:
            logger.warning("No PVWatts response file found. Will fetch new data.")
            update_pvwatts_data()
    except Exception as e:
        logger.error(f"Error loading PVWatts data: {e}")
        hourly_dc_watts = [random.uniform(5000, 15000) for _ in range(8760)]


def update_pvwatts_data():
    """Fetch new PVWatts data with current settings."""
    global hourly_dc_watts, current_pvwatts_settings

    logger.info("Fetching new PVWatts data...")

    try:        # Call the PVWatts API with all parameters
        response = pvwatts.get_pvwatts_data(
            api_key=current_pvwatts_settings["api_key"],
            system_capacity=current_pvwatts_settings["system_capacity"],
            module_type=current_pvwatts_settings["module_type"],
            losses=current_pvwatts_settings["losses"],
            array_type=current_pvwatts_settings["array_type"],
            lat=current_pvwatts_settings["lat"],
            lon=current_pvwatts_settings["lon"],
            tilt=current_pvwatts_settings["tilt"],
            azimuth=current_pvwatts_settings["azimuth"],
            # Optional parameters
            dc_ac_ratio=current_pvwatts_settings.get("dc_ac_ratio"),
            gcr=current_pvwatts_settings.get("gcr"),
            inv_eff=current_pvwatts_settings.get("inv_eff"),
            radius=current_pvwatts_settings.get("radius"),
            dataset=current_pvwatts_settings.get("dataset"),
            albedo=current_pvwatts_settings.get("albedo"),
            bifaciality=current_pvwatts_settings.get("bifaciality"),
        )

        if response and "outputs" in response and "dc" in response["outputs"]:
            hourly_dc_watts = response["outputs"]["dc"]
            logger.info(
                f"Successfully fetched {len(hourly_dc_watts)} hourly DC watts values"
            )

            # Notify clients about the update
            socketio.emit(
                "pvwatts_updated",
                {
                    "success": True,
                    "message": "PVWatts data updated successfully",
                    "settings": current_pvwatts_settings,
                },
            )
            return True
        else:
            logger.error("Failed to get valid PVWatts data")
            socketio.emit(
                "pvwatts_updated",
                {"success": False, "message": "Failed to get valid PVWatts data"},
            )
            return False

    except Exception as e:
        logger.error(f"Error updating PVWatts data: {e}")
        socketio.emit(
            "pvwatts_updated", {"success": False, "message": f"Error: {str(e)}"}
        )
        return False


def get_current_dc_watts() -> float:
    """Get the current DC watts for the simulation based on the current hour."""
    global hourly_dc_watts, current_dc_hour_index

    if not hourly_dc_watts:
        # Attempt to load if empty, might happen if accessed before initial load completes
        load_pvwatts_dc_data()
        if not hourly_dc_watts:  # Still no data
            logger.warning(
                "hourly_dc_watts is empty, returning 0.0 for get_current_dc_watts"
            )
            return 0.0

    # Get base value from the current hour
    base_dc_watts = hourly_dc_watts[
        current_dc_hour_index % len(hourly_dc_watts)
    ]  # Added modulo for safety

    # Add some random noise (±5% of the value)
    noise_factor = random.uniform(0.95, 1.05)
    dc_watts = base_dc_watts * noise_factor

    return dc_watts


def initialize_simulation(force_restart=False):
    """Initialize the MATLAB simulation engine.
    If already initialized and force_restart is False, does nothing.
    """
    global simulation_manager

    if simulation_manager is not None and not force_restart:
        # TODO: Add a more robust check here to see if the engine is truly responsive/healthy.
        # For now, we assume if simulation_manager exists, it's usable.
        logger.info(
            "MATLAB simulation engine already initialized and not forcing restart."
        )
        return True

    if (
        simulation_manager is not None
    ):  # Implies force_restart is True or it's the first call after a failed init
        logger.info("Stopping existing MATLAB engine for re-initialization...")
        try:
            simulation_manager.stop_engine()
            logger.info("Existing MATLAB engine stopped.")
        except Exception as e:
            logger.error(f"Error stopping existing MATLAB engine: {e}", exc_info=True)
            # Continue to try and start a new one regardless

    logger.info("Attempting to start new MATLAB simulation engine...")
    simulation_manager = SimulationManager()
    success = simulation_manager.start_engine()

    if success:
        logger.info("MATLAB simulation engine started successfully.")
    else:
        logger.error("Failed to start MATLAB simulation engine.")
        simulation_manager = None  # Ensure it's None if start failed
    return success


def start_simulation_thread():
    """Start a new simulation thread if one is not already running."""
    global simulation_thread, simulation_running, simulation_datetime, total_simulation_seconds, current_dc_hour_index, last_pv_update_hour

    with simulation_lock:
        if simulation_thread is not None and simulation_thread.is_alive():
            logger.warning("Simulation already running")
            return False

        # Reset PV update tracking when starting a new simulation
        last_pv_update_hour = -1

        simulation_running = True
        simulation_thread = threading.Thread(target=run_continuous_simulation)
        simulation_thread.daemon = True
        simulation_thread.start()

        logger.info(
            f"Started new simulation thread (effective start datetime: {simulation_datetime.strftime('%Y-%m-%d %H:%M:%S')}, initial total_seconds: {total_simulation_seconds}, initial hour_index: {current_dc_hour_index})"
        )
        return True


def stop_simulation_thread():
    """Stop the running simulation thread."""
    global simulation_running

    with simulation_lock:
        simulation_running = False

    logger.info("Requested simulation thread to stop")
    return True


def run_continuous_simulation():
    """Run simulation continuously, sending data point by point."""
    global simulation_running, simulation_manager, current_simulation_params
    global simulation_datetime, total_simulation_seconds, current_dc_hour_index, last_pv_update_hour  # Make sure current_dc_hour_index is global here
    global last_websocket_message_time

    logger.info("Starting continuous simulation loop with point-by-point data emission")

    try:
        while simulation_running:
            # Update current_dc_hour_index based on the current simulation_datetime for the batch
            day_of_year = simulation_datetime.timetuple().tm_yday
            hour_of_day = simulation_datetime.hour
            calculated_idx = (day_of_year - 1) * 24 + hour_of_day

            temp_current_dc_hour_index = 0
            if hourly_dc_watts:  # Should be loaded
                temp_current_dc_hour_index = calculated_idx % len(hourly_dc_watts)
            else:
                logger.warning(
                    "hourly_dc_watts not available in run_continuous_simulation for current_dc_hour_index."
                )
                # temp_current_dc_hour_index remains 0 as fallback

            if temp_current_dc_hour_index != current_dc_hour_index:
                logger.debug(
                    f"Updating current_dc_hour_index from {current_dc_hour_index} to {temp_current_dc_hour_index} for batch starting at {simulation_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            current_dc_hour_index = (
                temp_current_dc_hour_index  # Update global for get_current_dc_watts()
            )

            loop_start_total_seconds = total_simulation_seconds
            batch_start_datetime_for_points = simulation_datetime

            # Update the PV output only when the hour changes (not every 50 seconds)
            current_hour = batch_start_datetime_for_points.hour
            if current_hour != last_pv_update_hour:
                # Hour has changed, update PV output
                dc_watts_current_hour_avg = get_current_dc_watts()
                pv_output_watts_actual = dc_watts_current_hour_avg * random.uniform(
                    0.95, 1.05
                )
                pv_output_kw_for_simulink = pv_output_watts_actual / 1000.0

                with simulation_lock:
                    current_simulation_params.PVOutput = max(
                        0.01, pv_output_kw_for_simulink
                    )

                last_pv_update_hour = current_hour
                logger.info(
                    f"Updated PV output to {pv_output_kw_for_simulink:.2f} kW for hour {current_hour}"
                )

            # Update grid peak status (can be updated every batch as it's based on time of day)
            is_grid_peak = 8 <= current_hour < 22
            with simulation_lock:
                current_simulation_params.GridPeak = 1.0 if is_grid_peak else 0.0

            results = run_single_simulation_batch()

            if results and results.time_vector:
                # Send each data point individually
                for i in range(len(results.time_vector)):
                    if not simulation_running:
                        break

                    abs_time_for_point = (
                        loop_start_total_seconds + results.time_vector[i]
                    )
                    current_point_datetime = (
                        batch_start_datetime_for_points
                        + timedelta(seconds=results.time_vector[i])
                    )

                    data_point = {
                        "time_abs": abs_time_for_point,
                        "time_rel": results.time_vector[i],
                        "batt_value": (
                            results.batt_values[i] if results.batt_values else None
                        ),
                        "batt_recharge": (
                            results.batt_recharge[i] if results.batt_recharge else None
                        ),
                        "ev_recharge": (
                            results.ev_recharge[i] if results.ev_recharge else None
                        ),
                        "grid_request": (
                            results.grid_request[i] if results.grid_request else None
                        ),
                        "vehicle1_battery_level": (
                            results.vehicle1_battery_level[i]
                            if results.vehicle1_battery_level
                            else None
                        ),
                        "vehicle2_battery_level": (
                            results.vehicle2_battery_level[i]
                            if results.vehicle2_battery_level
                            else None
                        ),
                        "vehicle3_battery_level": (
                            results.vehicle3_battery_level[i]
                            if results.vehicle3_battery_level
                            else None
                        ),
                        "vehicle4_battery_level": (
                            results.vehicle4_battery_level[i]
                            if results.vehicle4_battery_level
                            else None
                        ),                        "pv_output_watts": pv_output_watts_actual,
                        "date": current_point_datetime.strftime("%Y-%m-%d"),
                        "time": current_point_datetime.strftime("%H:%M:%S"),
                        "is_grid_peak": is_grid_peak,
                        "grid_peak_status": "Peak" if is_grid_peak else "Off-Peak",
                    }
                    socketio.emit("new_simulation_point", data_point)

                    # Calculate delay based on current speed multiplier
                    # A higher multiplier means a shorter delay (faster simulation)
                    delay_s = BASE_POINT_DELAY_S / current_simulation_speed_multiplier
                    socketio.sleep(delay_s)
                # After processing all points in the batch, update the system's battery SOC
                # for the next iteration or a new simulation start.
                if results.batt_values and len(results.batt_values) > 0:
                    final_soc_from_batch = results.batt_values[-1]
                    with simulation_lock:
                        # We store the latest SOC value for simulation continuity,
                        # but we don't overwrite user-set values during parameter updates
                        # This allows the user's SOC setting to take effect when applying changes
                        if (
                            not hasattr(
                                current_simulation_params, "_user_set_battery_soc"
                            )
                            or not current_simulation_params._user_set_battery_soc
                        ):
                            current_simulation_params.battery_soc = final_soc_from_batch
                            logger.info(
                                f"Updated current_simulation_params.battery_soc to {final_soc_from_batch:.2f}% for next batch/simulation."
                            )

            if not simulation_running:  # Exit loop if stop was requested
                break

            # Advance simulation time for the next batch
            simulation_datetime += timedelta(seconds=SIMULATION_STOP_TIME_S)
            total_simulation_seconds += SIMULATION_STOP_TIME_S

            hour_increments = (total_simulation_seconds // 3600) - (
                current_dc_hour_index
            )
            if hour_increments > 0:
                current_dc_hour_index = (current_dc_hour_index + hour_increments) % len(
                    hourly_dc_watts
                )
                logger.info(
                    f"Advanced to hour index {current_dc_hour_index} (Date: {simulation_datetime.strftime('%Y-%m-%d %H:%M:%S')})"
                )

            # Notify clients about the overall simulation time advancement (throttled)
            # This event now confirms the batch completion and overall state.
            current_time_millis = int(round(time.time() * 1000))
            if (
                current_time_millis - last_websocket_message_time
                >= WEBSOCKET_THROTTLE_MS
            ):
                # simulation_datetime here is the start of the *next* batch
                # is_grid_peak was for the batch that just *completed*

                # Calculate the hour_index for the *next* period, based on the *advanced* simulation_datetime
                next_sim_datetime_for_payload = (
                    simulation_datetime  # This is already advanced
                )
                next_day_of_year = next_sim_datetime_for_payload.timetuple().tm_yday
                next_hour_of_day = next_sim_datetime_for_payload.hour
                next_dc_hour_index_for_payload = (
                    next_day_of_year - 1
                ) * 24 + next_hour_of_day

                if hourly_dc_watts:
                    next_dc_hour_index_for_payload %= len(hourly_dc_watts)
                else:
                    next_dc_hour_index_for_payload = 0  # Fallback

                socketio.emit(
                    "simulation_time_update",
                    {
                        "datetime": next_sim_datetime_for_payload.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "total_seconds": total_simulation_seconds,
                        "hour_index": next_dc_hour_index_for_payload,  # Use the newly calculated one
                        "pv_output_watts": pv_output_watts_actual,
                        "pv_output_kw_simulink": pv_output_kw_for_simulink,
                        "date": next_sim_datetime_for_payload.strftime("%Y-%m-%d"),
                        "time": next_sim_datetime_for_payload.strftime("%H:%M:%S"),
                        "is_grid_peak": is_grid_peak,
                        "grid_peak_status": "Peak" if is_grid_peak else "Off-Peak",
                    },
                )
                last_websocket_message_time = current_time_millis

    except Exception as e:
        logger.error(f"Error in simulation thread: {e}", exc_info=True)
        socketio.emit("simulation_error", {"message": str(e)})
    finally:
        with simulation_lock:
            simulation_running = False

        logger.info("Simulation thread exited")
        socketio.emit("simulation_stopped", {"message": "Simulation has stopped"})


def run_single_simulation_batch():
    """Run a single simulation batch with current parameters."""
    global simulation_manager, current_simulation_params

    if simulation_manager is None:
        logger.error("Cannot run simulation: MATLAB engine not available")
        return None

    try:
        # Make a copy of current parameters to avoid race conditions
        with simulation_lock:
            params = current_simulation_params

        # Run simulation
        start_time = time.time()
        results = simulation_manager.run_and_parse_simulation(
            params=params,
            configure_for_deployment=True,
            stop_time=SIMULATION_STOP_TIME_S,
        )
        duration = time.time() - start_time

        if results:
            logger.info(
                f"Simulation batch completed in {duration:.2f}s with {results.data_length} data points"
            )
            return results
        else:
            logger.error("Simulation batch failed")
            return None

    except Exception as e:
        logger.error(f"Error running simulation batch: {e}")
        return None


def downsample_data(
    data: Dict[str, List],
    threshold: int = DOWNSAMPLING_THRESHOLD,
    target: int = DOWNSAMPLING_TARGET,
) -> Dict[str, List]:
    """
    Downsample simulation data to reduce network traffic and improve performance.

    Args:
        data: Dictionary of time series data
        threshold: Number of points before downsampling is applied
        target: Target number of points after downsampling

    Returns:
        Downsampled data dictionary
    """
    # If data is smaller than threshold or downsampling is disabled, return as is
    if not ENABLE_DOWNSAMPLING or len(data.get("time", [])) <= threshold:
        return data

    # Compute the downsampling rate
    rate = max(1, len(data["time"]) // target)

    # Create a downsampled copy
    downsampled = {}

    # Process each list in the data dictionary
    for key, values in data.items():
        if isinstance(values, list) and len(values) > 0:
            # Select every rate-th element
            downsampled[key] = values[::rate]

    logger.info(
        f"Downsampled data from {len(data['time'])} to {len(downsampled['time'])} points"
    )
    return downsampled


def throttled_emit(event, data=None):
    """
    Throttle WebSocket emissions to avoid overwhelming the client.

    Args:
        event: The WebSocket event name
        data: The data to send

    Returns:
        bool: True if the message was sent, False if throttled
    """
    global last_websocket_message_time

    current_time = time.time() * 1000  # Convert to milliseconds
    time_since_last = current_time - last_websocket_message_time

    # If we've waited long enough, send the message
    if time_since_last >= WEBSOCKET_THROTTLE_MS:
        last_websocket_message_time = current_time
        socketio.emit(event, data)
        return True

    # Otherwise, skip this message
    return False


# Socket.IO Event Handlers (for events from client)
@socketio.on("connect")
def handle_connect():
    logger.info("Client connected")
    # Send current state (including speed) to newly connected client
    emit_current_simulation_state()


@socketio.on("disconnect")
def handle_disconnect():
    logger.info("Client disconnected")


@socketio.on("set_simulation_speed")
def handle_set_simulation_speed(data):
    global current_simulation_speed_multiplier
    try:
        speed = float(data.get("speed", 1.0))
        if speed <= 0:
            raise ValueError("Speed multiplier must be positive.")
        current_simulation_speed_multiplier = speed
        logger.info(
            f"Simulation speed multiplier set to: {current_simulation_speed_multiplier}x"
        )
        socketio.emit(
            "simulation_speed_updated",
            {
                "success": True,
                "message": f"Simulation speed set to {current_simulation_speed_multiplier}x",
                "speed": current_simulation_speed_multiplier,
            },
        )
    except Exception as e:
        logger.error(f"Error setting simulation speed: {e}")
        socketio.emit(
            "simulation_speed_updated",
            {"success": False, "message": f"Error: {str(e)}"},
        )


# Flask Routes
@app.route("/")
def index():
    """Render the main dashboard page."""
    return render_template("index.html")


# API Routes
@app.route("/api/simulation/params", methods=["GET", "POST"])
def simulation_params():
    """Get or update simulation parameters."""
    global current_simulation_params

    if request.method == "GET":
        with simulation_lock:
            return jsonify(current_simulation_params.__dict__)

    elif request.method == "POST":
        try:
            data = request.json
            with simulation_lock:
                # Update only the fields provided in the request
                for key, value in data.items():
                    if hasattr(current_simulation_params, key):
                        setattr(current_simulation_params, key, float(value))

            return jsonify(
                {
                    "success": True,
                    "message": "Parameters updated successfully",
                    "params": current_simulation_params.__dict__,
                }
            )

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error updating parameters: {str(e)}",
                    }
                ),
                400,
            )


@app.route("/api/pvwatts/settings", methods=["GET", "POST"])
def pvwatts_settings():
    """Get or update PVWatts settings."""
    global current_pvwatts_settings

    if request.method == "GET":
        return jsonify(current_pvwatts_settings)

    elif request.method == "POST":
        try:
            data = request.json            # Update settings with new values
            for key, value in data.items():
                if key in current_pvwatts_settings:
                    # Handle empty values for optional parameters
                    if value == "" or value is None:
                        if key in ["albedo", "bifaciality"]:  # Optional parameters that can be None
                            current_pvwatts_settings[key] = None
                        else:
                            continue  # Skip empty required parameters
                    # Convert to appropriate type
                    elif key in ["module_type", "array_type", "radius"]:
                        current_pvwatts_settings[key] = int(value)
                    elif key in ["api_key", "dataset"]:
                        current_pvwatts_settings[key] = str(value)
                    else:
                        current_pvwatts_settings[key] = float(value)

            # After updating, try to fetch new PVWatts data
            if update_pvwatts_data():
                return jsonify(
                    {
                        "success": True,
                        "message": "PVWatts settings updated and data re-fetched successfully",
                        "settings": current_pvwatts_settings,
                    }
                )
            else:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "PVWatts settings updated, but failed to re-fetch data. Check API key and parameters.",
                            "settings": current_pvwatts_settings,
                        }
                    ),
                    500,
                )  # Internal server error if data fetch fails

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error updating PVWatts settings: {str(e)}",
                    }
                ),
                400,
            )


@app.route("/api/simulation/control", methods=["POST"])
def simulation_control():
    """Start or stop the simulation."""  # Ensure all relevant globals are accessible
    global simulation_running, current_simulation_params, current_pvwatts_settings
    global simulation_datetime, total_simulation_seconds, current_dc_hour_index, hourly_dc_watts, last_pv_update_hour

    action = request.json.get("action")

    if action == "start":
        if not simulation_running:  # Handle user-defined start date/time
            start_date_str = request.json.get("start_date")
            start_time_str = request.json.get("start_time")
            # Lock before modifying shared global simulation time variables
            with simulation_lock:
                if start_date_str and start_time_str:
                    try:
                        # Ensure time string is in HH:MM:SS format for strptime
                        if len(start_time_str.split(":")) == 2:  # Format is HH:MM
                            start_time_str += ":00"  # Append seconds

                        user_start_datetime = datetime.strptime(
                            f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S"
                        )

                        # Update globals
                        simulation_datetime = user_start_datetime
                        total_simulation_seconds = 0  # Reset for the new logical start
                        last_pv_update_hour = (
                            -1
                        )  # Reset PV update tracking for new simulation

                        # Reset the user-set flag for battery_soc when starting a new simulation
                        # This allows simulation to update battery SOC based on simulation results
                        if hasattr(current_simulation_params, "_user_set_battery_soc"):
                            setattr(
                                current_simulation_params,
                                "_user_set_battery_soc",
                                False,
                            )
                            logger.info(
                                "Reset user-set battery SOC flag for new simulation"
                            )

                        day_of_year = simulation_datetime.timetuple().tm_yday
                        hour_of_day = simulation_datetime.hour
                        calculated_idx = (day_of_year - 1) * 24 + hour_of_day

                        if hourly_dc_watts:  # Should be loaded by now
                            current_dc_hour_index = calculated_idx % len(
                                hourly_dc_watts
                            )
                        else:
                            logger.warning(
                                "hourly_dc_watts not available for precise initial current_dc_hour_index setting during simulation start."
                            )
                            current_dc_hour_index = 0  # Fallback

                        logger.info(
                            f"Simulation starting from user-defined datetime: {simulation_datetime.strftime('%Y-%m-%d %H:%M:%S')}, initial hour index: {current_dc_hour_index}"
                        )

                    except ValueError as e:
                        logger.warning(
                            f"Could not parse user-defined start_date ('{start_date_str}') or start_time ('{start_time_str}'): {e}. Using current/default simulation time: {simulation_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                else:
                    # Reset PV update tracking even when no custom time is provided
                    last_pv_update_hour = -1
                    logger.info(
                        f"No user-defined start time provided. Simulation will start/resume from: {simulation_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
                    )

            # Proceed with initialization and starting the thread (outside the lock for these calls)
            if initialize_simulation():  # Initialize MATLAB engine if needed
                if (
                    start_simulation_thread()
                ):  # This will use the potentially updated globals
                    emit_current_simulation_state()
                    return jsonify({"success": True, "message": "Simulation started"})
                else:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "Failed to start simulation thread",
                            }
                        ),
                        500,
                    )
            else:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Failed to initialize MATLAB engine",
                        }
                    ),
                    500,
                )
        else:
            return (
                jsonify({"success": False, "message": "Simulation already running"}),
                400,
            )

    elif action == "stop":
        if simulation_running:
            if stop_simulation_thread():
                # State update will be sent by the simulation thread upon exit
                return jsonify(
                    {"success": True, "message": "Simulation stop requested"}
                )
            else:
                return (
                    jsonify({"success": False, "message": "Failed to stop simulation"}),
                    500,
                )
        else:
            return jsonify({"success": False, "message": "Simulation not running"}), 400

    return jsonify({"success": False, "message": "Invalid action"}), 400


@app.route("/api/simulation/state", methods=["GET"])
def get_simulation_state():
    """Get the current simulation state, parameters, and PVWatts settings."""
    return jsonify(get_current_simulation_state_payload())


def emit_current_simulation_state():
    """Emits the current simulation state to all clients."""
    payload = get_current_simulation_state_payload()
    socketio.emit("simulation_state", payload)


def get_current_simulation_state_payload() -> Dict[str, Any]:
    """Constructs the payload for the simulation_state event."""
    global simulation_running, current_simulation_params, current_pvwatts_settings, simulation_datetime, total_simulation_seconds, current_simulation_speed_multiplier
    with simulation_lock:
        params_dict = current_simulation_params.__dict__
        pvwatts_dict = current_pvwatts_settings
        is_running = simulation_running
        sim_dt = simulation_datetime
        total_sec = total_simulation_seconds
        speed_mult = current_simulation_speed_multiplier

    # Calculate peak status based on current simulation time
    current_hour = sim_dt.hour
    is_grid_peak = 8 <= current_hour < 22

    return {
        "running": is_running,
        "params": params_dict,
        "pvwatts": pvwatts_dict,
        "datetime": sim_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "date": sim_dt.strftime("%Y-%m-%d"),
        "time": sim_dt.strftime("%H:%M:%S"),
        "total_seconds": total_sec,
        "speed": speed_mult,  # Include current speed
        "is_grid_peak": is_grid_peak,
        "grid_peak_status": "Peak" if is_grid_peak else "Off-Peak",
    }


# WebSocket events
@socketio.on("connect")
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")

    # Send current simulation state to the new client
    with simulation_lock:
        socketio.emit(
            "simulation_state",
            {
                "running": simulation_running,
                "params": current_simulation_params.__dict__,
                "pvwatts": current_pvwatts_settings,
                "datetime": simulation_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "total_seconds": total_simulation_seconds,
                "date": simulation_datetime.strftime("%Y-%m-%d"),
                "time": simulation_datetime.strftime("%H:%M:%S"),
            },
            to=request.sid,
        )


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on("update_simulation_params")
def handle_update_params(data):
    """Handle parameter update request from client."""
    global current_simulation_params, simulation_datetime

    try:
        with simulation_lock:
            # Update parameters
            for key, value in data.items():
                if key == "initial_start_date" or key == "initial_start_time":
                    # Store the initial start date/time but don't update simulation_datetime yet
                    # This will be handled when starting the simulation
                    continue
                elif hasattr(current_simulation_params, key):
                    # Convert value to float for numeric parameters
                    setattr(current_simulation_params, key, float(value))

                    # Mark battery_soc as user-set so it doesn't get overwritten by simulation
                    if key == "battery_soc":
                        setattr(
                            current_simulation_params, "_user_set_battery_soc", True
                        )
                        logger.info(
                            f"User manually set battery_soc to {float(value):.2f}%"
                        )

        # For date parameters, store them separately for the next simulation start
        if "initial_start_date" in data and "initial_start_time" in data:
            try:
                # Parse the date/time strings (validation only, don't update simulation_datetime yet)
                start_date_str = data.get("initial_start_date")
                start_time_str = data.get("initial_start_time")

                # Ensure time string is in HH:MM:SS format
                if len(start_time_str.split(":")) == 2:
                    start_time_str += ":00"

                # Validate the datetime (but don't set it yet)
                datetime.strptime(
                    f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S"
                )
                logger.info(
                    f"Validated new start datetime: {start_date_str} {start_time_str} (will be applied on next simulation start)"
                )
            except ValueError as e:
                logger.warning(f"Invalid datetime format in parameters: {e}")

        # Acknowledge update
        socketio.emit(
            "params_updated",
            {
                "success": True,
                "message": "Parameters updated successfully",
                "params": current_simulation_params.__dict__,
            },
            to=request.sid,
        )

    except Exception as e:
        socketio.emit(
            "params_updated",
            {"success": False, "message": f"Error updating parameters: {str(e)}"},
            to=request.sid,
        )


@socketio.on("update_pvwatts_settings")
def handle_update_pvwatts(data):
    """Handle PVWatts settings update request from client."""
    global current_pvwatts_settings

    try:        # Update PVWatts settings
        for key, value in data.items():
            if key in current_pvwatts_settings:
                # Handle empty values for optional parameters
                if value == "" or value is None:
                    if key in ["albedo", "bifaciality"]:  # Optional parameters that can be None
                        current_pvwatts_settings[key] = None
                    else:
                        continue  # Skip empty required parameters
                # Convert to appropriate type
                elif key in ["module_type", "array_type", "radius"]:
                    current_pvwatts_settings[key] = int(value)
                elif key in ["api_key", "dataset"]:
                    current_pvwatts_settings[key] = str(value)
                else:
                    current_pvwatts_settings[key] = float(value)

        # Fetch new data in a background thread to avoid blocking
        def fetch_data_thread():
            success = update_pvwatts_data()

        thread = threading.Thread(target=fetch_data_thread)
        thread.daemon = True
        thread.start()

        # Acknowledge the settings update immediately
        socketio.emit(
            "pvwatts_settings_updated",
            {
                "success": True,
                "message": "Settings updated, fetching new data...",
                "settings": current_pvwatts_settings,
            },
            to=request.sid,
        )

    except Exception as e:
        socketio.emit(
            "pvwatts_settings_updated",
            {"success": False, "message": f"Error updating PVWatts settings: {str(e)}"},
            to=request.sid,
        )


# --- Application Startup Logic ---
load_pvwatts_dc_data()  # Ensure PVWatts data is loaded early

logger.info("Attempting to pre-initialize MATLAB engine...")
if (
    initialize_simulation()
):  # Initialize engine (won't force restart if already somehow initialized)
    logger.info("MATLAB engine initialized successfully.")

    # Run the first simulation immediately after startup
    logger.info(
        "Starting first simulation automatically without waiting for web interface..."
    )
    try:
        # Set simulation date and related globals with a lock to avoid race conditions
        with simulation_lock:
            simulation_datetime = datetime(
                2020, 1, 1, 0, 0, 0
            )  # Start from January 1, 2020
            total_simulation_seconds = 0

            # Calculate the hour index based on the simulation date
            day_of_year = simulation_datetime.timetuple().tm_yday
            hour_of_day = simulation_datetime.hour
            calculated_idx = (day_of_year - 1) * 24 + hour_of_day

            # Set the current hour index for PVWatts data
            if hourly_dc_watts:
                current_dc_hour_index = calculated_idx % len(hourly_dc_watts)
            else:
                current_dc_hour_index = 0

            # Reset user-set flags for battery SOC
            if hasattr(current_simulation_params, "_user_set_battery_soc"):
                delattr(current_simulation_params, "_user_set_battery_soc")

        # Start the simulation thread
        if start_simulation_thread():
            logger.info("First simulation started automatically")
        else:
            logger.warning("Could not start first simulation automatically")
    except Exception as e:
        logger.error(f"Error starting first simulation: {e}", exc_info=True)
else:
    logger.error(
        "Failed to initialize MATLAB engine at startup. System may experience pauses during first user simulation."
    )
# --- End Application Startup Logic ---

if __name__ == "__main__":
    logger.info("Starting Flask-SocketIO server...")
    # Use eventlet if available and patched, otherwise fall back to Flask's default dev server (Werkzeug)
    if HAS_EVENTLET:
        socketio.run(app, debug=True, host="0.0.0.0", port=5000)
    else:
        logger.warning(
            "Eventlet not available. Running with Flask's default development server (Werkzeug)."
        )
        logger.warning(
            "For production or better WebSocket performance, consider installing eventlet or gevent."
        )
        socketio.run(
            app, debug=True, host="0.0.0.0", port=5000
        )  # Werkzeug might not be ideal for socketio production
