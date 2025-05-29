"""
Final test script to verify peak status functionality works correctly
"""
import requests
import time
from datetime import datetime

def test_peak_status_functionality():
    """Test that peak status correctly updates when time is changed"""
    base_url = "http://127.0.0.1:5000"
    
    print("=== Testing Peak Status Functionality ===\n")
    
    # Test 1: Check current status at midnight (should be off-peak)
    print("Test 1: Current simulation time and peak status")
    try:
        response = requests.get(f"{base_url}/api/simulation/state")
        if response.status_code == 200:
            data = response.json()
            current_time = data.get('current_datetime', 'Unknown')
            is_peak = data.get('is_grid_peak', 'Unknown')
            peak_status = data.get('grid_peak_status', 'Unknown')
            
            print(f"Current simulation time: {current_time}")
            print(f"Is grid peak: {is_peak}")
            print(f"Peak status: {peak_status}")
        else:
            print(f"Failed to get simulation state: {response.status_code}")
    except Exception as e:
        print(f"Error getting simulation state: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Set time to 8:00 AM (should be peak time)
    print("Test 2: Setting time to 8:00 AM (peak time)")
    try:
        # Stop the current simulation first
        stop_data = {"action": "stop"}
        response = requests.post(f"{base_url}/api/simulation/control", json=stop_data)
        if response.status_code == 200:
            print("Stopped current simulation")
            time.sleep(1)  # Wait for stop to complete
        
        # Start simulation with time set to 8:00 AM
        start_data = {
            "action": "start",
            "start_date": "2020-01-01",
            "start_time": "08:00:00"
        }
        
        response = requests.post(f"{base_url}/api/simulation/control", json=start_data)
        if response.status_code == 200:
            print("Successfully set time to 8:00 AM")
            
            # Wait a moment for the change to take effect
            time.sleep(3)
            
            # Check the new status
            response = requests.get(f"{base_url}/api/simulation/state")
            if response.status_code == 200:
                data = response.json()
                current_time = data.get('current_datetime', 'Unknown')
                is_peak = data.get('is_grid_peak', 'Unknown')
                peak_status = data.get('grid_peak_status', 'Unknown')
                
                print(f"New simulation time: {current_time}")
                print(f"Is grid peak: {is_peak}")
                print(f"Peak status: {peak_status}")
                
                # Verify the result
                if is_peak == True and peak_status == "Peak":
                    print("✅ SUCCESS: Peak status correctly shows as 'Peak' at 8:00 AM")
                else:
                    print(f"❌ FAILURE: Expected Peak=True and status='Peak', got Peak={is_peak}, status='{peak_status}'")
            else:
                print(f"Failed to get updated simulation state: {response.status_code}")
        else:
            print(f"Failed to set time: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error setting time to 8:00 AM: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Set time to 11:00 PM (should be off-peak time)
    print("Test 3: Setting time to 11:00 PM (off-peak time)")
    try:
        # Stop the current simulation first
        stop_data = {"action": "stop"}
        response = requests.post(f"{base_url}/api/simulation/control", json=stop_data)
        if response.status_code == 200:
            print("Stopped current simulation")
            time.sleep(1)  # Wait for stop to complete
        
        # Start simulation with time set to 11:00 PM
        start_data = {
            "action": "start",
            "start_date": "2020-01-01",
            "start_time": "23:00:00"
        }
        
        response = requests.post(f"{base_url}/api/simulation/control", json=start_data)
        if response.status_code == 200:
            print("Successfully set time to 11:00 PM")
            
            # Wait a moment for the change to take effect
            time.sleep(3)
            
            # Check the new status
            response = requests.get(f"{base_url}/api/simulation/state")
            if response.status_code == 200:
                data = response.json()
                current_time = data.get('current_datetime', 'Unknown')
                is_peak = data.get('is_grid_peak', 'Unknown')
                peak_status = data.get('grid_peak_status', 'Unknown')
                
                print(f"New simulation time: {current_time}")
                print(f"Is grid peak: {is_peak}")
                print(f"Peak status: {peak_status}")
                
                # Verify the result
                if is_peak == False and peak_status == "Off-Peak":
                    print("✅ SUCCESS: Peak status correctly shows as 'Off-Peak' at 11:00 PM")
                else:
                    print(f"❌ FAILURE: Expected Peak=False and status='Off-Peak', got Peak={is_peak}, status='{peak_status}'")
            else:
                print(f"Failed to get updated simulation state: {response.status_code}")
        else:
            print(f"Failed to set time: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error setting time to 11:00 PM: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: Set time back to midnight and verify
    print("Test 4: Setting time back to midnight (off-peak time)")
    try:
        # Stop the current simulation first
        stop_data = {"action": "stop"}
        response = requests.post(f"{base_url}/api/simulation/control", json=stop_data)
        if response.status_code == 200:
            print("Stopped current simulation")
            time.sleep(1)  # Wait for stop to complete
        
        # Start simulation with time set to midnight
        start_data = {
            "action": "start",
            "start_date": "2020-01-01",
            "start_time": "00:00:00"
        }
        
        response = requests.post(f"{base_url}/api/simulation/control", json=start_data)
        if response.status_code == 200:
            print("Successfully set time back to midnight")
            
            # Wait a moment for the change to take effect
            time.sleep(3)
            
            # Check the final status
            response = requests.get(f"{base_url}/api/simulation/state")
            if response.status_code == 200:
                data = response.json()
                current_time = data.get('current_datetime', 'Unknown')
                is_peak = data.get('is_grid_peak', 'Unknown')
                peak_status = data.get('grid_peak_status', 'Unknown')
                
                print(f"Final simulation time: {current_time}")
                print(f"Is grid peak: {is_peak}")
                print(f"Peak status: {peak_status}")
                
                # Verify the result
                if is_peak == False and peak_status == "Off-Peak":
                    print("✅ SUCCESS: Peak status correctly shows as 'Off-Peak' at midnight")
                else:
                    print(f"❌ FAILURE: Expected Peak=False and status='Off-Peak', got Peak={is_peak}, status='{peak_status}'")
            else:
                print(f"Failed to get final simulation state: {response.status_code}")
        else:
            print(f"Failed to set time back to midnight: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error setting time back to midnight: {e}")

if __name__ == "__main__":
    test_peak_status_functionality()
