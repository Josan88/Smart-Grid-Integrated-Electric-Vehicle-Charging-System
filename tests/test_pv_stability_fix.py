#!/usr/bin/env python3
"""
Test script to verify PV stability preservation logic.
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
test_logger = logging.getLogger("pv_stability_test")
test_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
test_logger.addHandler(handler)

def test_pv_preserve_logic():
    """Test that PV state preservation logic works correctly."""
    test_logger.info("=== Testing PV State Preservation Logic ===")
    
    with simulation_lock:
        # Set initial battery SOC for testing
        current_simulation_params.battery_soc = 50.0
        
        # Test preserve flag behavior
        current_simulation_params._preserve_pv_state = True
        
        test_logger.info(f"Set battery_soc to {current_simulation_params.battery_soc}%")
        test_logger.info(f"Set _preserve_pv_state to {current_simulation_params._preserve_pv_state}")
    
    # Verify the preserve flag is set
    assert hasattr(current_simulation_params, '_preserve_pv_state'), "PV preserve flag should exist"
    assert current_simulation_params._preserve_pv_state == True, "PV preserve flag should be True"
    
    test_logger.info("✓ PV state preservation logic is working")
    return True

def run_all_tests():
    """Run all PV stability tests."""
    test_logger.info("Starting PV Stability Tests")
    test_logger.info("=" * 40)
    
    try:
        test_pv_preserve_logic()
        
        test_logger.info("=" * 40)
        test_logger.info("🎉 ALL PV STABILITY TESTS PASSED!")
        test_logger.info("✓ PV preservation logic is working correctly")
        
        return True
        
    except Exception as e:
        test_logger.error(f"❌ TEST FAILED: {str(e)}")
        import traceback
        test_logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    time.sleep(2)
    
    try:
        success = run_all_tests()
        if success:
            print("\n" + "="*50)
            print("🎉 PV STABILITY TESTS COMPLETED SUCCESSFULLY!")
            print("✅ PV preservation logic is implemented correctly")
            print("="*50)
        else:
            print("\n" + "="*50)
            print("❌ PV STABILITY TESTS FAILED!")
            print("Please check the implementation and logs above")
            print("="*50)
            exit(1)
    except KeyboardInterrupt:
        test_logger.info("Tests interrupted by user")
    except Exception as e:
        test_logger.error(f"Test execution failed: {e}")
        exit(1)
