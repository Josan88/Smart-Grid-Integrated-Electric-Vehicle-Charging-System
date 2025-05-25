# Smart Grid-Integrated Electric Vehicle Charging System

## Project Overview

The Smart Grid-Integrated Electric Vehicle (EV) Charging System is a simulation dashboard designed to model, visualize, and manage the complexities of an EV charging infrastructure that interacts w[...]

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

(Instructions on how to set up and run the project will be added here. This typically includes steps for cloning the repository, installing dependencies, and starting the simulation server and UI.[...]

## Installation

### Install from MATLAB
You can install the MATLAB engine directly from MATLAB. Start MATLAB and run the following commands.

System	| MATLAB Commands
------- | ---------------
Windows® | `cd (fullfile(matlabroot,"extern","engines","python"))` <br> `system("python -m pip install .")`

For MATLAB and Python compatibility details, please refer to the official MathWorks documentation: [MATLAB Python Compatibility](https://uk.mathworks.com/support/requirements/python-compatibility.html)

## Project Structure

(A brief overview of the main directories and files will be added here to help users navigate the codebase.)

## How to Use

(Details on how to interact with the dashboard, configure simulations, and interpret the results will be added here.)

## Contributing

(Guidelines for contributing to the project will be added here, if applicable.)

## License

(License information for the project will be added here.)
