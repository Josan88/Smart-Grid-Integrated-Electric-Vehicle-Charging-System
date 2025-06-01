# Smart Grid-Integrated Electric Vehicle Charging System

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![MATLAB](https://img.shields.io/badge/MATLAB-R2024b-orange.svg)](https://mathworks.com)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](#project-status)

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Installation Guide](#installation-guide)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [User Guide](#user-guide)
- [API Documentation](#api-documentation)
- [Performance & Optimization](#performance--optimization)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## Project Overview

The **Smart Grid-Integrated Electric Vehicle (EV) Charging System** is a comprehensive web-based simulation platform that models and visualizes the complexities of EV charging infrastructure integrated with renewable energy sources and smart grid technology. This system provides real-time monitoring, cost analysis, and performance optimization for sustainable energy management.

### 🎯 **Primary Objectives**
- Model smart grid interactions with renewable energy integration
- Optimize EV charging strategies for cost and efficiency
- Provide real-time monitoring and control capabilities
- Analyze electricity costs with peak/off-peak pricing
- Demonstrate sustainable energy management practices

### 🏆 **Academic Context**
This project is part of the **ENG30002 Engineering Technology Sustainability Project** at Swinburne University of Technology Sarawak Campus, focusing on practical applications of sustainable energy technologies.

## Key Features

### 🚗 **Advanced Simulation Engine**
- **Real-time MATLAB Integration**: Direct interface with Simulink models via Python Engine API
- **Dynamic Speed Control**: Adjustable simulation speed (0.25x to 10x) for detailed analysis
- **Continuous Operation**: Point-by-point data emission with automatic progression
- **Parameter Persistence**: Intelligent handling of user-defined vs simulation-calculated values
- **Automatic Startup**: System begins simulation immediately upon launch

### 📊 **Comprehensive Visualization**
- **2D System Dashboard**: Interactive SVG-based visualization of energy flows
- **Real-time Monitoring**: Live updates for all system components
- **Animated Energy Flows**: Visual representation of power distribution between components
- **Color-coded Status**: Intuitive visual feedback for system health and performance
- **Progress Indicators**: Modern progress bars replacing traditional charts for better UX

### 💰 **Advanced Cost Management**
- **Real-time Cost Calculation**: Live electricity cost tracking based on grid usage
- **Peak/Off-Peak Pricing**: Time-based electricity rates (8 AM - 10 PM peak hours)
- **Malaysian Ringgit Support**: Localized pricing (RM 0.229/kWh peak, RM 0.139/kWh off-peak)
- **Cumulative Tracking**: Detailed cost breakdown and historical analysis
- **Export Functionality**: CSV export with comprehensive cost data
- **Configurable Pricing**: User-defined electricity rates and time periods

### 🔋 **Battery Management System**
- **Multi-level Monitoring**: System battery + 4 individual EV bay batteries
- **State-of-Charge Tracking**: Real-time SOC with color-coded status indicators
- **Charging Optimization**: Intelligent charging strategies based on grid conditions
- **Auto-completion**: Fully charged EVs (≥99.9%) automatically released from bays
- **User Control**: Manual override capabilities for bay occupancy and charge levels

### 🌞 **Solar PV Integration**
- **NREL PVWatts V8 API**: Real-world solar generation data
- **Location-specific Data**: Kuching, Sarawak coordinates (1.532°N, 110.357°E)
- **Hourly Resolution**: 8,760 data points for full-year simulation
- **Caching System**: Local caching for improved performance and offline capability
- **Configurable Parameters**: System capacity, tilt, azimuth, and efficiency settings

### 🔌 **EV Charging Infrastructure**
- **4-Bay Monitoring**: Individual tracking of charging bays with battery levels
- **Dynamic Charging Rates**: Variable charging speeds based on grid conditions
- **Occupancy Management**: Automated bay status updates with user override
- **Cost per Bay**: Individual cost tracking for each charging session
- **Smart Scheduling**: Peak/off-peak charging optimization

## Technology Stack

### **Core Technologies**
```
Frontend: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.0
Backend: Python 3.9+, Flask 2.3.3, Flask-SocketIO 5.3.6
Simulation: MATLAB R2024b, Simulink, MATLAB Engine for Python
Real-time: Socket.IO, EventLet for async WebSocket handling
APIs: NREL PVWatts V8, RESTful APIs with JSON
```

### **Performance & Optimization**
- **EventLet**: Asynchronous WebSocket handling for high-performance real-time updates
- **Data Filtering**: Startup artifact removal and intelligent data downsampling
- **WebSocket Throttling**: Configurable message rate limiting (100ms default)
- **Caching System**: File-based caching for PVWatts data with 30-day expiry
- **Memory Management**: Optimized data structures for continuous operation

### **Development Tools**
- **Automation**: PowerShell setup script for one-command deployment
- **Dependencies**: Requirements.txt with pinned versions for reproducibility
- **Logging**: Comprehensive logging system for debugging and monitoring
- **Error Handling**: Robust exception handling with user-friendly messages

## Quick Start

### 🚀 **One-Command Setup (Recommended)**
```powershell
# Clone and run the system
.\run.ps1
```

### 🎛️ **Custom Configuration**
```powershell
# Custom port
.\run.ps1 -Port 8080

# Skip dependency installation
.\run.ps1 -SkipInstall

# View all options
.\run.ps1 -Help
```

### 🌐 **Access Dashboard**
Open your browser to: **http://localhost:5000**

## Installation Guide

### **Prerequisites**
- **Python 3.9+** (Recommended: 3.12+)
- **MATLAB R2024b** with Simulink
- **Windows 10/11** with PowerShell
- **Modern Web Browser** (Chrome, Firefox, Edge)

### **Method 1: Automated Setup**
The PowerShell script handles all installation steps automatically:

```powershell
# Download or clone the project
git clone [repository-url]
cd website

# Run automated setup
.\run.ps1
```

**What the script does:**
- ✅ Validates Python version (3.9+ required)
- ✅ Creates virtual environment (if needed)
- ✅ Installs all dependencies from requirements.txt
- ✅ Configures MATLAB Engine for Python
- ✅ Starts the Flask application
- ✅ Opens browser to dashboard

### **Method 2: Manual Installation**

#### **Step 1: Python Environment**
```powershell
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### **Step 2: MATLAB Engine Installation**
```powershell
# Navigate to MATLAB Python engine directory
cd "C:\Program Files\MATLAB\R2024b\extern\engines\python"

# Install MATLAB Engine for Python
python -m pip install .
```

#### **Step 3: Start Application**
```powershell
# Return to project directory
cd path\to\website

# Start the application
python app.py --port 5000 --host 0.0.0.0
```

### **Verification**
Test the installation by importing the MATLAB engine:
```python
import matlab.engine
print("MATLAB engine imported successfully!")
```

## System Architecture

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│   MATLAB        │   Python        │   WebSocket     │   Frontend      │
│   Simulink      │   Flask         │   Socket.IO     │   Bootstrap     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ CompleteV1.slx  │ app.py          │ EventLet        │ index.html      │
│ Simulation      │ simulation.py   │ Real-time       │ 2D Visualization│
│ Model           │ pvwatts.py      │ Communication   │ Progress Bars   │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Battery Model   │ Cost Tracking   │ Live Updates    │ Energy Flows    │
│ PV Model        │ Data Processing │ Point-by-Point  │ Status Indicator│
│ Grid Model      │ API Integration │ State Sync      │ Control Panels  │
│ EV Models (4)   │ Parameter Mgmt  │ Error Handling  │ Export Features │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### **Data Flow**
1. **MATLAB Simulink** executes CompleteV1.slx model with parameters
2. **Python Backend** processes results and manages state
3. **WebSocket Layer** streams real-time data to frontend
4. **Frontend Dashboard** visualizes data and provides controls
5. **User Interactions** flow back through the same pipeline

## Project Structure

```
📁 website/
├── 🚀 run.ps1        # Automated PowerShell setup (VERIFIED)
├── 🐍 app.py                   # Main Flask application (1,800+ lines)
├── 🔧 simulation.py            # MATLAB-Python interface
├── ☀️ pvwatts.py              # NREL PVWatts API integration
├── 📋 requirements.txt         # Python dependencies
├── 🧮 CompleteV1.slx          # MATLAB Simulink model
├── 📊 sim_the_model.m         # MATLAB simulation script
├── 📄 README.md               # This documentation
├── 📄 SETUP_GUIDE.md          # Detailed setup instructions
│
├── 📁 templates/
│   └── 🌐 index.html          # Main dashboard interface
│
├── 📁 static/
│   ├── 📁 css/
│   │   └── 🎨 style.css       # Custom styling and animations
│   └── 📁 js/
│       └── ⚡ script.js       # Frontend logic and visualization
│
├── 📁 tests/                  # Testing scripts
├── 📁 slprj/                  # MATLAB Simulink project files
├── 💾 pvwatts_response.json   # Cached PVWatts data
└── 🗂️ __pycache__/           # Python bytecode cache
```

### **Key Components**
- **`app.py`**: Central Flask application with WebSocket handling, API endpoints, and cost tracking
- **`simulation.py`**: MATLAB engine interface with result parsing and data filtering
- **`run.ps1`**: Production-ready automation script with error handling
- **`index.html`**: Complete dashboard with 2D visualization and real-time controls
- **`script.js`**: Frontend logic for real-time updates and user interactions

## User Guide

### **Dashboard Overview**
The main interface provides comprehensive monitoring and control:

#### **🎮 Control Panel**
- **Simulation Speed**: Adjust from 0.25x to 10x for detailed analysis
- **Start/Stop**: Control simulation execution with custom start dates
- **Parameter Controls**: Real-time adjustment of system parameters
- **Export Data**: Download CSV files with complete simulation data

#### **📊 System Monitor**
- **Battery Management**: System battery level with charging/discharging status
- **Solar PV System**: Real-time power generation with efficiency indicators
- **Grid Connection**: Power flow with peak/off-peak status and cost display
- **EV Charging Bays**: Individual monitoring of 4 charging stations

#### **💰 Cost Analysis**
- **Real-time Costs**: Live electricity cost calculation and display
- **Peak/Off-Peak Rates**: Time-based pricing with status indicators
- **Cumulative Tracking**: Running total of electricity costs
- **Rate Configuration**: User-defined electricity pricing

### **Parameter Configuration**

#### **Simulation Parameters**
```
Battery Output: 30.0 kW (adjustable)
PV Output: 10.0 kW (from PVWatts data)
Battery SOC: 0-100% (user-configurable)
Bay Occupancy: Individual bay control
Bay Charge Levels: 0-100% per bay
```

#### **PVWatts Settings**
```
Location: Kuching, Sarawak (1.532°N, 110.357°E)
System Capacity: 26.02 kW
Module Type: Standard/Premium/Thin Film
Array Type: Fixed/Tracking options
Tilt Angle: 20° (configurable)
Azimuth: 180° South-facing (configurable)
```

#### **Electricity Pricing**
```
Peak Rate: RM 0.229/kWh (8 AM - 10 PM)
Off-Peak Rate: RM 0.139/kWh (10 PM - 8 AM)
Currency: Malaysian Ringgit (RM)
Time Zones: Configurable peak hours
```

### **Advanced Features**

#### **Auto-completion System**
- EVs reaching ≥99.9% charge are automatically released
- Bays reset to 0% and marked as available
- Prevents blocking of charging infrastructure

#### **Data Export**
- Comprehensive CSV export with timestamps
- Cost data included in all exports
- Configurable data range selection
- Real-time and historical data

## API Documentation

### **RESTful Endpoints**

#### **Simulation Control**
```http
POST /api/simulation/control
Content-Type: application/json

{
  "action": "start|stop",
  "start_date": "2024-01-01",
  "start_time": "08:00:00"
}
```

#### **Parameter Management**
```http
GET /api/simulation/params
POST /api/simulation/params
Content-Type: application/json

{
  "battery_soc": 50.0,
  "bay1_occupied": 1.0,
  "bay1_percentage": 25.0,
  "PVOutput": 15.0
}
```

#### **Cost Management**
```http
GET /api/electricity/pricing
POST /api/electricity/pricing
Content-Type: application/json

{
  "peak_rate": 0.229,
  "off_peak_rate": 0.139,
  "currency": "RM",
  "peak_start_hour": 8,
  "peak_end_hour": 22
}
```

### **WebSocket Events**

#### **Client → Server**
```javascript
// Update simulation parameters
socket.emit('update_simulation_params', {
  battery_soc: 75.0,
  bay2_occupied: 1.0
});

// Control simulation speed
socket.emit('set_simulation_speed', {
  speed: 2.0
});
```

#### **Server → Client**
```javascript
// Real-time simulation data
socket.on('new_simulation_point', (data) => {
  // Process real-time data point
});

// Simulation state updates
socket.on('simulation_state', (state) => {
  // Update UI with current state
});
```

## Performance & Optimization

### **Real-time Performance**
- **Data Rate**: Point-by-point emission with configurable speed
- **WebSocket Throttling**: 100ms minimum between messages
- **Memory Usage**: Optimized data structures for continuous operation
- **CPU Efficiency**: EventLet async processing for WebSocket handling

### **Data Management**
- **Filtering**: Automatic removal of simulation startup artifacts
- **Downsampling**: Optional data reduction for large datasets (1000+ points)
- **Caching**: PVWatts data cached for 30 days with automatic refresh
- **Export Optimization**: Efficient CSV generation for large datasets

### **System Requirements**
```
Minimum: 4GB RAM, 2-core CPU, Windows 10
Recommended: 8GB RAM, 4-core CPU, Windows 11
Storage: 2GB free space for dependencies and data
Network: Internet connection for PVWatts API
```

## Troubleshooting

### **Common Issues**

#### **🔧 PowerShell Script**
```powershell
# Issue: Execution policy error
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Issue: Multiple browser tabs
# Fixed in latest version - now opens single tab

# Issue: Permission denied
# Run PowerShell as Administrator
```

#### **🐍 Python/MATLAB**
```python
# Issue: MATLAB Engine not found
# Solution: Reinstall MATLAB Engine for Python
cd "C:\Program Files\MATLAB\R2024b\extern\engines\python"
python -m pip install .

# Issue: Version incompatibility
# Check: https://uk.mathworks.com/support/requirements/python-compatibility.html
```

#### **🌐 Web Application**
```javascript
// Issue: WebSocket connection failed
// Check: Firewall settings and browser WebSocket support

// Issue: Real-time updates not working
// Verify: EventLet installation and Socket.IO connection

// Issue: Cost display problems
// Ensure: JavaScript enabled and valid pricing configuration
```

### **Performance Issues**
- **Slow MATLAB startup**: Pre-initialize engine during application startup
- **Memory leaks**: Monitor Python process during long simulations
- **WebSocket lag**: Adjust throttling settings in app.py
- **Export failures**: Check disk space and file permissions

### **Debugging Tools**
```python
# Enable debug logging
logging.getLogger().setLevel(logging.DEBUG)

# Check simulation state
GET /api/simulation/state

# Monitor WebSocket events
# Use browser developer tools → Network → WS
```

## Development

### **Development Setup**
```powershell
# Development environment
python -m venv .venv-dev
.venv-dev\Scripts\activate
pip install -r requirements.txt

# Run in development mode
python app.py --debug
```

### **Code Structure Guidelines**
- **Python**: Follow PEP 8, use type hints where appropriate
- **JavaScript**: ES6+ features, modular structure
- **CSS**: BEM methodology, responsive design principles
- **Documentation**: Update README and inline comments for new features

### **Testing Strategy**
```python
# Unit tests for simulation logic
pytest tests/test_simulation.py

# Integration tests for API endpoints
pytest tests/test_api.py

# Frontend testing with browser automation
# Manual testing for WebSocket functionality
```

### **Performance Considerations**
- **Real-time Updates**: Consider impact on WebSocket message frequency
- **Memory Usage**: Monitor data structure sizes during development
- **MATLAB Integration**: Minimize engine start/stop cycles
- **Cost Tracking**: Ensure efficient calculation algorithms

### **Contributing Guidelines**
1. **Feature Development**: Create feature branches from main
2. **Code Review**: All changes require review before merging
3. **Testing**: Test both frontend and MATLAB integration
4. **Documentation**: Update README and API documentation
5. **Performance**: Profile changes for real-time impact

## License

This project is developed for educational purposes as part of the **Engineering Technology Sustainability Project** at Swinburne University of Technology Sarawak Campus.

### **Academic Use**
- Educational and research purposes
- Non-commercial applications
- Academic publication with attribution

### **Third-Party Components**
- **NREL PVWatts**: Subject to NREL terms of use
- **MATLAB**: Requires valid MATLAB license
- **Flask/Python**: Open source licenses
- **Bootstrap**: MIT License

---

## Project Status

**Status**: ✅ **PRODUCTION READY**  
**Version**: v2.1 (Enhanced Documentation + Performance Optimized)  
**Compatibility**: Python 3.9+ | MATLAB R2024b | Windows 10/11

### **✅ Verified Functionality**
- [x] **MATLAB Integration**: Engine API working with Python 3.12.10
- [x] **Real-time WebSocket**: Socket.IO with EventLet optimization
- [x] **Cost Tracking**: Live electricity cost calculation and export
- [x] **PowerShell Automation**: One-command deployment working
- [x] **4-Bay EV Monitoring**: Individual battery and cost tracking
- [x] **PVWatts Integration**: Solar data caching and API calls
- [x] **CSV Export**: Complete data export with cost information
- [x] **Auto-completion**: Fully charged EVs automatically released
- [x] **Peak/Off-Peak Pricing**: Time-based electricity rates
- [x] **2D Visualization**: Animated energy flows and status indicators

### **🚀 Recent Enhancements**
- **Enhanced Documentation**: Comprehensive README with technical details
- **API Documentation**: Complete endpoint and WebSocket event documentation
- **Performance Metrics**: Detailed system requirements and optimization guide
- **Troubleshooting Guide**: Comprehensive issue resolution procedures
- **Development Guidelines**: Code structure and contribution guidelines

### **📊 System Metrics**
- **Codebase**: 4,000+ lines of production code
- **Real-time Streams**: 9 active data channels
- **Cost Tracking**: Real-time calculation with RM currency
- **Performance**: <100ms WebSocket response time
- **Reliability**: Automatic error recovery and state management

**Setup Command**: `.\run.ps1`  
**Access URL**: http://localhost:5000  
**Documentation**: Complete technical and user documentation included
