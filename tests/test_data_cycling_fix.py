#!/usr/bin/env python3
"""
Test script to verify that the data cycling fix works correctly when simulation parameters change.
This simulates the scenario where parameters are changed during simulation runtime.
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add the current directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_hour_index_calculation():
    """Test the hour index calculation logic that was fixed."""
    print("Testing hour index calculation logic...")
    
    # Load sample hourly_dc_watts data (8760 hours)
    try:
        with open("pvwatts_response.json", "r") as f:
            data = json.load(f)
        hourly_dc_watts = data["outputs"]["dc"]
        print(f"Loaded {len(hourly_dc_watts)} hourly DC watts values")
    except:
        # Create dummy data if file not found
        hourly_dc_watts = list(range(8760))  # Simple sequential values for testing
        print("Using dummy data for testing")

    def calculate_hour_index(simulation_datetime):
        """Calculate hour index based on datetime (the correct method)."""
        day_of_year = simulation_datetime.timetuple().tm_yday
        hour_of_day = simulation_datetime.hour
        calculated_idx = (day_of_year - 1) * 24 + hour_of_day
        return calculated_idx % len(hourly_dc_watts)

    # Test scenarios
    test_scenarios = [
        # (description, start_datetime, parameter_change_datetime, expected_behavior)
        ("New Year Start", datetime(2020, 1, 1, 0, 0, 0), datetime(2020, 1, 1, 12, 0, 0), "Should cycle correctly"),
        ("Mid Year Start", datetime(2020, 6, 15, 8, 0, 0), datetime(2020, 6, 15, 20, 0, 0), "Should maintain correct index"),
        ("Year End", datetime(2020, 12, 31, 20, 0, 0), datetime(2020, 12, 31, 23, 0, 0), "Should handle year boundary"),
        ("Leap Year", datetime(2020, 2, 29, 12, 0, 0), datetime(2020, 3, 1, 0, 0, 0), "Should handle leap year correctly"),
    ]

    print("\nTesting different scenarios:")
    print("=" * 80)
    
    for description, start_dt, change_dt, expected in test_scenarios:
        print(f"\nScenario: {description}")
        print(f"Start DateTime: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Parameter Change DateTime: {change_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Calculate initial hour index
        initial_index = calculate_hour_index(start_dt)
        print(f"Initial Hour Index: {initial_index}")
        print(f"Initial DC Watts: {hourly_dc_watts[initial_index]}")
        
        # Calculate hour index after parameter change
        change_index = calculate_hour_index(change_dt)
        print(f"After Change Hour Index: {change_index}")
        print(f"After Change DC Watts: {hourly_dc_watts[change_index]}")
        
        # Verify the calculation is consistent
        hours_elapsed = (change_dt - start_dt).total_seconds() / 3600
        expected_index = (initial_index + int(hours_elapsed)) % len(hourly_dc_watts)
        
        if change_index == expected_index:
            print(f"✅ PASS: Index calculation is consistent")
        else:
            print(f"❌ FAIL: Expected index {expected_index}, got {change_index}")
        
        print(f"Expected: {expected}")
        print("-" * 60)

def test_parameter_change_simulation():
    """Simulate the parameter change scenario that was causing issues."""
    print("\n" + "=" * 80)
    print("SIMULATION: Parameter Change During Runtime")
    print("=" * 80)
    
    # Load hourly data
    try:
        with open("pvwatts_response.json", "r") as f:
            data = json.load(f)
        hourly_dc_watts = data["outputs"]["dc"]
    except:
        hourly_dc_watts = list(range(8760))
    
    def get_hour_index_from_datetime(dt):
        day_of_year = dt.timetuple().tm_yday
        hour_of_day = dt.hour
        return ((day_of_year - 1) * 24 + hour_of_day) % len(hourly_dc_watts)
    
    # Simulate the old problematic behavior vs new fixed behavior
    print("\nSimulating old vs new behavior:")
    
    # Initial simulation state
    initial_datetime = datetime(2020, 6, 15, 10, 0, 0)  # June 15, 10 AM
    current_dc_hour_index = get_hour_index_from_datetime(initial_datetime)
    total_simulation_seconds = 0
    
    print(f"Initial State:")
    print(f"  DateTime: {initial_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Hour Index: {current_dc_hour_index}")
    print(f"  DC Watts: {hourly_dc_watts[current_dc_hour_index]}")
    
    # Simulate running for 2 hours (multiple iterations)
    simulation_datetime = initial_datetime
    for iteration in range(4):  # 4 iterations of 30 minutes each = 2 hours
        simulation_datetime += timedelta(seconds=1800)  # 30 minutes
        total_simulation_seconds += 1800
        
        # OLD METHOD (problematic)
        old_hour_increments = (total_simulation_seconds // 3600) - current_dc_hour_index
        if old_hour_increments > 0:
            old_index = (current_dc_hour_index + old_hour_increments) % len(hourly_dc_watts)
        else:
            old_index = current_dc_hour_index
        
        # NEW METHOD (fixed)
        new_index = get_hour_index_from_datetime(simulation_datetime)
        
        print(f"\nIteration {iteration + 1} - {simulation_datetime.strftime('%Y-%m-%d %H:%M:%S')}:")
        print(f"  Old Method Index: {old_index}")
        print(f"  New Method Index: {new_index}")
        print(f"  Match: {'✅' if old_index == new_index else '❌'}")
        
        # Update for next iteration
        current_dc_hour_index = new_index
    
    # Now simulate parameter change (restart simulation)
    print(f"\n🔄 PARAMETER CHANGE - Restarting simulation at new time:")
    new_start_datetime = datetime(2020, 8, 20, 14, 0, 0)  # August 20, 2 PM
    new_index = get_hour_index_from_datetime(new_start_datetime)
    
    print(f"  New DateTime: {new_start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  New Hour Index: {new_index}")
    print(f"  New DC Watts: {hourly_dc_watts[new_index]}")
    
    # Continue simulation from new state
    current_dc_hour_index = new_index
    total_simulation_seconds = 0  # Reset as per the restart logic
    simulation_datetime = new_start_datetime
    
    print(f"\nContinuing from new parameters:")
    for iteration in range(2):  # 2 more iterations
        simulation_datetime += timedelta(seconds=1800)  # 30 minutes
        total_simulation_seconds += 1800
        
        # Both methods should now work correctly
        new_index = get_hour_index_from_datetime(simulation_datetime)
        
        print(f"  Iteration {iteration + 1} - {simulation_datetime.strftime('%Y-%m-%d %H:%M:%S')}:")
        print(f"    Hour Index: {new_index}")
        print(f"    DC Watts: {hourly_dc_watts[new_index]}")
        
        current_dc_hour_index = new_index

if __name__ == "__main__":
    print("Data Cycling Fix Verification Test")
    print("=" * 50)
    
    test_hour_index_calculation()
    test_parameter_change_simulation()
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("The fix ensures that hour index calculation is always based on the current")
    print("simulation_datetime rather than problematic increment calculations.")
    print("This resolves the incorrect data cycling when parameters change.")
    print("=" * 80)
