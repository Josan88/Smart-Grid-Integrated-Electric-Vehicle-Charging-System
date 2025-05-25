# Smart Grid-Integrated Electric Vehicle Charging System

## Project Overview

The Smart Grid-Integrated Electric Vehicle (EV) Charging System is a simulation dashboard designed to model, visualize, and manage the complexities of an EV charging infrastructure that interacts with a smart grid. This system allows users to simulate various scenarios, monitor real-time data, and analyze the performance of the charging system, including the integration of renewable energy sources like solar power.

## Key Features

*   **Dynamic Simulation Control:**
    *   Start, stop, and control the speed of simulations.
    *   Set specific start dates and times for simulation runs to model different conditions.
*   **Real-time Data Visualization:**
    *   Interactive charts displaying key performance indicators:
        *   **PV Output:** Monitors power generated from photovoltaic (solar) sources.
        *   **Battery Status:** Tracks the state of charge (SoC) and recharge rate of energy storage systems.
        *   **EV Charging:** Shows the recharge rate for EVs and the battery levels of individual vehicles connected to charging bays.
        *   **Grid Interaction:** Visualizes power requested from or supplied to the main grid.
*   **Configurable Simulation Parameters:**
    *   Adjust a wide range of parameters influencing energy flow, charging bay allocation strategies, battery management logic, and more.
*   **PVWatts Integration:**
    *   Allows users to input or update PVWatts settings, enabling the simulation to incorporate realistic solar energy generation data.
*   **Comprehensive Data Logging & Export:**
    *   Logs significant simulation events and data points.
    *   Provides functionality to export detailed simulation data to CSV files for further analysis.
*   **Interactive User Interface:**
    *   A web-based dashboard built with HTML, CSS, and JavaScript.
    *   Utilizes Socket.IO for seamless real-time communication between the frontend and backend.
    *   Features intuitive controls such as buttons, forms, dropdown menus, and sliders for user interaction.
*   **Modular Backend System:**
    *   The backend is primarily developed in Python, managing the core simulation logic, data processing, and communication with the user interface.
    *   Includes MATLAB components (e.g., `sim_the_model.m`) for specific modeling or simulation tasks, indicating a hybrid approach to the simulation engine.

## Technologies Used

*   **Frontend:** HTML, CSS, JavaScript
    *   **Charting Library:** (Likely Chart.js or a similar library, based on common web practices)
    *   **Real-time Communication:** Socket.IO
*   **Backend:** Python, MATLAB
*   **Data Exchange Format:** JSON (for API communication), CSV (for data export)

## Getting Started

(Instructions on how to set up and run the project will be added here. This typically includes steps for cloning the repository, installing dependencies, and starting the simulation server and UI.[...])

## Installation (Windows)

To integrate MATLAB functionalities with this Python-based system, the MATLAB Engine API for Python must be installed on your Windows system. This is best done within a Python virtual environment to isolate project dependencies.

**Compatibility Check:**
First, verify that your Python version is compatible with your MATLAB installation. Consult the official MathWorks documentation:
[MATLAB Python Compatibility](https://uk.mathworks.com/support/requirements/python-compatibility.html)

### Installing into a Python Virtual Environment (Windows - Recommended)

1.  **Create and Activate Your Python Virtual Environment (Windows):**
    If you haven't already, create a virtual environment in your project directory. Open Command Prompt or PowerShell.

    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```
    *(Replace `.venv` with your preferred environment name if desired.)*

2.  **Install the MATLAB Engine into the Activated Environment (Windows):**
    With your virtual environment active, **open a new Command Prompt or PowerShell as Administrator**.
    Navigate to the MATLAB Python engine directory. You can find your MATLAB installation path (known as `matlabroot`) by typing `matlabroot` in the MATLAB Command Window.

    Replace `YOUR_MATLAB_ROOT_PATH` with your actual MATLAB installation path (e.g., `C:\Program Files\MATLAB\R2023b`).
    ```bash
    cd "YOUR_MATLAB_ROOT_PATH\extern\engines\python"
    python -m pip install .
    ```
    Example: If your MATLAB is installed in `C:\Program Files\MATLAB\R2023b`, the command would be:
    `cd "C:\Program Files\MATLAB\R2023b\extern\engines\python"`

3.  **Verify Installation (Optional):**
    In your activated virtual environment, start a Python interpreter and run:
    ```python
    import matlab.engine
    print("MATLAB engine imported successfully!")
    ```

## Project Structure

(A brief overview of the main directories and files will be added here to help users navigate the codebase.)

## How to Use

(Details on how to interact with the dashboard, configure simulations, and interpret the results will be added here.)

## Contributing

(Guidelines for contributing to the project will be added here, if applicable.)

## License

(License information for the project will be added here.)
