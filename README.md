# Smart Grid-Integrated Electric Vehicle Charging System

## Project Overview

The Smart Grid-Integrated Electric Vehicle (EV) Charging System is a comprehensive web-based simulation dashboard that models, visualizes, and manages the complexities of an EV charging infrastructure integrated with a smart grid. This system features real-time data visualization, MATLAB-Python integration, electricity cost tracking, and a modern user interface designed for monitoring and analyzing the performance of renewable energy systems and EV charging infrastructure.

## Key Features

### 🚗 **Dynamic Simulation Control**
*   Start, stop, and control simulation speed (0.25x to 10x)
*   Real-time simulation date and time display with user-configurable start times
*   Configurable simulation parameters through web interface
*   MATLAB Simulink integration via Python Engine API
*   Automatic simulation startup for immediate system readiness

### 📊 **Real-time Data Visualization**
*   **2D System Visualization:** Interactive animated display showing energy flows between components
*   **Battery Management System:** Real-time battery level with animated fill and color-coded status
*   **Solar PV System:** Live solar power output with generation status indicators
*   **Grid Connection:** Real-time grid power request/supply with peak/off-peak status
*   **EV Charging Bays:** Individual monitoring of 4 charging bays with battery levels and charging rates
*   **Energy Flow Animations:** 6 different animated energy flow paths between system components

### 💰 **Electricity Cost Tracking & Management**
*   **Real-time Cost Calculation:** Live electricity cost tracking based on grid usage
*   **Peak/Off-Peak Pricing:** Configurable electricity rates with time-based pricing
*   **Cost Analytics:** Cumulative cost tracking and detailed cost breakdown
*   **Malaysian Ringgit (RM) Support:** Localized currency and pricing structure
*   **Cost Export:** Detailed cost data included in CSV exports
*   **Cost Reset Functionality:** Reset cost tracking for new simulation scenarios

### ⚙️ **Configurable System Parameters**
*   Solar panel output settings with PVWatts integration
*   Battery management parameters with state-of-charge tracking
*   EV charging bay configurations with individual battery monitoring
*   Grid interaction settings with peak/off-peak scheduling
*   Electricity pricing configuration (peak: RM 0.229/kWh, off-peak: RM 0.139/kWh)
*   User-defined simulation start date and time

### 🌞 **PVWatts Integration**
*   NREL PVWatts V8 API integration for realistic solar data
*   Cached solar generation data for improved performance
*   Configurable solar panel specifications (capacity, tilt, azimuth, etc.)
*   Location-based solar generation (Kuching, Sarawak coordinates)
*   Hourly solar output with 8,760 data points (full year)

### 📈 **Data Management & Export**
*   Real-time data logging and processing with point-by-point emission
*   CSV export functionality for detailed analysis including cost data
*   Comprehensive simulation event logging
*   Data filtering and optimization for performance
*   WebSocket throttling for optimal real-time performance

### 🖥️ **Modern Web Interface**
*   Bootstrap-based responsive design with optimized performance
*   Real-time updates via Socket.IO WebSocket communication
*   Progress bars and visual indicators replacing traditional charts
*   Mobile-friendly interface with touch-optimized controls
*   Dark mode support and modern CSS animations

## Technologies Used

### **Frontend**
*   **Framework:** HTML5, CSS3, JavaScript (ES6+)
*   **UI Library:** Bootstrap 5.3.0 with Bootstrap Icons
*   **Real-time Communication:** Socket.IO for WebSocket connections
*   **Visualization:** Custom 2D SVG-based animations and progress indicators
*   **Responsive Design:** Mobile-first approach with modern CSS Grid and Flexbox

### **Backend**
*   **Primary Language:** Python 3.9+ (tested with 3.12.10)
*   **Web Framework:** Flask 2.3.3 with Flask-SocketIO 5.3.6
*   **Async Support:** EventLet for high-performance WebSocket handling
*   **MATLAB Integration:** MATLAB Engine API for Python (matlabengine 24.2.2)
*   **Simulation Engine:** MATLAB Simulink 2024b (CompleteV1.slx model)
*   **External APIs:** NREL PVWatts V8 API for solar data

### **Data & Communication**
*   **Data Exchange:** JSON for API communication with optimized payloads
*   **Data Export:** CSV format for analysis with cost tracking
*   **Caching:** File-based caching for PVWatts data
*   **Real-time Updates:** EventLet for asynchronous operations
*   **Performance:** WebSocket throttling and data downsampling

### **Development Tools**
*   **Dependencies:** Requirements.txt for Python package management
*   **Performance:** Optimized data structures for real-time processing
*   **Logging:** Comprehensive logging system for debugging and monitoring
*   **Automation:** PowerShell setup script for one-command deployment

