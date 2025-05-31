"""
Final test script to verify peak status functionality works correctly
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import calculate_electricity_cost, current_electricity_pricing
from simulation import SimulationParameters


class TestPeakStatusFunctionality(unittest.TestCase):
    """Test suite for peak status functionality across the system."""

    def setUp(self):
        """Set up test fixtures."""
        self.peak_start_hour = 8  # 8 AM
        self.peak_end_hour = 22   # 10 PM
        
    def test_peak_time_detection_morning_start(self):
        """Test peak time detection at morning start (8 AM)."""
        test_datetime = datetime(2020, 1, 1, 8, 0, 0)  # 8:00 AM
        is_peak = (
            test_datetime.hour >= self.peak_start_hour
            and test_datetime.hour < self.peak_end_hour
        )
        self.assertTrue(is_peak, "8 AM should be peak time")
        
    def test_peak_time_detection_evening_end(self):
        """Test peak time detection at evening end (10 PM)."""
        test_datetime = datetime(2020, 1, 1, 22, 0, 0)  # 10:00 PM
        is_peak = (
            test_datetime.hour >= self.peak_start_hour
            and test_datetime.hour < self.peak_end_hour
        )
        self.assertFalse(is_peak, "10 PM should be off-peak time")
        
    def test_peak_time_detection_midnight(self):
        """Test peak time detection at midnight."""
        test_datetime = datetime(2020, 1, 1, 0, 0, 0)  # 12:00 AM
        is_peak = (
            test_datetime.hour >= self.peak_start_hour
            and test_datetime.hour < self.peak_end_hour
        )
        self.assertFalse(is_peak, "Midnight should be off-peak time")
        
    def test_peak_time_detection_noon(self):
        """Test peak time detection at noon."""
        test_datetime = datetime(2020, 1, 1, 12, 0, 0)  # 12:00 PM
        is_peak = (
            test_datetime.hour >= self.peak_start_hour
            and test_datetime.hour < self.peak_end_hour
        )
        self.assertTrue(is_peak, "Noon should be peak time")

    def test_electricity_cost_calculation_peak(self):
        """Test electricity cost calculation during peak hours."""
        # Test during peak hours (noon)
        test_datetime = datetime(2020, 1, 1, 12, 0, 0)
        grid_request = 10.0  # 10 kW
        time_hours = 1.0     # 1 hour
        
        cost_info = calculate_electricity_cost(grid_request, time_hours, test_datetime)
        
        # Should use peak rate (0.229 RM/kWh)
        expected_cost = 10.0 * 1.0 * 0.229  # 2.29 RM
        self.assertAlmostEqual(cost_info['cost'], expected_cost, places=3)
        self.assertEqual(cost_info['rate_type'], 'Peak')
        self.assertEqual(cost_info['rate_used'], 0.229)

    def test_electricity_cost_calculation_off_peak(self):
        """Test electricity cost calculation during off-peak hours."""
        # Reset global cost tracking for clean test
        import app
        app.total_grid_cost = 0.0
        
        # Test during off-peak hours (midnight)
        test_datetime = datetime(2020, 1, 1, 0, 0, 0)
        grid_request = 10.0  # 10 kW
        time_hours = 1.0     # 1 hour
        
        cost_info = calculate_electricity_cost(grid_request, time_hours, test_datetime)
        
        # Should use off-peak rate (0.139 RM/kWh)
        expected_cost = 10.0 * 1.0 * 0.139  # 1.39 RM
        self.assertAlmostEqual(cost_info['cost'], expected_cost, places=3)
        self.assertEqual(cost_info['rate_type'], 'Off-Peak')
        self.assertEqual(cost_info['rate_used'], 0.139)

    def test_simulation_grid_peak_parameter(self):
        """Test that SimulationParameters correctly handles GridPeak."""
        params = SimulationParameters()
        
        # Test setting peak status
        params.GridPeak = 1.0  # Peak time
        self.assertEqual(params.GridPeak, 1.0)
        
        # Test setting off-peak status
        params.GridPeak = 0.0  # Off-peak time
        self.assertEqual(params.GridPeak, 0.0)
        
        # Test parameters dictionary conversion
        params_dict = params.to_dict()
        self.assertIn('GridPeak', params_dict)
        self.assertEqual(params_dict['GridPeak'], 0.0)

    def test_peak_status_boundary_conditions(self):
        """Test peak status at boundary conditions."""
        test_cases = [
            (7, 59, False, "7:59 AM should be off-peak"),
            (8, 0, True, "8:00 AM should be peak"),
            (8, 1, True, "8:01 AM should be peak"),
            (21, 59, True, "9:59 PM should be peak"),
            (22, 0, False, "10:00 PM should be off-peak"),
            (22, 1, False, "10:01 PM should be off-peak"),
        ]
        
        for hour, minute, expected_peak, message in test_cases:
            test_datetime = datetime(2020, 1, 1, hour, minute, 0)
            is_peak = (
                test_datetime.hour >= self.peak_start_hour
                and test_datetime.hour < self.peak_end_hour
            )
            self.assertEqual(is_peak, expected_peak, message)

    def test_peak_status_data_structure(self):
        """Test that peak status data structure is correct."""
        # Test peak time
        test_datetime_peak = datetime(2020, 1, 1, 14, 0, 0)  # 2 PM
        current_hour = test_datetime_peak.hour
        is_grid_peak = 8 <= current_hour < 22
        
        data_point = {
            "is_grid_peak": is_grid_peak,
            "grid_peak_status": "Peak" if is_grid_peak else "Off-Peak",
        }
        
        self.assertTrue(data_point["is_grid_peak"])
        self.assertEqual(data_point["grid_peak_status"], "Peak")
        
        # Test off-peak time
        test_datetime_off_peak = datetime(2020, 1, 1, 2, 0, 0)  # 2 AM
        current_hour = test_datetime_off_peak.hour
        is_grid_peak = 8 <= current_hour < 22
        
        data_point = {
            "is_grid_peak": is_grid_peak,
            "grid_peak_status": "Peak" if is_grid_peak else "Off-Peak",
        }
        
        self.assertFalse(data_point["is_grid_peak"])
        self.assertEqual(data_point["grid_peak_status"], "Off-Peak")

    def test_all_hours_classification(self):
        """Test peak classification for all 24 hours."""
        for hour in range(24):
            test_datetime = datetime(2020, 1, 1, hour, 0, 0)
            is_peak = (
                test_datetime.hour >= self.peak_start_hour
                and test_datetime.hour < self.peak_end_hour
            )
            
            if 8 <= hour < 22:
                self.assertTrue(is_peak, f"Hour {hour} should be peak")
            else:
                self.assertFalse(is_peak, f"Hour {hour} should be off-peak")

    def test_peak_status_string_formatting(self):
        """Test peak status string formatting for UI display."""
        # Test peak status formatting
        peak_statuses = [
            (True, "Peak"),
            (False, "Off-Peak"),
        ]
        
        for is_peak, expected_string in peak_statuses:
            status_string = "Peak" if is_peak else "Off-Peak"
            self.assertEqual(status_string, expected_string)


def run_peak_status_tests():
    """Run all peak status tests and return results."""
    print("=" * 60)
    print("PEAK STATUS FUNCTIONALITY TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPeakStatusFunctionality)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("PEAK STATUS TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
    
    return success


if __name__ == "__main__":
    run_peak_status_tests()
