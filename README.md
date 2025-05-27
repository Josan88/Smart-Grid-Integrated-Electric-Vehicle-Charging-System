# Smart Grid-Integrated Electric Vehicle Charging System

## Project Overview

The Smart Grid-Integrated Electric Vehicle (EV) Charging System is a comprehensive web-based simulation dashboard that models, visualizes, and manages the complexities of an EV charging infrastructure integrated with a smart grid. This system features real-time data visualization, MATLAB-Python integration, and a modern user interface designed for monitoring and analyzing the performance of renewable energy systems and EV charging infrastructure.

## Key Features

### 🚗 **Dynamic Simulation Control**
*   Start, stop, and control simulation speed (0.25x to 10x)
*   Real-time simulation date and time display
*   Configurable simulation parameters through web interface
*   MATLAB Simulink integration via Python Engine API

### 📊 **Real-time Data Visualization**
*   **2D System Visualization:** Interactive animated display showing energy flows between components
*   **Battery Management System:** Real-time battery level with animated fill and color-coded status
*   **Solar PV System:** Live solar power output with generation status indicators
*   **Grid Connection:** Real-time grid power request/supply with peak/off-peak status
*   **EV Charging Bays:** Individual monitoring of 4 charging bays with battery levels and charging rates
*   **Energy Flow Animations:** 6 different animated energy flow paths between system components

### ⚙️ **Configurable System Parameters**
*   Solar panel output settings
*   Battery management parameters
*   EV charging bay configurations
*   Grid interaction settings
*   Electricity pricing and peak time management

### 🌞 **PVWatts Integration**
*   NREL PVWatts V8 API integration for realistic solar data
*   Cached solar generation data for improved performance
*   Configurable solar panel specifications (capacity, tilt, azimuth, etc.)

### 📈 **Data Management & Export**
*   Real-time data logging and processing
*   CSV export functionality for detailed analysis
*   Comprehensive simulation event logging
*   Data filtering and optimization for performance

### 🖥️ **Modern Web Interface**
*   Bootstrap-based responsive design
*   Real-time updates via Socket.IO WebSocket communication
*   Progress bars and visual indicators replacing traditional charts
*   Mobile-friendly interface with optimized performance

## Technologies Used

### **Frontend**
*   **Framework:** HTML5, CSS3, JavaScript (ES6+)
*   **UI Library:** Bootstrap 5.3.0 with Bootstrap Icons
*   **Real-time Communication:** Socket.IO for WebSocket connections
*   **Visualization:** Custom 2D SVG-based animations and progress indicators
*   **Responsive Design:** Mobile-first approach with modern CSS Grid and Flexbox

### **Backend**
*   **Primary Language:** Python 3.12+
*   **Web Framework:** Flask 2.3.3 with Flask-SocketIO 5.3.6
*   **MATLAB Integration:** MATLAB Engine API for Python (matlabengine 24.2.2)
*   **Simulation Engine:** MATLAB Simulink (CompleteV1.slx model)
*   **External APIs:** NREL PVWatts V8 API for solar data

### **Data & Communication**
*   **Data Exchange:** JSON for API communication
*   **Data Export:** CSV format for analysis
*   **Caching:** File-based caching for PVWatts data
*   **Real-time Updates:** EventLet for asynchronous operations

### **Development Tools**
*   **Dependencies:** Requirements.txt for Python package management
*   **Performance:** Optimized data structures for real-time processing
*   **Logging:** Comprehensive logging system for debugging and monitoring

## Getting Started

### Prerequisites
*   **Python 3.12+** with pip package manager
*   **MATLAB R2023b+** with Simulink
*   **Web Browser** with JavaScript enabled (Chrome/Firefox/Edge recommended)
*   **Windows OS** (as configured for this implementation)

### Quick Start
1. **Install Python Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Install MATLAB Engine for Python:**
   ```powershell
   # Navigate to your MATLAB installation directory
   cd "C:\Program Files\MATLAB\R2023b\extern\engines\python"
   python -m pip install .
   ```

3. **Start the Application:**
   ```powershell
   python app.py
   ```

4. **Open Dashboard:**
   Navigate to `http://localhost:5000` in your web browser

### System Architecture
```
[MATLAB Simulink] → [Python Flask Backend] → [WebSocket] → [Web Dashboard] → [2D Visualization]
        ↓                    ↓                   ↓              ↓                ↓
   CompleteV1.slx      Real-time API        Socket.IO     Bootstrap UI     SVG Animations
   Simulation Model    Data Processing      Live Updates   Progress Bars    Energy Flows
```

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

