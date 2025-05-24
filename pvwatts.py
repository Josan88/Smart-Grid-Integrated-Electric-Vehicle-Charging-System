import requests
import json
import os
import time
from typing import Dict, Any, Optional


# Cache settings
CACHE_FILE = "pvwatts_response.json"
CACHE_EXPIRY_DAYS = 30  # Cache expiry in days


def get_pvwatts_data(
    api_key, system_capacity, module_type, losses, array_type, lat, lon, tilt, azimuth,
    use_cache=True, force_refresh=False
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
        use_cache (bool): Whether to use cached data if available.
        force_refresh (bool): Whether to force refresh the cache.
        
    Returns:
        dict: The JSON response from the API, or None if an error occurs.
    """
    # Try to use cached data if allowed
    if use_cache and not force_refresh:
        cached_data = read_from_cache(
            system_capacity, module_type, losses, array_type, lat, lon, tilt, azimuth
        )
        if cached_data:
            print("Using cached PVWatts data")
            return cached_data

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
    
    response = None
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # Parse the JSON response
        response_data = response.json()
        
        # Save to cache
        write_to_cache(
            response_data,
            system_capacity, module_type, losses, array_type, lat, lon, tilt, azimuth
        )
        
        return response_data
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


def read_from_cache(
    system_capacity, module_type, losses, array_type, lat, lon, tilt, azimuth
) -> Optional[Dict[str, Any]]:
    """
    Reads cached data from the cache file.

    Args:
        system_capacity (float): Nameplate capacity (kW). Range: 0.05 to 500000.
        module_type (int): Module type (0=Standard, 1=Premium, 2=Thin film).
        losses (float): System losses (percent). Range: -5 to 99.
        array_type (int): Array type (0=Fixed Open Rack, 1=Fixed Roof Mount, 2=1-Axis Tracking, 3=1-Axis Backtracking, 4=2-Axis Tracking).
        lat (float): Latitude (degrees). Range: -90 to 90.
        lon (float): Longitude (degrees). Range: -180 to 180.
        tilt (float): Tilt angle (degrees). Range: 0 to 90.
        azimuth (float): Azimuth angle (degrees). Range: 0 to 359.9.

    Returns:
        dict: The cached data as a dictionary, or None if not found or expired.
    """
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, "r") as f:
            cached_data = json.load(f)

        # Check if the cached data is expired
        expiry_time = cached_data.get("expiry_time")
        if expiry_time and time.time() > expiry_time:
            return None  # Cached data is expired

        # Check if the requested parameters match the cached data
        request_params = cached_data.get("request_params", {})
        
        # Compare the key parameters
        if (abs(request_params.get("system_capacity", 0) - system_capacity) < 0.01 and
            request_params.get("module_type") == module_type and
            abs(request_params.get("losses", 0) - losses) < 0.1 and
            request_params.get("array_type") == array_type and
            abs(request_params.get("lat", 0) - lat) < 0.01 and
            abs(request_params.get("lon", 0) - lon) < 0.01 and
            abs(request_params.get("tilt", 0) - tilt) < 0.1 and
            abs(request_params.get("azimuth", 0) - azimuth) < 0.1):
            
            # We found a match with close enough parameters
            return cached_data
        
        return None
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"Error reading from cache: {e}")
        return None


def write_to_cache(
    response_data: Dict[str, Any], 
    system_capacity, module_type, losses, array_type, lat, lon, tilt, azimuth
) -> None:
    """
    Writes API response data to cache file.

    Args:
        response_data (dict): The response data to cache.
        system_capacity (float): Nameplate capacity (kW).
        module_type (int): Module type.
        losses (float): System losses (percent).
        array_type (int): Array type.
        lat (float): Latitude (degrees).
        lon (float): Longitude (degrees).
        tilt (float): Tilt angle (degrees).
        azimuth (float): Azimuth angle (degrees).
    """
    # Add metadata to the response data
    enhanced_data = response_data.copy()
    
    # Add cache expiry time
    enhanced_data["expiry_time"] = time.time() + (CACHE_EXPIRY_DAYS * 24 * 60 * 60)
    
    # Add request parameters
    enhanced_data["request_params"] = {
        "system_capacity": system_capacity,
        "module_type": module_type,
        "losses": losses,
        "array_type": array_type,
        "lat": lat,
        "lon": lon,
        "tilt": tilt,
        "azimuth": azimuth
    }
    
    # Write to cache file
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(enhanced_data, f, indent=2)
        print(f"Cached PVWatts data to {CACHE_FILE}")
    except IOError as e:
        print(f"Error caching PVWatts data: {e}")


def get_cache_status() -> Dict[str, Any]:
    """
    Get information about the cached PVWatts data.
    
    Returns:
        dict: Information about the cache status.
    """
    cache_info = {
        "exists": False,
        "expiry_days_left": 0,
        "size_bytes": 0,
        "parameters": None,
        "last_modified": None
    }
    
    if not os.path.exists(CACHE_FILE):
        return cache_info
    
    cache_info["exists"] = True
    cache_info["size_bytes"] = os.path.getsize(CACHE_FILE)
    cache_info["last_modified"] = os.path.getmtime(CACHE_FILE)
    
    try:
        with open(CACHE_FILE, "r") as f:
            cached_data = json.load(f)
        
        expiry_time = cached_data.get("expiry_time")
        if expiry_time:
            days_left = (expiry_time - time.time()) / (24 * 60 * 60)
            cache_info["expiry_days_left"] = max(0, round(days_left, 1))
        
        cache_info["parameters"] = cached_data.get("request_params")
        
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    
    return cache_info


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
        # Display cache status
        cache_status = get_cache_status()
        print(f"Cache status: {cache_status}")
    else:
        print("Failed to retrieve data from PVWatts API.")
