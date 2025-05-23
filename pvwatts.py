import requests
import json


def get_pvwatts_data(
    api_key, system_capacity, module_type, losses, array_type, lat, lon, tilt, azimuth
):
    """
    Calls the NREL PVWatts V8 API to get photovoltaic energy production estimates.

    Args:
        api_key (str): Your NREL developer API key.
        system_capacity (float): Nameplate capacity (kW). Range: 0.05 to 500000.
        module_type (int): Module type (0=Standard, 1=Premium, 2=Thin film).
        losses (float): System losses (percent). Range: -5 to 99.
        array_type (int): Array type (0=Fixed Open Rack, 1=Fixed Roof Mount, 2=1-Axis Tracking, 3=1-Axis Backtracking, 4=2-Axis Tracking).
        lat (float): Latitude (degrees). Range: -90 to 90.
        lon (float): Longitude (degrees). Range: -180 to 180.
        tilt (float): Tilt angle (degrees). Range: 0 to 90.
        azimuth (float): Azimuth angle (degrees). Range: 0 to 359.9.

    Returns:
        dict: The JSON response from the API, or None if an error occurs.
    """
    base_url = "https://developer.nrel.gov/api/pvwatts/v8.json"
    params = {
        "api_key": api_key,
        "system_capacity": system_capacity,
        "module_type": module_type,
        "losses": losses,
        "array_type": array_type,
        "lat": lat,
        "lon": lon,
        "tilt": tilt,
        "azimuth": azimuth,
        "timeframe": "hourly",  # Optional: 'hourly' or 'monthly'
        # Add other optional parameters as needed, e.g., 'gcr', 'dc_ac_ratio', 'inv_eff', 'radius', 'soiling', 'albedo', 'bifaciality'
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling PVWatts API: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response from PVWatts API.")
        print(f"Response text: {response.text}")
        return None


if __name__ == "__main__":
    # --- Test Configuration ---
    API_KEY = "YAwml3YOnwIHYekjGfahs7hSVx4iI0gDtTxlvwCu"
    LATITUDE = 1.532498597850374
    LONGITUDE = 110.35732724037013
    SYSTEM_CAPACITY_KW = 26.02
    MODULE_TYPE = 0  # 0=Standard, 1=Premium, 2=Thin film
    LOSSES_PERCENT = 14.0
    ARRAY_TYPE = 1  # 0=Fixed Open Rack, 1=Fixed Roof Mount, 2=1-Axis Tracking, ...
    TILT_ANGLE = 20.0  # Tilt angle (degrees)
    AZIMUTH_ANGLE = 180.0  # Azimuth angle (degrees, 180=South)
    OUTPUT_FILE = "pvwatts_response.json"
    # --- End Configuration ---

    print("Requesting data from PVWatts API...")
    pvwatts_data = get_pvwatts_data(
        api_key=API_KEY,
        system_capacity=SYSTEM_CAPACITY_KW,
        module_type=MODULE_TYPE,
        losses=LOSSES_PERCENT,
        array_type=ARRAY_TYPE,
        lat=LATITUDE,
        lon=LONGITUDE,
        tilt=TILT_ANGLE,
        azimuth=AZIMUTH_ANGLE,
    )

    if pvwatts_data:
        print("Successfully retrieved data.")
        # Optionally, save the response to a file
        try:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(pvwatts_data, f, indent=4)
            print(f"Response saved to {OUTPUT_FILE}")
        except IOError as e:
            print(f"Error saving response to file: {e}")
    else:
        print("Failed to retrieve data from PVWatts API.")
