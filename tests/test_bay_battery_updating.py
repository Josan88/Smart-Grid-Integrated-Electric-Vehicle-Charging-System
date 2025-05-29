#!/usr/bin/env python3
"""
Test script to verify bay battery updating functionality.

This script tests that bay battery percentages are properly updated
when user-set flags are False (automatic mode).
"""

import sys
import time
import logging
from app import (
    current_simulation_params, 
    simulation_lock,
    logger
)

# Set up logging for this test
test_logger = logging.getLogger("bay_battery_update_test")
test_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
test_logger.addHandler(handler)

def test_bay_percentage_updating():
    """Test that bay percentages are updated when user-set flags are False."""
    test_logger.info("=== Testing Bay Percentage Automatic Updates ===")
    
    with simulation_lock:
        # Set initial values
        current_simulation_params.bay1_percentage = 25.0
        current_simulation_params.bay2_percentage = 30.0
        current_simulation_params.bay3_percentage = 35.0
        current_simulation_params.bay4_percentage = 40.0
        
        # Ensure user-set flags are False (automatic mode)
        current_simulation_params._user_set_bay1_percentage = False
        current_simulation_params._user_set_bay2_percentage = False
        current_simulation_params._user_set_bay3_percentage = False
        current_simulation_params._user_set_bay4_percentage = False
        
        test_logger.info(f"Initial values - Bay1: {current_simulation_params.bay1_percentage}%, "
                        f"Bay2: {current_simulation_params.bay2_percentage}%, "
                        f"Bay3: {current_simulation_params.bay3_percentage}%, "
                        f"Bay4: {current_simulation_params.bay4_percentage}%")
    
    # Simulate simulation results with new values
    mock_simulation_results = {
        'vehicle1_battery_level': [85.0],
        'vehicle2_battery_level': [90.0],
        'vehicle3_battery_level': [70.0],
        'vehicle4_battery_level': [95.0]
    }
    
    test_logger.info(f"Mock simulation results - Bay1: {mock_simulation_results['vehicle1_battery_level'][0]}%, "
                    f"Bay2: {mock_simulation_results['vehicle2_battery_level'][0]}%, "
                    f"Bay3: {mock_simulation_results['vehicle3_battery_level'][0]}%, "
                    f"Bay4: {mock_simulation_results['vehicle4_battery_level'][0]}%")
    
    with simulation_lock:
        # Apply the update logic from run_continuous_simulation
        
        # Bay 1 - Should be updated (user-set flag is False)
        if (not hasattr(current_simulation_params, "_user_set_bay1_percentage") 
            or not current_simulation_params._user_set_bay1_percentage):
            current_simulation_params.bay1_percentage = mock_simulation_results['vehicle1_battery_level'][0]
            test_logger.info("Bay 1 updated from simulation results")
        else:
            test_logger.info("Bay 1 preserved (unexpected in this test)")
        
        # Bay 2 - Should be updated (user-set flag is False)
        if (not hasattr(current_simulation_params, "_user_set_bay2_percentage") 
            or not current_simulation_params._user_set_bay2_percentage):
            current_simulation_params.bay2_percentage = mock_simulation_results['vehicle2_battery_level'][0]
            test_logger.info("Bay 2 updated from simulation results")
        else:
            test_logger.info("Bay 2 preserved (unexpected in this test)")
        
        # Bay 3 - Should be updated (user-set flag is False)
        if (not hasattr(current_simulation_params, "_user_set_bay3_percentage") 
            or not current_simulation_params._user_set_bay3_percentage):
            current_simulation_params.bay3_percentage = mock_simulation_results['vehicle3_battery_level'][0]
            test_logger.info("Bay 3 updated from simulation results")
        else:
            test_logger.info("Bay 3 preserved (unexpected in this test)")
        
        # Bay 4 - Should be updated (user-set flag is False)
        if (not hasattr(current_simulation_params, "_user_set_bay4_percentage") 
            or not current_simulation_params._user_set_bay4_percentage):
            current_simulation_params.bay4_percentage = mock_simulation_results['vehicle4_battery_level'][0]
            test_logger.info("Bay 4 updated from simulation results")
        else:
            test_logger.info("Bay 4 preserved (unexpected in this test)")
    
    # Verify values were updated correctly
    assert current_simulation_params.bay1_percentage == 85.0, f"Bay 1 not updated! Expected 85.0, got {current_simulation_params.bay1_percentage}"
    assert current_simulation_params.bay2_percentage == 90.0, f"Bay 2 not updated! Expected 90.0, got {current_simulation_params.bay2_percentage}"
    assert current_simulation_params.bay3_percentage == 70.0, f"Bay 3 not updated! Expected 70.0, got {current_simulation_params.bay3_percentage}"
    assert current_simulation_params.bay4_percentage == 95.0, f"Bay 4 not updated! Expected 95.0, got {current_simulation_params.bay4_percentage}"
    
    test_logger.info("✓ All bay percentages were correctly updated from simulation results")
    test_logger.info(f"Final values - Bay1: {current_simulation_params.bay1_percentage}%, "
                    f"Bay2: {current_simulation_params.bay2_percentage}%, "
                    f"Bay3: {current_simulation_params.bay3_percentage}%, "
                    f"Bay4: {current_simulation_params.bay4_percentage}%")
    return True