## Getting Started

### Prerequisites
*   **Python 3.9+** with pip package manager (3.12+ recommended)
*   **MATLAB 2024b** with Simulink
*   **Web Browser** with JavaScript enabled (Chrome/Firefox/Edge recommended)
*   **Windows OS** with PowerShell (as configured for this implementation)

### Quick Start

#### Method 1: Automated Setup (Recommended)
Use the provided PowerShell script for automated setup and launch:

1. **Run Setup Script:**
   ```powershell
   .\setup_and_run.ps1
   ```

2. **Optional Parameters:**
   ```powershell
   .\setup_and_run.ps1 -Port 8080          # Custom port
   .\setup_and_run.ps1 -SkipInstall        # Skip dependency installation
   .\setup_and_run.ps1 -Help               # Show help options
   ```

The script will automatically:
- ✅ Check Python version compatibility (3.9+)
- ✅ Install required dependencies from `requirements.txt`
- ✅ Start the Flask application with automatic simulation
- ✅ Open your browser to the dashboard (single tab)

#### Method 2: Manual Setup
1. **Install Python Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Install MATLAB Engine for Python:**
   ```powershell
   # Navigate to your MATLAB installation directory
   cd "C:\Program Files\MATLAB\R2024b\extern\engines\python"
   python -m pip install .
   ```

3. **Start the Application:**
   ```powershell
   python app.py --port 5000
   ```

4. **Open Dashboard:**
   Navigate to `http://localhost:5000` in your web browser

