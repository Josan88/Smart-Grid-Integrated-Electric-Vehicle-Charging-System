#!/usr/bin/env python3
"""
Detailed analysis script to examine zero-filtering behavior.
This will show exactly which time points get filtered and why.
"""

import logging
import sys
from simulation import SimulationParameters, simulation_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("detailed_analysis")

def analyze_filtering_behavior():
    """Detailed analysis of what gets filtered and why."""
    
    # Test with the problematic parameter set
    params = SimulationParameters(
        bay1_occupied=1.0,
        bay2_occupied=1.0,
        bay1_percentage=50.0,
        bay2_percentage=75.0,
        PVOutput=10.0,
        BatteryOutput=30.0,
    )
    
    with simulation_session() as sim_manager:
        if sim_manager is None:
            logger.error("Failed to start simulation session")
            return
            
        logger.info("Running simulation with EV charging parameters...")
        results = sim_manager.run_and_parse_simulation(
            params=params,
            configure_for_deployment=True,
            stop_time=50,
        )
        
        if not results:
            logger.error("Simulation failed")
            return
            
        logger.info(f"Results contain {results.data_length} data points")
        logger.info(f"Time range: {results.time_vector[0]} to {results.time_vector[-1]}")
        
        # Analyze the first 10 time points in detail
        logger.info("\nDetailed analysis of first 10 time points:")
        logger.info("Time\tBatt\tBattRech\tEVRech\tGridReq\tV1Batt\tV2Batt\tV3Batt\tV4Batt\tAllZero?")
        logger.info("-" * 100)
        
        for i in range(min(10, len(results.time_vector))):
            time_val = results.time_vector[i]
            batt = results.batt_values[i] if i < len(results.batt_values) else 0
            batt_rech = results.batt_recharge[i] if i < len(results.batt_recharge) else 0
            ev_rech = results.ev_recharge[i] if i < len(results.ev_recharge) else 0
            grid_req = results.grid_request[i] if i < len(results.grid_request) else 0
            v1_batt = results.vehicle1_battery_level[i] if i < len(results.vehicle1_battery_level) else 0
            v2_batt = results.vehicle2_battery_level[i] if i < len(results.vehicle2_battery_level) else 0
            v3_batt = results.vehicle3_battery_level[i] if i < len(results.vehicle3_battery_level) else 0
            v4_batt = results.vehicle4_battery_level[i] if i < len(results.vehicle4_battery_level) else 0
            
            # Check if all values are zero
            data_values = [batt, batt_rech, ev_rech, grid_req, v1_batt, v2_batt, v3_batt, v4_batt]
            all_zero = all(abs(value) < 1e-10 for value in data_values if not (isinstance(value, float) and value != value))
            
            logger.info(f"{time_val:.1f}\t{batt:.3f}\t{batt_rech:.3f}\t{ev_rech:.3f}\t{grid_req:.3f}\t{v1_batt:.3f}\t{v2_batt:.3f}\t{v3_batt:.3f}\t{v4_batt:.3f}\t{all_zero}")
        
        # Check if there are any completely zero time points
        logger.info("\nLooking for time points where ALL values are zero:")
        zero_points_found = 0
        for i in range(len(results.time_vector)):
            time_val = results.time_vector[i]
            batt = results.batt_values[i] if i < len(results.batt_values) else 0
            batt_rech = results.batt_recharge[i] if i < len(results.batt_recharge) else 0
            ev_rech = results.ev_recharge[i] if i < len(results.ev_recharge) else 0
            grid_req = results.grid_request[i] if i < len(results.grid_request) else 0
            v1_batt = results.vehicle1_battery_level[i] if i < len(results.vehicle1_battery_level) else 0
            v2_batt = results.vehicle2_battery_level[i] if i < len(results.vehicle2_battery_level) else 0
            v3_batt = results.vehicle3_battery_level[i] if i < len(results.vehicle3_battery_level) else 0
            v4_batt = results.vehicle4_battery_level[i] if i < len(results.vehicle4_battery_level) else 0
            
            data_values = [batt, batt_rech, ev_rech, grid_req, v1_batt, v2_batt, v3_batt, v4_batt]
            all_zero = all(abs(value) < 1e-10 for value in data_values if not (isinstance(value, float) and value != value))
            
            if all_zero:
                zero_points_found += 1
                logger.info(f"  Time {time_val:.1f}: ALL values are zero")
        
        if zero_points_found == 0:
            logger.info("  No time points found where ALL values are zero - this is why no filtering occurred")
        else:
            logger.info(f"  Found {zero_points_found} time points where all values are zero")

if __name__ == "__main__":
    try:
        analyze_filtering_behavior()
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Analysis failed with error: {e}")
        sys.exit(1)