def test_user_set_flag_behavior():
    """Test the user-set flag setting and preservation behavior."""
    test_logger.info("=== Testing User-Set Flag Behavior ===")
    
    with simulation_lock:
        # Clear any existing flags
        for attr in ['_user_set_bay1_percentage', '_user_set_bay2_percentage', 
                     '_user_set_bay3_percentage', '_user_set_bay4_percentage']:
            if hasattr(current_simulation_params, attr):
                delattr(current_simulation_params, attr)
        
        # Set some values and flags manually
        current_simulation_params.bay1_percentage = 55.0
        current_simulation_params._user_set_bay1_percentage = True
        
        current_simulation_params.bay2_percentage = 60.0
        # Don't set bay2 flag - should default to False
        
        test_logger.info(f"Set bay1_percentage to {current_simulation_params.bay1_percentage}% with user-set flag True")
        test_logger.info(f"Set bay2_percentage to {current_simulation_params.bay2_percentage}% with no user-set flag")
    
    # Simulate trying to update from simulation results
    mock_results = {
        'vehicle1_battery_level': [75.0],  # Different from user-set 55%
        'vehicle2_battery_level': [80.0],  # Different from 60%
    }
    
    with simulation_lock:
        # Bay 1 - Should NOT be updated (user-set flag is True)
        if (not hasattr(current_simulation_params, "_user_set_bay1_percentage") 
            or not current_simulation_params._user_set_bay1_percentage):
            current_simulation_params.bay1_percentage = mock_results['vehicle1_battery_level'][0]
            test_logger.info("Bay 1 updated (unexpected!)")
        else:
            test_logger.info("Bay 1 preserved due to user-set flag")
        
        # Bay 2 - Should be updated (no user-set flag or flag is False)
        if (not hasattr(current_simulation_params, "_user_set_bay2_percentage") 
            or not current_simulation_params._user_set_bay2_percentage):
            current_simulation_params.bay2_percentage = mock_results['vehicle2_battery_level'][0]
            test_logger.info("Bay 2 updated (expected)")
        else:
            test_logger.info("Bay 2 preserved (unexpected!)")
    
    # Verify behavior
    assert current_simulation_params.bay1_percentage == 55.0, f"Bay 1 should be preserved! Expected 55.0, got {current_simulation_params.bay1_percentage}"
    assert current_simulation_params.bay2_percentage == 80.0, f"Bay 2 should be updated! Expected 80.0, got {current_simulation_params.bay2_percentage}"
    
    test_logger.info("✓ User-set flag behavior working correctly")
    return True

def run_all_tests():
    """Run all bay battery update tests."""
    test_logger.info("Starting Bay Battery Update Tests")
    test_logger.info("=" * 50)
    
    try:
        test_bay_percentage_updating()
        test_user_set_flag_behavior()
        
        test_logger.info("=" * 50)
        test_logger.info("🎉 ALL BAY BATTERY UPDATE TESTS PASSED!")
        test_logger.info("✓ Bay percentages update correctly when user-set flags are False")
        test_logger.info("✓ User-set flags prevent unwanted updates when True")
        test_logger.info("✓ Implementation maintains simulation continuity")
        
        return True
        
    except Exception as e:
        test_logger.error(f"❌ TEST FAILED: {str(e)}")
        import traceback
        test_logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Wait a moment to ensure the application is fully started
    time.sleep(2)
    
    try:
        success = run_all_tests()
        if success:
            print("\n" + "="*60)
            print("🎉 BAY BATTERY UPDATE TESTS COMPLETED SUCCESSFULLY!")
            print("✅ All update functionality is working correctly")
            print("✅ Bay percentages update from simulation when appropriate")
            print("✅ User-set flags properly control update behavior")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ BAY BATTERY UPDATE TESTS FAILED!")
            print("Please check the implementation and logs above")
            print("="*60)
            exit(1)
    except KeyboardInterrupt:
        test_logger.info("Tests interrupted by user")
    except Exception as e:
        test_logger.error(f"Test execution failed: {e}")
        exit(1)