```
📁 website/
├── 📄 app.py                    # Main Flask application with Socket.IO
├── 📄 simulation.py             # MATLAB-Python interface and simulation management
├── 📄 pvwatts.py               # NREL PVWatts API integration with caching
├── 📄 requirements.txt         # Python dependencies
├── 📄 CompleteV1.slx           # MATLAB Simulink simulation model
├── 📄 sim_the_model.m          # MATLAB simulation script
├── 📄 matlab.mat               # MATLAB workspace data
├── 📁 templates/
│   └── 📄 index.html           # Main dashboard interface (839 lines)
├── 📁 static/
│   ├── 📁 css/
│   │   └── 📄 style.css        # Custom styling and animations
│   └── 📁 js/
│       └── 📄 script.js        # Frontend logic and 2D visualization
├── 📁 slprj/                   # MATLAB Simulink project files
├── 📁 __pycache__/             # Python bytecode cache
├── 📄 pvwatts_response.json    # Cached PVWatts API responses
├── 📄 pvwatts_fields.json      # PVWatts configuration fields
└── 📄 analyze_filtering.py     # Data analysis and filtering utilities

📄 test_*.py files             # Testing and verification scripts
📄 *.md files                  # Documentation and integration reports
```

### Key Components
*   **`app.py`**: Main Flask application (1355+ lines) handling web server, API endpoints, and WebSocket communication
*   **`simulation.py`**: MATLAB engine interface (613+ lines) managing Simulink model execution and data processing  
*   **`templates/index.html`**: Complete dashboard interface with 2D visualization, progress indicators, and controls
*   **`static/js/script.js`**: Frontend logic including real-time data processing and 2D system visualization
*   **`CompleteV1.slx`**: MATLAB Simulink model for smart grid and EV charging simulation

## How to Use

### Dashboard Interface
1. **Start Simulation**: Click "Start Simulation" to begin real-time data generation
2. **Control Speed**: Use the speed selector (0.25x to 10x) to adjust simulation pace
3. **Monitor Systems**: View real-time status through:
   - **Battery Management**: Animated battery level with color-coded status (green/yellow/red)
   - **Solar PV Output**: Live power generation with efficiency indicators
   - **Grid Connection**: Power request/supply with peak/off-peak status
   - **EV Charging Bays**: Individual battery levels and charging rates for 4 vehicles
   - **Energy Flows**: Animated flow lines showing power distribution between components

### Parameter Configuration
*   **Simulation Parameters**: Adjust battery output, PV settings, and EV charging parameters
*   **PVWatts Settings**: Configure solar panel specifications (latitude, longitude, tilt, azimuth)
*   **Electricity Pricing**: Set peak/off-peak rates and time periods

### Data Export & Analysis
*   **Export Data**: Click "Export Data" to download simulation results as CSV
*   **Real-time Logging**: Monitor system events in the simulation log panel
*   **Performance Metrics**: View efficiency and status indicators for all components

### 2D Visualization Features
*   **Component Status**: Visual indicators show operational state of each system component
*   **Energy Flow Animation**: Real-time animated flows between solar panels, battery, grid, and EV charging bays
*   **Status Color Coding**: Immediate visual feedback through color-coded status indicators
*   **Interactive Elements**: Hover effects and responsive design for better user experience

### Advanced Features
*   **WebSocket Communication**: Real-time updates without page refresh
*   **Mobile Responsive**: Optimized interface for tablets and mobile devices
*   **Performance Monitoring**: Built-in performance optimization with data filtering
*   **Error Handling**: Comprehensive error handling with user-friendly messages

## Performance & Reliability

### **Data Processing**
*   **Simulation Cycles**: 1.6-12 second batches with 49 active data points
*   **Real-time Updates**: Live data streaming via WebSocket connections
*   **Data Filtering**: Optimized startup point filtering for improved performance
*   **Memory Management**: Efficient data structures for continuous operation

### **System Monitoring**
*   8 active data streams: Battery, BattRecharge, EVRecharge, GridRequest, Vehicle1-4BatteryLevel
*   Real-time status monitoring for all system components
*   Comprehensive logging system for debugging and analysis
*   Performance metrics tracking for system optimization

## Contributing

This project is part of the **ENG30002 Engineering Technology Sustainability Project** at Swinburne Sarawak. 

### Development Guidelines
*   **Code Style**: Follow PEP 8 for Python, use meaningful variable names
*   **Documentation**: Update README.md and inline comments for new features
*   **Testing**: Test all changes with both frontend and MATLAB integration
*   **Performance**: Consider real-time performance impact of modifications

## License

This project is developed for educational purposes as part of the Engineering Technology Sustainability Project at Swinburne University of Technology Sarawak Campus.

---

**Project Status**: ✅ **COMPLETE AND VERIFIED**  
**Last Updated**: May 26, 2025  
**Version**: Final Integration v1.0  
**Access**: http://localhost:5000
