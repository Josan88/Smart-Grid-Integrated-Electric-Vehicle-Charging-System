#!/usr/bin/env python3
"""
Test script to simulate changing parameters and check zero-filtering behavior.
This simulates what happens when the web application changes parameters.
"""

import logging
import sys
from simulation import SimulationParameters, simulation_session

# Configure logging to match the main application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("test_parameter_change")

def test_simulation_with_different_parameters():
    """Test simulation with different parameter sets to check filtering behavior."""
    
    # Define different parameter sets to test
    test_cases = [
        {
            "name": "Default Parameters",
            "params": SimulationParameters(
                PVOutput=10.0,
                BatteryOutput=30.0,
            )
        },
        {
            "name": "EV Charging Scenario",
            "params": SimulationParameters(
                bay1_occupied=1.0,
                bay2_occupied=1.0,
                bay1_percentage=50.0,
                bay2_percentage=75.0,
                PVOutput=10.0,
                BatteryOutput=30.0,
            )
        },
        {
            "name": "Grid Peak Load",
            "params": SimulationParameters(
                bay1_occupied=1.0,
                bay2_occupied=1.0,
                bay3_occupied=1.0,
                bay4_occupied=1.0,
                bay1_percentage=80.0,
                bay2_percentage=90.0,
                bay3_percentage=60.0,
                bay4_percentage=70.0,
                PVOutput=15.0,
                BatteryOutput=50.0,
                GridPeak=1.0,
                battery_soc=50.0,
            )
        },
        {
            "name": "High Battery SOC",
            "params": SimulationParameters(
                PVOutput=20.0,
                BatteryOutput=40.0,
                battery_soc=90.0,
            )
        }
    ]
    
    with simulation_session() as sim_manager:
        if sim_manager is None:
            logger.error("Failed to start simulation session")
            return
            
        for i, test_case in enumerate(test_cases):
            logger.info(f"\n{'='*60}")
            logger.info(f"TEST CASE {i+1}: {test_case['name']}")
            logger.info(f"{'='*60}")
            
            # Convert parameters to dict for logging
            params_dict = test_case['params'].to_dict()
            logger.info(f"Parameters: {params_dict}")
            
            # Run simulation
            results = sim_manager.run_and_parse_simulation(
                params=test_case['params'],
                configure_for_deployment=True,
                stop_time=50,
            )
            
            if results:
                logger.info(f"✅ RESULTS for {test_case['name']}:")
                logger.info(f"   - Data length: {results.data_length}")
                logger.info(f"   - Time range: {results.time_vector[0]:.1f} - {results.time_vector[-1]:.1f}")
                logger.info(f"   - Time points: {len(results.time_vector)}")
                
                # Check for any obvious patterns
                all_zero_batt = all(abs(v) < 1e-10 for v in results.batt_values)
                all_zero_ev = all(abs(v) < 1e-10 for v in results.ev_recharge)
                any_nonzero_grid = any(abs(v) > 1e-10 for v in results.grid_request)
                
                logger.info(f"   - Battery values all zero: {all_zero_batt}")
                logger.info(f"   - EV recharge all zero: {all_zero_ev}")
                logger.info(f"   - Grid request has non-zero: {any_nonzero_grid}")
                
                # Show a sample of the data
                logger.info(f"   - Sample times: {results.time_vector[:5]}")
                logger.info(f"   - Sample battery: {results.batt_values[:5]}")
                logger.info(f"   - Sample grid request: {results.grid_request[:5]}")
                
            else:
                logger.error(f"❌ Simulation failed for {test_case['name']}")
            
            logger.info("")  # Empty line for readability

if __name__ == "__main__":
    try:
        test_simulation_with_different_parameters()
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        sys.exit(1)