### System Architecture
```
[MATLAB Simulink] → [Python Flask Backend] → [WebSocket] → [Web Dashboard] → [2D Visualization]
        ↓                    ↓                   ↓              ↓                ↓
   CompleteV1.slx      Real-time API        Socket.IO     Bootstrap UI     SVG Animations
   Simulation Model    Data Processing      Live Updates   Progress Bars    Energy Flows
        ↓                    ↓                   ↓              ↓                ↓
   Cost Tracking      EventLet Async       Point-by-Point  Real-time Cost   Display
   Peak/Off-Peak      PVWatts Cache        Data Emission   Flow Indicators  Status Colors
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
    Navigate to the MATLAB Python engine directory. You can find your MATLAB installation path (known as `matlabroot`) by typing `matlabroot` in the MATLAB Command Window.    Replace `YOUR_MATLAB_ROOT_PATH` with your actual MATLAB installation path (e.g., `C:\Program Files\MATLAB\R2024b`).
    ```bash
    cd "YOUR_MATLAB_ROOT_PATH\extern\engines\python"
    python -m pip install .
    ```
    Example: If your MATLAB is installed in `C:\Program Files\MATLAB\R2024b`, the command would be:
    `cd "C:\Program Files\MATLAB\R2024b\extern\engines\python"`

3.  **Verify Installation (Optional):**
    In your activated virtual environment, start a Python interpreter and run:
    ```python
    import matlab.engine
    print("MATLAB engine imported successfully!")
    ```

## Project Structure

```
📁 website/
├── 📄 app.py                    # Main Flask application with Socket.IO (1,800+ lines)
├── 📄 simulation.py             # MATLAB-Python interface and simulation management
├── 📄 pvwatts.py               # NREL PVWatts API integration with caching
├── 📄 setup_and_run.ps1        # Automated PowerShell setup script (VERIFIED)
├── 📄 setup_and_run.py         # Alternative Python setup script
├── 📄 requirements.txt         # Python dependencies (EventLet, Flask-SocketIO, etc.)
├── 📄 CompleteV1.slx           # MATLAB Simulink simulation model
├── 📄 sim_the_model.m          # MATLAB simulation script
├── 📄 matlab.mat               # MATLAB workspace data
├── 📄 README.md                # Project documentation (this file)
├── 📄 SETUP_GUIDE.md           # Detailed setup instructions
├── 📁 templates/
│   └── 📄 index.html           # Main dashboard interface (responsive design)
├── 📁 static/
│   ├── 📁 css/
│   │   └── 📄 style.css        # Custom styling and animations
│   └── 📁 js/
│       └── 📄 script.js        # Frontend logic and 2D visualization
├── 📁 tests/                   # Testing and verification scripts
├── 📁 slprj/                   # MATLAB Simulink project files
├── 📁 __pycache__/             # Python bytecode cache
├── 📄 pvwatts_response.json    # Cached PVWatts API responses
├── 📄 pvwatts_fields.json      # PVWatts configuration fields
└── 📄 analyze_filtering.py     # Data analysis and filtering utilities
```

### Key Components
*   **`app.py`**: Main Flask application (1,800+ lines) handling web server, API endpoints, WebSocket communication, and electricity cost tracking
*   **`simulation.py`**: MATLAB engine interface managing Simulink model execution and data processing  
*   **`setup_and_run.ps1`**: **VERIFIED** PowerShell automation script with proper syntax and single browser tab opening
*   **`templates/index.html`**: Complete dashboard interface with 2D visualization, progress indicators, and cost display
*   **`static/js/script.js`**: Frontend logic including real-time data processing and 2D system visualization
*   **`CompleteV1.slx`**: MATLAB Simulink model for smart grid and EV charging simulation
*   **`requirements.txt`**: Updated dependencies including EventLet for performance optimization

## Recent Updates & Fixes

### ✅ **Latest Enhancements (Current Version)**
- **Electricity Cost Tracking**: Real-time cost calculation with peak/off-peak pricing (RM 0.229/0.139 per kWh)
- **Performance Optimization**: EventLet integration for improved WebSocket performance
- **Automatic Simulation**: System starts simulation immediately upon startup for instant readiness
- **Enhanced Logging**: Comprehensive cost tracking and simulation state logging
- **User-Set Parameter Tracking**: Intelligent handling of user-modified vs simulation-updated parameters

### ✅ **PowerShell Script Fixes (Verified)**
- **Fixed syntax errors**: Resolved "Unexpected token '}' in expression or statement"
- **Single browser tab**: Eliminated duplicate browser opening (now opens single tab)
- **Improved error handling**: Better Python version detection and dependency management
- **Enhanced compatibility**: Updated Python version requirement from 3.12+ to 3.9+ for broader compatibility
- **ASCII encoding**: Ensured proper script encoding to prevent character-related issues

### ✅ **System Reliability Improvements**
- **Automated setup**: One-command deployment with `.\setup_and_run.ps1`
- **Dependency management**: Automatic installation including EventLet for async support
- **Port configuration**: Configurable port settings with default 5000
- **Browser integration**: Controlled browser opening with proper server startup timing
- **Cost tracking**: Comprehensive electricity cost monitoring and export capabilities

### ✅ **Application Features**
- **MATLAB Integration**: Verified working with Python 3.12.10 and MATLAB Engine
- **Real-time WebSocket**: Socket.IO communication with EventLet for optimal performance
- **Multi-vehicle monitoring**: 4 EV charging bays with individual battery and cost tracking
- **Performance optimization**: Efficient data processing, memory management, and WebSocket throttling

## How to Use

### Dashboard Interface
1. **Automatic Start**: System automatically begins simulation upon startup
2. **Control Speed**: Use the speed selector (0.25x to 10x) to adjust simulation pace
3. **Monitor Systems**: View real-time status through:
   - **Battery Management**: Animated battery level with color-coded status (green/yellow/red)
   - **Solar PV Output**: Live power generation with efficiency indicators
   - **Grid Connection**: Power request/supply with peak/off-peak status and real-time cost
   - **EV Charging Bays**: Individual battery levels and charging rates for 4 vehicles
   - **Energy Flows**: Animated flow lines showing power distribution between components
   - **Cost Display**: Real-time electricity cost tracking with cumulative totals

### Parameter Configuration
*   **Simulation Parameters**: Adjust battery output, PV settings, and EV charging parameters
*   **Date/Time Settings**: Configure simulation start date and time
*   **PVWatts Settings**: Configure solar panel specifications (latitude, longitude, tilt, azimuth)
*   **Electricity Pricing**: Set peak/off-peak rates and time periods (default: RM 0.229/0.139 per kWh)
*   **Cost Management**: Reset cost tracking and configure pricing parameters

### Data Export & Analysis
*   **Export Data**: Click "Export Data" to download simulation results as CSV including cost data
*   **Cost Analysis**: View real-time cost breakdown with peak/off-peak rate calculations
*   **Real-time Logging**: Monitor system events and cost tracking in the simulation log panel
*   **Performance Metrics**: View efficiency and status indicators for all components

### 2D Visualization Features
*   **Component Status**: Visual indicators show operational state with cost information
*   **Energy Flow Animation**: Real-time animated flows between solar panels, battery, grid, and EV charging bays
*   **Status Color Coding**: Immediate visual feedback through color-coded status indicators
*   **Interactive Elements**: Hover effects and responsive design for better user experience
*   **Cost Indicators**: Real-time cost display integrated with system status

### Advanced Features
*   **WebSocket Communication**: Real-time updates without page refresh using EventLet
*   **Mobile Responsive**: Optimized interface for tablets and mobile devices
*   **Performance Monitoring**: Built-in performance optimization with data filtering and throttling
*   **Error Handling**: Comprehensive error handling with user-friendly messages
*   **Cost Tracking**: Detailed electricity cost monitoring with Malaysian Ringgit support

## Performance & Reliability

### **Data Processing**
*   **Simulation Cycles**: Point-by-point data emission with configurable speed (0.25x to 10x)
*   **Real-time Updates**: Live data streaming via WebSocket connections with EventLet
*   **Data Filtering**: Optimized startup point filtering for improved performance
*   **Memory Management**: Efficient data structures for continuous operation
*   **Cost Calculation**: Real-time electricity cost tracking with minimal performance impact

### **System Monitoring**
*   9 active data streams: Battery, BattRecharge, EVRecharge, GridRequest, Vehicle1-4BatteryLevel, Cost
*   Real-time status monitoring for all system components including cost tracking
*   Comprehensive logging system for debugging, analysis, and cost auditing
*   Performance metrics tracking for system optimization

### **Verified Compatibility**
*   **Python Versions**: 3.9+ (tested with 3.12.10)
*   **MATLAB Versions**: 2024b (tested with MATLAB Engine API)
*   **Operating System**: Windows 10/11 with PowerShell
*   **Browsers**: Chrome, Firefox, Edge (WebSocket support required)
*   **Dependencies**: EventLet, Flask-SocketIO, Requests, matlabengine

## Troubleshooting

### Common Issues & Solutions

#### **PowerShell Script Errors**
- **Syntax Error "Unexpected token '}'​"**: Fixed in latest version
- **Execution Policy**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Permission Issues**: Run PowerShell as Administrator if needed

#### **Python/MATLAB Integration**
- **MATLAB Engine not found**: Ensure MATLAB Engine for Python is installed correctly
- **Version incompatibility**: Check [MATLAB Python Compatibility](https://uk.mathworks.com/support/requirements/python-compatibility.html)
- **Import errors**: Verify virtual environment activation and dependency installation
- **EventLet issues**: EventLet automatically installs with requirements.txt

#### **Browser/Network Issues**
- **Multiple tabs opening**: Fixed in latest PowerShell script (now opens single tab)
- **Port conflicts**: Use `-Port` parameter to specify different port
- **WebSocket connection failed**: Check firewall settings and browser WebSocket support
- **Cost display issues**: Ensure JavaScript is enabled for real-time cost updates

#### **Application Performance**
- **Slow response**: Check MATLAB engine initialization and system resources
- **Memory issues**: Monitor Python process memory usage during long simulations
- **Data export problems**: Ensure sufficient disk space and write permissions
- **Cost calculation errors**: Verify electricity pricing configuration and grid data

## Contributing

This project is part of the **ENG30002 Engineering Technology Sustainability Project** at Swinburne Sarawak. 

### Development Guidelines
*   **Code Style**: Follow PEP 8 for Python, use meaningful variable names
*   **Documentation**: Update README.md and inline comments for new features
*   **Testing**: Test all changes with both frontend and MATLAB integration
*   **Performance**: Consider real-time performance impact of modifications
*   **Cost Tracking**: Ensure new features integrate properly with electricity cost tracking

## License

This project is developed for educational purposes as part of the Engineering Technology Sustainability Project at Swinburne University of Technology Sarawak Campus.

---

**Project Status**: ✅ **FULLY OPERATIONAL & ENHANCED**  
**Last Updated**: January 2025  
**Version**: Production v2.0 (Cost Tracking + Performance Optimized)  
**Setup Method**: `.\setup_and_run.ps1` (Recommended)  
**Access**: http://localhost:5000  
**Compatibility**: Python 3.9+ | MATLAB 2024b | Windows 10/11

### Recent Achievements
- ✅ **Electricity cost tracking with real-time calculation**
- ✅ **EventLet integration for optimal WebSocket performance**
- ✅ **Automatic simulation startup for immediate system readiness**
- ✅ **PowerShell automation script fully functional**
- ✅ **Single browser tab opening (fixed duplicate issue)**
- ✅ **MATLAB Engine integration working perfectly**
- ✅ **Real-time WebSocket communication established**
- ✅ **4-vehicle battery monitoring with cost tracking**
- ✅ **Zero syntax errors in all components**
- ✅ **Malaysian Ringgit (RM) cost tracking integration**
- ✅ **Peak/off-peak electricity pricing (8 AM - 10 PM peak hours)**
- ✅ **Comprehensive CSV export with cost data**
