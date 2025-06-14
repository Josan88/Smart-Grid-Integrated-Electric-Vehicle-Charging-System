// Main JavaScript for the simulation dashboard

// Socket.IO connection
const socket = io();

// DOM elements - Declare globally, assign in DOMContentLoaded
let startSimulationBtn;
let stopSimulationBtn;
let simulationLog;
let clearLogBtn;
let pvwattsForm;
let simulationSpeedSelect;
let currentSpeedDisplay; // Add this new element
let simStartMonthSelect; // Updated for month selection
let simStartDaySelect;   // Updated for day selection
let simStartHourSelect;  // Updated for hour selection
let useCurrentLocationBtn; // For PVWatts location
let currentLocationDisplay; // To display fetched location

// Charts - removed for simplified dashboard
// let batteryChart;
// let evChargingChart;
// let gridChart;

// Data buffers for charts (limit to last 100 points)
const MAX_DATA_POINTS = 100;
const chartData = {
    time: [],
    batteryValues: [],
    batteryRecharge: [],
    evRecharge: [],
    gridRequest: [],
    vehicle1BatteryLevel: [],
    vehicle2BatteryLevel: [],
    vehicle3BatteryLevel: [],
    vehicle4BatteryLevel: [],
    electricityCost: [],
    cumulativeCost: [],
    pvOutput: []  // Add PV output data tracking
};

// Solar performance tracking variables
let dailyPeakPV = 0;  // Track peak PV output for the current day
let currentDate = '';  // Track current simulation date to reset daily peak

// Parameters management - Declare globally, assign in DOMContentLoaded
let paramInputs;
let rangeValueDisplays = {}; // Initialize as empty, populate in DOMContentLoaded

// Current simulation state
let simulationRunning = false;

// Debounce function to prevent too many form updates
let paramChangeTimeout = null;
const PARAM_CHANGE_DEBOUNCE_MS = 500; // 500ms debounce

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {    // Assign DOM elements now that the DOM is ready
    startSimulationBtn = document.getElementById('start-simulation-btn');
    stopSimulationBtn = document.getElementById('stop-simulation-btn');
    simulationLog = document.getElementById('simulation-log');
    clearLogBtn = document.getElementById('clear-log');
    pvwattsForm = document.getElementById('pvwatts-form');
    simulationSpeedSelect = document.getElementById('simulation-speed-select');
    currentSpeedDisplay = document.getElementById('current-speed-display');
    simStartMonthSelect = document.getElementById('sim-start-month');
    simStartDaySelect = document.getElementById('sim-start-day');
    simStartHourSelect = document.getElementById('sim-start-hour');
    useCurrentLocationBtn = document.getElementById('use-current-location-btn');
    currentLocationDisplay = document.getElementById('current-location-display');

    paramInputs = document.querySelectorAll('.param-input');
    rangeValueDisplays = {
        'bay1_percentage': document.getElementById('bay1_percentage_value'),
        'bay2_percentage': document.getElementById('bay2_percentage_value'),
        'bay3_percentage': document.getElementById('bay3_percentage_value'),
        'bay4_percentage': document.getElementById('bay4_percentage_value'),
        'battery_soc': document.getElementById('battery_soc_value')
    };    // Check if essential elements were found
    if (!startSimulationBtn) {
        console.error("CRITICAL: #start-simulation-btn not found during DOMContentLoaded!");
    }
    // Add more checks for other critical elements if necessary    initializeCharts(); // Keep function call but charts are disabled
    setupEventListeners();
    fetchInitialData();
    initialize2DVisualization(); // Initialize 2D system visualization
});

// Socket.IO event handlers
socket.on('connect', () => {
    logMessage('Connected to server', 'success');
});

socket.on('new_simulation_point', (data) => {
    processSingleDataPoint(data);
    // Update simulation time display with data from the point itself
    if (data.date && data.time) {
        const dateDisplay = document.getElementById('simulation-date');
        if (dateDisplay) {
            dateDisplay.textContent = data.date;
        }
        // Removed else console.error for brevity, already checked in initial DOM load
        
        const timeDisplay = document.getElementById('simulation-time');
        if (timeDisplay) {
            timeDisplay.textContent = data.time;
        }
        // Removed else console.error for brevity

        // Populate the custom dropdown selectors if simulation is not running
        // and these values are part of the initial state sent by the server.
        if (!simulationRunning && data.date) {
            try {
                // Parse the date from the data
                const dateParts = data.date.split('-');
                const year = parseInt(dateParts[0]);
                const month = parseInt(dateParts[1]);
                const day = parseInt(dateParts[2]);
                
                // Parse the time from the data
                const timeParts = data.time.split(':');
                const hour = parseInt(timeParts[0]);
                
                // Update dropdowns
                if (simStartMonthSelect) simStartMonthSelect.value = month;
                // Populate days based on the current month
                populateDaysInMonth();
                if (simStartDaySelect) simStartDaySelect.value = day;
                if (simStartHourSelect) simStartHourSelect.value = hour;
            } catch (error) {
                console.error('Error parsing date/time for dropdown selectors:', error);
            }
        }
    }
    
    logMessage('Received current simulation state', 'info');
});

socket.on('disconnect', () => {
    logMessage('Disconnected from server', 'error');
    simulationRunning = false;
    updateUIState();
});

socket.on('simulation_data', (data) => {
    processSimulationData(data);
});

socket.on('simulation_time_update', (data) => {
    // Note: updateSimulationTime function was removed as part of history removal
    // This event handler can be removed if no longer needed
});

socket.on('simulation_state', (data) => {
    simulationRunning = data.running;
    updateUIState();
    
    // Update form values with current parameters
    if (data.params) {
        updateParamFormValues(data.params);
    }
    
    // Update PVWatts form values
    if (data.pvwatts) {
        updatePVWattsFormValues(data.pvwatts);
    }
    
    // Update speed display if available
    if (data.speed) {
        if (simulationSpeedSelect) {
            simulationSpeedSelect.value = data.speed.toString();
        }
        updateSpeedDisplay(data.speed);
    }
    
    // Update simulation time display
    if (data.date && data.time) {
        const dateDisplay = document.getElementById('simulation-date');
        if (dateDisplay) {
            dateDisplay.textContent = data.date;
        } else {
            console.error("DOM element #simulation-date not found.");
        }
        
        const timeDisplay = document.getElementById('simulation-time');
        if (timeDisplay) {
            timeDisplay.textContent = data.time;
        } else {
            console.error("DOM element #simulation-time not found.");
        }
    }

    // Remove this redundant grid peak status update
    // Grid peak status is now handled in updateGridComponent function
    
    logMessage('Received current simulation state', 'info');
});

socket.on('simulation_error', (data) => {
    logMessage(`Simulation error: ${data.message}`, 'error');
});

socket.on('simulation_stopped', (data) => {
    simulationRunning = false;
    updateUIState();
    logMessage(data.message, 'info');
});

socket.on('params_updated', (data) => {
    if (data.success) {
        logMessage(data.message, 'success');
        if (data.params) {
            updateParamFormValues(data.params);
        }
    } else {
        logMessage(data.message, 'error');
    }
});

socket.on('pvwatts_settings_updated', (data) => {
    if (data.success) {
        logMessage(data.message, 'info');
        if (data.settings) {
            updatePVWattsFormValues(data.settings);
        }
    } else {
        logMessage(data.message, 'error');
    }
});

socket.on('pvwatts_updated', (data) => {
    if (data.success) {
        logMessage(data.message, 'success');
    } else {
        logMessage(data.message, 'error');
    }
});

socket.on('simulation_speed_updated', (data) => {
    if (data.success) {
        logMessage(data.message, 'success');
        if (simulationSpeedSelect && data.speed) {
            simulationSpeedSelect.value = data.speed.toString();
            updateSpeedDisplay(data.speed);
        }
    } else {
        logMessage(data.message, 'error');
    }
});

// Function to initialize charts - removed for simplified dashboard
// Charts have been replaced with progress bars and summary cards
function initializeCharts() {
    console.log('Chart initialization skipped - using simplified dashboard');
    // No chart initialization needed - using progress bars and visual indicators instead
}

// Function to populate days in month based on the selected month
function populateDaysInMonth() {
    const month = parseInt(simStartMonthSelect.value);
    const year = 2020; // Fixed to 2020
    
    // Clear current options
    simStartDaySelect.innerHTML = '';
    
    // Get number of days in the month
    const daysInMonth = new Date(year, month, 0).getDate();
    
    // Populate days dropdown
    for (let day = 1; day <= daysInMonth; day++) {
        const option = document.createElement('option');
        option.value = day;
        option.textContent = day;
        simStartDaySelect.appendChild(option);
    }
}

// Setup event listeners for buttons and forms
function setupEventListeners() {
    // Simulation control buttons
    startSimulationBtn.addEventListener('click', startSimulation);
    stopSimulationBtn.addEventListener('click', stopSimulation);    // Export data button
    const exportDataBtn = document.getElementById('export-data-btn');
    if (exportDataBtn) {
        exportDataBtn.addEventListener('click', exportSimulationData);
    }
      // Setup month change event to update days dropdown
    if (simStartMonthSelect) {
        simStartMonthSelect.addEventListener('change', populateDaysInMonth);
        // Also trigger auto-apply when month changes
        simStartMonthSelect.addEventListener('change', triggerAutoApply);
        // Initialize days for initial month selection
        populateDaysInMonth();
    }
    
    // Add event listeners for day and hour selectors
    if (simStartDaySelect) {
        simStartDaySelect.addEventListener('change', triggerAutoApply);
    }
    
    if (simStartHourSelect) {
        simStartHourSelect.addEventListener('change', triggerAutoApply);    }
      // Set up auto-apply for parameter inputs
    setupAutoApplyForInputs();
    
    // Set up electricity pricing event listeners
    setupElectricityPricingEventListeners();
    
    // Load current electricity pricing configuration
    loadElectricityPricing();
    
    // PVWatts form submission
    pvwattsForm.addEventListener('submit', (e) => {
        e.preventDefault();
        updatePVWattsSettings();
    });

    // PVWatts use current location button
    if (useCurrentLocationBtn) {
        useCurrentLocationBtn.addEventListener('click', fetchAndSetCurrentLocation);
    }
    
    // Clear log button
    clearLogBtn.addEventListener('click', () => {
        simulationLog.innerHTML = '';
        logMessage('Log cleared', 'info');
    });
    
    // Set up range input value displays and change handlers
    setupRangeInputs();

    // Simulation speed control
    if (simulationSpeedSelect) {
        simulationSpeedSelect.addEventListener('change', (event) => {
            const speed = parseFloat(event.target.value);
            updateSpeedDisplay(speed); // Update display immediately
            socket.emit('set_simulation_speed', { speed: speed });
            logMessage(`Setting simulation speed to ${speed}x...`, 'info');
        });
        
        // Initialize speed display on page load
        const initialSpeed = parseFloat(simulationSpeedSelect.value);
        updateSpeedDisplay(initialSpeed);
    }
}

// Setup range input displays and handlers
function setupRangeInputs() {
    // Update range value displays
    paramInputs.forEach(input => {
        if (input.type === 'range') {
            const param = input.dataset.param;
            if (rangeValueDisplays[param]) {
                input.addEventListener('input', () => {
                    rangeValueDisplays[param].textContent = `${input.value}%`;
                });
            }
        }
    });
}

// Setup auto-apply for inputs
function setupAutoApplyForInputs() {
    // Add change/input listeners to all parameter inputs
    paramInputs.forEach(input => {
        // For checkboxes and number inputs, use 'change' event
        if (input.type === 'checkbox' || input.type === 'number') {
            input.addEventListener('change', triggerAutoApply);
        }
        // For range inputs, use both 'input' and 'change' events
        // 'input' provides real-time updates during sliding, 'change' catches the final value
        else if (input.type === 'range') {
            input.addEventListener('change', triggerAutoApply);
            // For continuous sliders, we can optionally use 'input' event with longer debounce
            // Commented out to prevent too many updates during sliding
            // input.addEventListener('input', triggerAutoApply);
        }
    });
    
    // Log message to inform users of the auto-apply behavior
    logMessage('Form inputs will automatically apply changes when modified', 'info');
}

// Set up event listeners for electricity pricing functionality
function setupElectricityPricingEventListeners() {
    // Pricing configuration form
    const pricingForm = document.getElementById('pricing-config-form');
    if (pricingForm) {
        pricingForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(pricingForm);
            updateElectricityPricing(formData);
        });
    }
    
    // Reset costs button
    const resetCostsBtn = document.getElementById('reset-costs-btn');
    if (resetCostsBtn) {
        resetCostsBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to reset all electricity cost data?')) {
                resetElectricityCosts();
            }
        });
    }
}

// Trigger auto-apply with debouncing
function triggerAutoApply() {
    // Clear any pending timeout
    if (paramChangeTimeout) {
        clearTimeout(paramChangeTimeout);
    }
    
    // Set a new timeout
    paramChangeTimeout = setTimeout(() => {
        logMessage('Auto-applying parameter changes...', 'info');
        applySimulationParameters();
        paramChangeTimeout = null;
    }, PARAM_CHANGE_DEBOUNCE_MS);
}

// Fetch initial data from the server
function fetchInitialData() {
    // Fetch current simulation parameters
    fetch('/api/simulation/params')
        .then(response => response.json())
        .then(data => {
            updateParamFormValues(data);
        })
        .catch(error => {
            logMessage(`Error fetching simulation parameters: ${error}`, 'error');
        });
    
    // Fetch current PVWatts settings
    fetch('/api/pvwatts/settings')
        .then(response => response.json())
        .then(data => {
            updatePVWattsFormValues(data);
        })
        .catch(error => {
            logMessage(`Error fetching PVWatts settings: ${error}`, 'error');
        });
}

// Start the simulation
function startSimulation() {
    // Get selected values from the dropdowns
    const month = parseInt(simStartMonthSelect.value);
    const day = parseInt(simStartDaySelect.value);
    const hour = parseInt(simStartHourSelect.value);
    
    // Format date and time strings for the API
    // Use padStart to ensure two digits for month and day
    const startDate = `2020-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
    const startTime = `${hour.toString().padStart(2, '0')}:00:00`; // Set minutes and seconds to 00:00
    
    let payload = { action: 'start' };
    if (startDate && startTime) {
        payload.start_date = startDate;
        payload.start_time = startTime;
        logMessage(`Requesting simulation start at ${startDate} ${startTime}`, 'info');
    } else {
        logMessage('Requesting simulation start with default datetime', 'info');
    }

    fetch('/api/simulation/control', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            simulationRunning = true;
            updateUIState();
            logMessage(data.message, 'success');
        } else {
            logMessage(data.message, 'error');
        }
    })
    .catch(error => {
        logMessage(`Error starting simulation: ${error}`, 'error');
    });
}

// Stop the simulation
function stopSimulation() {
    fetch('/api/simulation/control', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: 'stop' })
    })
    .then(response => response.json())
    .then(data => {
        logMessage(data.message, 'info');
        // Note: We don't update UI state here, we wait for the 'simulation_stopped' event
    })
    .catch(error => {
        logMessage(`Error stopping simulation: ${error}`, 'error');
    });
}

// Apply simulation parameters
function applySimulationParameters() {
    const params = {};
    
    paramInputs.forEach(input => {
        const param = input.dataset.param;
        let value;
        
        if (input.type === 'checkbox') {
            // Use data-value attribute for checkbox values
            value = input.checked ? parseFloat(input.dataset.value) : parseFloat(input.dataset.offValue || "0.0");
        } else if (input.type === 'range') {
            value = parseFloat(input.value);
        } else if (input.type === 'number') {
            value = parseFloat(input.value);
        }
        
        if (param && !isNaN(value)) {
            params[param] = value;
        }
    });
    
    // Get selected date/time values
    if (simStartMonthSelect && simStartDaySelect && simStartHourSelect) {
        const month = parseInt(simStartMonthSelect.value);
        const day = parseInt(simStartDaySelect.value);
        const hour = parseInt(simStartHourSelect.value);
        
        // Format date and time strings for the server
        const startDate = `2020-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
        const startTime = `${hour.toString().padStart(2, '0')}:00:00`;
        
        // Add date parameters to the params object
        params.initial_start_date = startDate;
        params.initial_start_time = startTime;
    }
    
    // Check if simulation is running
    if (simulationRunning) {
        logMessage('Stopping simulation to apply parameter changes...', 'info');
        
        // Stop the simulation first
        fetch('/api/simulation/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action: 'stop' })
        })
        .then(response => response.json())
        .then(data => {
            // Now apply the parameters
            socket.emit('update_simulation_params', params);
            logMessage('Applying simulation parameters...', 'info');
            
            // Set up listener for 'simulation_stopped' event to restart after parameters are applied
            const restartAfterStop = function(data) {
                // Remove this listener to avoid multiple restarts
                socket.off('simulation_stopped', restartAfterStop);
                
                // Give a short delay to ensure parameters are fully applied
                setTimeout(() => {
                    logMessage('Restarting simulation with new parameters...', 'info');
                    startSimulation();
                }, 500);
            };
            
            // Add the temporary event listener
            socket.on('simulation_stopped', restartAfterStop);
        })
        .catch(error => {
            logMessage(`Error stopping simulation to apply parameters: ${error}`, 'error');
        });
    } else {
        // If not running, just apply the parameters
        socket.emit('update_simulation_params', params);
        logMessage('Applying simulation parameters...', 'info');
    }
}

// Update PVWatts settings
function updatePVWattsSettings() {
    const form = document.getElementById('pvwatts-form');
    const formData = new FormData(form);
    const settings = {};
    
    for (const [key, value] of formData.entries()) {
        settings[key] = value;
    }
    
    // Send settings to the server
    socket.emit('update_pvwatts_settings', settings);
    logMessage('Updating PVWatts settings...', 'info');
}

// Process simulation data received from the server
function processSimulationData(data) {
    // This function is kept for now if any old 'simulation_data' events are sent,
    // but primary data handling will be through 'new_simulation_point'.
    // It processes a batch of data, which might be useful for initial load or catch-up.
    logMessage(`Processing batch simulation data with ${data.time ? data.time.length : 0} points.`, 'info');

    if (data.time && data.time.length > 0) {
        const baseTime = chartData.time.length > 0 ? Math.max(...chartData.time) + 1 : 0;
          for (let i = 0; i < data.time.length; i++) {
            chartData.time.push(baseTime + data.time[i]);

            if (data.batt_values && i < data.batt_values.length) chartData.batteryValues.push(data.batt_values[i]);
            if (data.batt_recharge && i < data.batt_recharge.length) chartData.batteryRecharge.push(data.batt_recharge[i]);
            if (data.ev_recharge && i < data.ev_recharge.length) chartData.evRecharge.push(data.ev_recharge[i]);
            if (data.grid_request && i < data.grid_request.length) chartData.gridRequest.push(data.grid_request[i]);
            if (data.vehicle1_battery_level && i < data.vehicle1_battery_level.length) chartData.vehicle1BatteryLevel.push(data.vehicle1_battery_level[i]);
            if (data.vehicle2_battery_level && i < data.vehicle2_battery_level.length) chartData.vehicle2BatteryLevel.push(data.vehicle2_battery_level[i]);
            if (data.vehicle3_battery_level && i < data.vehicle3_battery_level.length) chartData.vehicle3BatteryLevel.push(data.vehicle3_battery_level[i]);
            if (data.vehicle4_battery_level && i < data.vehicle4_battery_level.length) chartData.vehicle4BatteryLevel.push(data.vehicle4_battery_level[i]);
        }        trimChartData();
        // updateCharts(); // Removed - no charts to update
        updateCurrentValues();        updateProgressIndicators(); // Update progress bars and visual indicators
        update2DVisualization(); // Update 2D system visualization
    }
}

function processSingleDataPoint(data) {
    // Store the last received data point globally for peak status calculation
    window.lastReceivedDataPoint = data;
    
    // Add data to buffers
    chartData.time.push(data.time_abs); // Use absolute time for chart labels
    chartData.batteryValues.push(data.batt_value);
    chartData.batteryRecharge.push(data.batt_recharge);
    chartData.evRecharge.push(data.ev_recharge);
    chartData.gridRequest.push(data.grid_request);
    chartData.vehicle1BatteryLevel.push(data.vehicle1_battery_level);
    chartData.vehicle2BatteryLevel.push(data.vehicle2_battery_level);
    chartData.vehicle3BatteryLevel.push(data.vehicle3_battery_level);
    chartData.vehicle4BatteryLevel.push(data.vehicle4_battery_level);
    
    // Add PV output data if available
    if (data.pv_output_watts !== undefined) {
        chartData.pvOutput.push(data.pv_output_watts);
    } else {
        chartData.pvOutput.push(0); // Default to 0 if no PV data
    }
    
    // Add cost data if available
    if (data.electricity_cost !== undefined) {
        chartData.electricityCost.push(data.electricity_cost);
    }
    if (data.cumulative_cost !== undefined) {
        chartData.cumulativeCost.push(data.cumulative_cost);
    }    trimChartData();
    // updateCharts(); // Removed - no charts to update    updateCurrentValues(); // Update dashboard numbers
    updateProgressIndicators(); // Update progress bars and visual indicators
    updateCostDisplay(data); // Update cost information
    updateSolarPerformance(data); // Update solar performance metrics
    update2DVisualization(); // Update 2D system visualization
}

// Removed redundant code that's causing the error
// The grid peak status is already handled in update2DVisualization -> updateGridComponent

function trimChartData() {
    if (chartData.time.length > MAX_DATA_POINTS) {
        const excess = chartData.time.length - MAX_DATA_POINTS;
        chartData.time.splice(0, excess);
        chartData.batteryValues.splice(0, excess);
        chartData.batteryRecharge.splice(0, excess);
        chartData.evRecharge.splice(0, excess);
        chartData.gridRequest.splice(0, excess);
        chartData.vehicle1BatteryLevel.splice(0, excess);
        chartData.vehicle2BatteryLevel.splice(0, excess);
        chartData.vehicle3BatteryLevel.splice(0, excess);
        chartData.vehicle4BatteryLevel.splice(0, excess);
        chartData.electricityCost.splice(0, excess);
        chartData.cumulativeCost.splice(0, excess);
        chartData.pvOutput.splice(0, excess);
    }
}

// Export simulation data to CSV
function exportSimulationData() {
    if (chartData.time.length === 0) {
        logMessage('No data to export', 'warning');
        return;
    }
      // Create CSV content
    let csvContent = 'Time (s),Battery Level (%),Battery Recharge (kW),EV Recharge (kW),Grid Request (kW),Vehicle 1 Battery (%),Vehicle 2 Battery (%),Vehicle 3 Battery (%),Vehicle 4 Battery (%)\n';
    
    // Combine all data points
    for (let i = 0; i < chartData.time.length; i++) {
        const row = [
            chartData.time[i] || '',
            chartData.batteryValues[i] || '',
            chartData.batteryRecharge[i] || '',
            chartData.evRecharge[i] || '',
            chartData.gridRequest[i] || '',
            chartData.vehicle1BatteryLevel[i] || '',
            chartData.vehicle2BatteryLevel[i] || '',
            chartData.vehicle3BatteryLevel[i] || '',
            chartData.vehicle4BatteryLevel[i] || ''
        ];
        csvContent += row.join(',') + '\n';
    }
    
    // Create a Blob and download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `simulation-data-${timestamp}.csv`;
    
    // Create and click a download link
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    logMessage(`Exported ${chartData.time.length} data points to ${filename}`, 'success');
}

// Remove or comment out the old updateSimulationTime function as its role is superseded
/*
function updateSimulationTime(data) {
    const dateDisplay = document.getElementById('simulation-date');
    const timeDisplay = document.getElementById('simulation-time');
    const currentHourDisplay = document.getElementById('current-hour');

    if (dateDisplay && data.date) {
        dateDisplay.textContent = data.date;
    } else if (!dateDisplay && data.date) {
        console.warn("#simulation-date element not found, cannot update date.");
    }

    if (timeDisplay && data.time) {
        timeDisplay.textContent = data.time;
    } else if (!timeDisplay && data.time) {
        console.warn("#simulation-time element not found, cannot update time.");
    }
    
    if (currentHourDisplay && data.time) {
        currentHourDisplay.textContent = data.time.substring(0, 5); // Display HH:MM
    } else if (!currentHourDisplay && data.time) {
        console.warn("#current-hour element not found, cannot update current hour.");
    }
}
*/

// Update all charts with current data - replaced with progress indicators
function updateCharts() {
    // Charts removed - functionality replaced with updateProgressIndicators()
    console.log('Chart updates skipped - using simplified dashboard');
}

// Update current values displayed in the dashboard
function updateCurrentValues() {
    if (chartData.batteryValues.length > 0) {
        const lastBatteryValue = chartData.batteryValues[chartData.batteryValues.length - 1];
        document.getElementById('current-battery-level').textContent = 
            `${lastBatteryValue.toFixed(3)}%`;
    }
    
    if (chartData.batteryRecharge.length > 0) {
        const lastBatteryRecharge = chartData.batteryRecharge[chartData.batteryRecharge.length - 1];
        document.getElementById('current-battery-output').textContent = 
            `${lastBatteryRecharge.toFixed(2)} kW`;
    }
    
    if (chartData.evRecharge.length > 0) {
        const lastEVRecharge = chartData.evRecharge[chartData.evRecharge.length - 1];
        document.getElementById('current-ev-recharge').textContent = 
            `${lastEVRecharge.toFixed(2)} kW`;
    }
      if (chartData.gridRequest.length > 0) {
        const lastGridRequest = chartData.gridRequest[chartData.gridRequest.length - 1];
        document.getElementById('current-grid-request').textContent = 
            `${lastGridRequest.toFixed(2)} kW`;
    }
    
    // Update current PV output
    if (chartData.pvOutput.length > 0) {
        const lastPVOutput = chartData.pvOutput[chartData.pvOutput.length - 1];
        const pvOutputElement = document.getElementById('current-pv-output');
        if (pvOutputElement) {
            pvOutputElement.textContent = `${(lastPVOutput / 1000).toFixed(2)} kW`; // Convert watts to kW
        }
    }
}

// Update UI state based on simulation running status
function updateUIState() {
    if (simulationRunning) {
        startSimulationBtn.disabled = true;
        stopSimulationBtn.disabled = false;
    } else {
        startSimulationBtn.disabled = false;
        stopSimulationBtn.disabled = true;
    }
    
    // Handle export button state
    const exportDataBtn = document.getElementById('export-data-btn');
    if (exportDataBtn) {
        exportDataBtn.disabled = chartData.time.length === 0;
    }
}

// Update parameter form values
function updateParamFormValues(params) {
    paramInputs.forEach(input => {
        const paramKey = input.dataset.param;
        if (params.hasOwnProperty(paramKey)) {
            if (input.type === 'checkbox') {
                // Assuming checkbox data-value is "1.0" and data-off-value is "0.0"
                input.checked = parseFloat(params[paramKey]) === parseFloat(input.dataset.value);
            } else if (input.type === 'range') {
                input.value = params[paramKey];
                // Update display for range input
                if (rangeValueDisplays[paramKey]) {
                    rangeValueDisplays[paramKey].textContent = `${input.value}%`;
                }
            } else {
                input.value = params[paramKey];
            }        }
    });
    
    // Update date/time selectors if provided in params
    if (params.initial_start_date && params.initial_start_time) {
        try {
            // Parse date string (format: YYYY-MM-DD)
            const dateParts = params.initial_start_date.split('-');
            const month = parseInt(dateParts[1]);
            const day = parseInt(dateParts[2]);
            
            // Parse time string (format: HH:MM:SS or HH:MM)
            const timeParts = params.initial_start_time.split(':');
            const hour = parseInt(timeParts[0]);
            
            // Update the dropdowns
            if (simStartMonthSelect) simStartMonthSelect.value = month;
            populateDaysInMonth(); // Update days for the selected month
            if (simStartDaySelect) simStartDaySelect.value = day;
            if (simStartHourSelect) simStartHourSelect.value = hour;
        } catch (error) {
            console.error('Error parsing date/time from params:', error);
        }
    }
}

// Update PVWatts form values
function updatePVWattsFormValues(settings) {
    for (const [key, value] of Object.entries(settings)) {
        const input = document.getElementById(key);
        if (input) {
            input.value = value;
        }
    }
    // Update location display text
    if (currentLocationDisplay) {
        if (settings.lat && settings.lon) {
            currentLocationDisplay.textContent = `Lat: ${parseFloat(settings.lat).toFixed(4)}, Lon: ${parseFloat(settings.lon).toFixed(4)}`;
        } else {
            currentLocationDisplay.textContent = 'Location not set. Click button to use current location.';
        }
    }
}

// Add message to the simulation log
function logMessage(message, type = 'info') {
    const now = new Date();
    const timestamp = now.toLocaleTimeString();
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;
    
    simulationLog.appendChild(logEntry);
    simulationLog.scrollTop = simulationLog.scrollHeight;
}

// Fetch and set the current location using browser geolocation
function fetchAndSetCurrentLocation() {
    if (!navigator.geolocation) {
        logMessage('Geolocation is not supported by your browser.', 'warning');
        if (currentLocationDisplay) {
            currentLocationDisplay.textContent = 'Geolocation not supported.';
        }
        return;
    }

    logMessage('Fetching current location...', 'info');
    if (currentLocationDisplay) {
        currentLocationDisplay.textContent = 'Fetching location...';
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            const latInput = document.getElementById('lat');
            const lonInput = document.getElementById('lon');

            if (latInput) latInput.value = latitude;
            if (lonInput) lonInput.value = longitude;

            if (currentLocationDisplay) {
                currentLocationDisplay.textContent = `Lat: ${latitude.toFixed(4)}, Lon: ${longitude.toFixed(4)}`;
            }
            logMessage(`Location fetched: Lat ${latitude.toFixed(4)}, Lon ${longitude.toFixed(4)}`, 'success');
            
            // Optionally, you might want to trigger an update to PVWatts settings here
            // or inform the user to click "Update PVWatts Data"
            // For now, it just populates the hidden fields.
        },
        (error) => {
            let errorMsg = 'Error fetching location: ';
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg += "User denied the request for Geolocation.";
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg += "Location information is unavailable.";
                    break;
                case error.TIMEOUT:
                    errorMsg += "The request to get user location timed out.";
                    break;
                case error.UNKNOWN_ERROR:
                    errorMsg += "An unknown error occurred.";
                    break;
            }
            logMessage(errorMsg, 'error');
            if (currentLocationDisplay) {
                currentLocationDisplay.textContent = 'Failed to retrieve location. Please enter manually if supported or try again.';
            }
        }
    );
}

// Update electricity cost display
function updateCostDisplay(data) {
    // Update total cumulative cost
    if (data.cumulative_cost !== undefined) {
        const totalCostEl = document.getElementById('total-electricity-cost');
        if (totalCostEl) {
            totalCostEl.textContent = `${data.currency || 'RM'} ${data.cumulative_cost.toFixed(2)}`;
        }
    }
    
    // Update current electricity rate
    if (data.electricity_rate !== undefined) {
        const currentRateEl = document.getElementById('current-electricity-rate');
        if (currentRateEl) {
            currentRateEl.textContent = `${data.currency || 'RM'} ${data.electricity_rate.toFixed(3)}/kWh`;
        }
    }
    
    // Update rate period
    if (data.rate_type !== undefined) {
        const ratePeriodEl = document.getElementById('rate-period');
        if (ratePeriodEl) {
            ratePeriodEl.textContent = data.rate_type;
        }
    }
}

// Load current electricity pricing configuration
function loadElectricityPricing() {
    fetch('/api/electricity/pricing')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.pricing) {
                const pricing = data.pricing;
                
                // Update pricing form fields
                const peakRateInput = document.getElementById('peak-rate');
                const offPeakRateInput = document.getElementById('off-peak-rate');
                const peakStartSelect = document.getElementById('peak-start');
                const peakEndSelect = document.getElementById('peak-end');
                
                if (peakRateInput) peakRateInput.value = pricing.peak_rate;
                if (offPeakRateInput) offPeakRateInput.value = pricing.off_peak_rate;
                if (peakStartSelect) peakStartSelect.value = pricing.peak_start_hour;
                if (peakEndSelect) peakEndSelect.value = pricing.peak_end_hour;
                
                logMessage('Loaded electricity pricing configuration', 'info');
            } else {
                logMessage('Failed to load electricity pricing configuration', 'error');
            }
        })
        .catch(error => {
            console.error('Error loading electricity pricing:', error);
            logMessage('Error loading electricity pricing configuration', 'error');
        });
}

// Update electricity pricing configuration
function updateElectricityPricing(formData) {
    const pricingData = {
        peak_rate: parseFloat(formData.get('peak-rate')),
        off_peak_rate: parseFloat(formData.get('off-peak-rate')),
        currency: 'RM',
        peak_start_hour: parseInt(formData.get('peak-start')),
        peak_end_hour: parseInt(formData.get('off-peak-end'))
    };
    
    fetch('/api/electricity/pricing', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(pricingData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            logMessage('Electricity pricing updated successfully', 'success');
        } else {
            logMessage(`Failed to update electricity pricing: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error updating electricity pricing:', error);
        logMessage('Error updating electricity pricing', 'error');
    });
}

// Reset electricity costs
function resetElectricityCosts() {
    fetch('/api/electricity/reset-costs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())    .then(data => {
        if (data.success) {
            logMessage('Electricity costs reset successfully', 'success');
            
            // Reset display values
            const totalCostEl = document.getElementById('total-electricity-cost');
            
            if (totalCostEl) totalCostEl.textContent = 'RM 0.00';
            
            // Clear cost chart data
            chartData.electricityCost = [];
            chartData.cumulativeCost = [];
        } else {
            logMessage(`Failed to reset electricity costs: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error resetting electricity costs:', error);
        logMessage('Error resetting electricity costs', 'error');
    });
}

// Update progress indicators and visual elements (replaces chart functionality)
function updateProgressIndicators() {
    // Update system battery progress bar
    if (chartData.batteryValues.length > 0) {
        const batteryLevel = chartData.batteryValues[chartData.batteryValues.length - 1];
        const systemBatteryProgress = document.getElementById('system-battery-progress');
        if (systemBatteryProgress) {
            const percentage = Math.max(0, Math.min(100, batteryLevel));
            systemBatteryProgress.style.width = `${percentage}%`;
            systemBatteryProgress.setAttribute('aria-valuenow', percentage);
            systemBatteryProgress.textContent = `${percentage.toFixed(1)}%`;
            
            // Update color based on battery level
            systemBatteryProgress.className = 'progress-bar';
            if (percentage > 60) {
                systemBatteryProgress.classList.add('bg-success');
            } else if (percentage > 30) {
                systemBatteryProgress.classList.add('bg-warning');
            } else {
                systemBatteryProgress.classList.add('bg-danger');
            }
        }
    }
    
    // Update grid load indicator
    if (chartData.gridRequest.length > 0) {
        const gridRequest = chartData.gridRequest[chartData.gridRequest.length - 1];
        const gridLoadProgress = document.getElementById('grid-load-progress');
        if (gridLoadProgress) {
            // Assume max grid capacity of 100 kW for percentage calculation
            const maxGridCapacity = 100;
            const percentage = Math.max(0, Math.min(100, (gridRequest / maxGridCapacity) * 100));
            gridLoadProgress.style.width = `${percentage}%`;
            gridLoadProgress.setAttribute('aria-valuenow', percentage);
            gridLoadProgress.textContent = `${gridRequest.toFixed(2)} kW`;
            
            // Update color based on grid load
            gridLoadProgress.className = 'progress-bar';
            if (percentage > 80) {
                gridLoadProgress.classList.add('bg-danger');
            } else if (percentage > 60) {
                gridLoadProgress.classList.add('bg-warning');
            } else {
                gridLoadProgress.classList.add('bg-success');
            }
        }
    }
}

// ===== 2D SYSTEM VISUALIZATION FUNCTIONS =====

/**
 * Update the 2D system visualization with real-time data
 */
function update2DVisualization() {
    if (chartData.time.length === 0) return;
    
    const latestIndex = chartData.time.length - 1;
    
    // Update Solar System
    updateSolarComponent(latestIndex);
    
    // Update Battery System
    updateBatteryComponent(latestIndex);
    
    // Update Grid System
    updateGridComponent(latestIndex);
    
    // Update EV Charging Bays
    updateEVBays(latestIndex);
    
    // Update Energy Flows
    updateEnergyFlows(latestIndex);
}

/**
 * Update solar component visualization
 */
function updateSolarComponent(index) {
    const pvOutput = chartData.pvOutput[index] || 0;
    const solarOutputEl = document.getElementById('solar-output');
    const solarStatusEl = document.getElementById('solar-status');
    const solarComponent = document.getElementById('solar-component');
    
    if (solarOutputEl) {
        solarOutputEl.textContent = `${pvOutput.toFixed(3)} W`;
    }
    
    if (solarStatusEl && solarComponent) {
        if (pvOutput > 0) {
            solarStatusEl.textContent = 'Generating';
            solarComponent.classList.add('active');
            solarComponent.classList.remove('warning', 'error');
        } else {
            solarStatusEl.textContent = 'Inactive';
            solarComponent.classList.remove('active', 'warning', 'error');
        }
    }
}

/**
 * Update battery component visualization
 */
function updateBatteryComponent(index) {
    const batteryLevel = chartData.batteryValues[index] || 0;
    const batteryRecharge = chartData.batteryRecharge[index] || 0;
    
    const batteryFill = document.getElementById('battery-fill');
    const batteryPercentage = document.getElementById('battery-percentage');
    const batteryPower = document.getElementById('battery-power');
    const batteryComponent = document.getElementById('battery-component');
    
    if (batteryFill) {
        batteryFill.style.height = `${Math.max(0, Math.min(100, batteryLevel))}%`;
        
        // Change color based on battery level
        if (batteryLevel > 60) {
            batteryFill.style.background = 'linear-gradient(180deg, #28a745 0%, #20c997 100%)';
        } else if (batteryLevel > 30) {
            batteryFill.style.background = 'linear-gradient(180deg, #ffc107 0%, #ffb300 100%)';
        } else {
            batteryFill.style.background = 'linear-gradient(180deg, #dc3545 0%, #c82333 100%)';
        }
    }
    
    if (batteryPercentage) {
        batteryPercentage.textContent = `${batteryLevel.toFixed(0)}%`;
    }
    
    if (batteryPower) {
        const powerText = batteryRecharge >= 0 ? `+${batteryRecharge.toFixed(2)} kW` : `${batteryRecharge.toFixed(2)} kW`;
        batteryPower.textContent = powerText;
        batteryPower.style.color = batteryRecharge >= 0 ? '#28a745' : '#dc3545';
    }
    
    if (batteryComponent) {
        if (batteryLevel > 60) {
            batteryComponent.classList.add('active');
            batteryComponent.classList.remove('warning', 'error');
        } else if (batteryLevel > 30) {
            batteryComponent.classList.add('warning');
            batteryComponent.classList.remove('active', 'error');
        } else {
            batteryComponent.classList.add('error');
            batteryComponent.classList.remove('active', 'warning');
        }
    }
}

/**
 * Update grid component visualization
 */
function updateGridComponent(index) {
    const gridComponent = document.getElementById('grid-component');
    const peakIndicator = document.getElementById('peak-indicator');
    const gridPower = document.getElementById('grid-power');
    
    if (!gridComponent || !peakIndicator || !gridPower) {
        console.warn('Grid component elements not found');
        return;
    }

    if (chartData.gridRequest.length > 0 && index < chartData.gridRequest.length) {
        const gridValue = chartData.gridRequest[index] || 0;
        
        // Update power display - show just the power value without import/export labels
        gridPower.textContent = `${Math.abs(gridValue).toFixed(2)} kW`;
        
        // Get current simulation time for peak status calculation
        const currentTime = chartData.time[index];
        let currentHour = 12; // Default to noon if no time data
        
        // Calculate hour from simulation data if available
        if (currentTime !== undefined) {
            // Assuming simulation starts at midnight and each point represents some time progression
            // This is a simplified calculation - adjust based on your actual time progression
            const simulationHours = (currentTime / 3600) % 24; // Convert seconds to hours, wrap at 24
            currentHour = Math.floor(simulationHours);
        }
        
        // Alternative: Use actual datetime if available from data point
        // This should be the preferred method if datetime is available
        const lastDataPoint = window.lastReceivedDataPoint;
        if (lastDataPoint && lastDataPoint.date && lastDataPoint.time) {
            const timeStr = lastDataPoint.time;
            const timeParts = timeStr.split(':');
            if (timeParts.length >= 1) {
                currentHour = parseInt(timeParts[0], 10);
            }
        }
        
        // Determine peak status (8 AM to 10 PM = peak hours)
        const isPeakTime = currentHour >= 8 && currentHour < 22;
        
        // Update peak indicator
        peakIndicator.textContent = isPeakTime ? 'Peak' : 'Off-Peak';
        
        // Update component styling based on peak status
        gridComponent.className = 'component grid-system';
        if (isPeakTime) {
            gridComponent.classList.add('peak-time');
            peakIndicator.className = 'peak-indicator peak-active';
        } else {
            gridComponent.classList.add('off-peak-time');
            peakIndicator.className = 'peak-indicator off-peak-active';
        }
        
        // Update component status based on grid usage
        if (Math.abs(gridValue) > 20) {
            gridComponent.classList.add('warning');
        } else if (Math.abs(gridValue) > 0.1) {
            gridComponent.classList.add('active');
        }
        
        console.log(`Grid updated: ${Math.abs(gridValue).toFixed(2)} kW, Hour: ${currentHour}, Peak: ${isPeakTime ? 'Yes' : 'No'}`);
    }
}

/**
 * Update EV charging bays visualization
 */
function updateEVBays(index) {
    const evData = [
        {
            batteryLevel: chartData.vehicle1BatteryLevel[index] || 0,
            occupied: document.getElementById('bay1_occupied')?.checked || false,
            bayId: 1
        },
        {
            batteryLevel: chartData.vehicle2BatteryLevel[index] || 0,
            occupied: document.getElementById('bay2_occupied')?.checked || false,
            bayId: 2
        },
        {
            batteryLevel: chartData.vehicle3BatteryLevel[index] || 0,
            occupied: document.getElementById('bay3_occupied')?.checked || false,
            bayId: 3
        },
        {
            batteryLevel: chartData.vehicle4BatteryLevel[index] || 0,
            occupied: document.getElementById('bay4_occupied')?.checked || false,
            bayId: 4
        }
    ];
    
    const evRecharge = chartData.evRecharge[index] || 0;
    const chargingRatePerBay = evData.filter(ev => ev.occupied).length > 0 ? 
        evRecharge / evData.filter(ev => ev.occupied).length : 0;
    
    evData.forEach(ev => {
        updateEVBayVisualization(ev.bayId, ev.batteryLevel, ev.occupied, chargingRatePerBay);
    });
}

/**
 * Update individual EV bay visualization
 */
function updateEVBayVisualization(bayId, batteryLevel, occupied, chargingRate) {
    const batteryFill = document.getElementById(`ev${bayId}-battery-fill`);
    const batteryText = document.getElementById(`ev${bayId}-battery-text`);
    const chargingRateEl = document.getElementById(`ev${bayId}-charging-rate`);
    const statusEl = document.getElementById(`ev${bayId}-status`);
    const bayComponent = document.getElementById(`ev-bay-${bayId}`);
    
    if (batteryFill) {
        batteryFill.style.height = `${Math.max(0, Math.min(100, batteryLevel))}%`;
    }
    
    if (batteryText) {
        batteryText.textContent = `${batteryLevel.toFixed(0)}%`;
    }
    
    if (chargingRateEl) {
        if (occupied && chargingRate > 0) {
            chargingRateEl.textContent = `${chargingRate.toFixed(2)} kW`;
        } else {
            chargingRateEl.textContent = '0.00 kW';
        }
    }
    
    if (statusEl) {
        let status = '';
        let statusClass = '';
        
        if (!occupied) {
            status = 'Empty';
            statusClass = 'empty';
        } else if (batteryLevel >= 100) {
            status = 'Full';
            statusClass = 'full';
        } else if (chargingRate > 0) {
            status = 'Charging';
            statusClass = 'charging';
        } else {
            status = 'Connected';
            statusClass = 'occupied';
        }
        
        statusEl.textContent = status;
        statusEl.className = `bay-status ${statusClass}`;
    }
    
    if (bayComponent) {
        if (occupied && chargingRate > 0) {
            bayComponent.classList.add('active');
            bayComponent.classList.remove('warning', 'error');
        } else if (occupied) {
            bayComponent.classList.add('warning');
            bayComponent.classList.remove('active', 'error');
        } else {
            bayComponent.classList.remove('active', 'warning', 'error');
        }
    }
}

/**
 * Update energy flow animations using SVG lines.
 */
function updateEnergyFlows(index) {
    const pvOutput = chartData.pvOutput[index] || 0; // Watts
    const batteryRecharge = chartData.batteryRecharge[index] || 0; // kW (positive for charging, negative for discharging)
    const evRecharge = chartData.evRecharge[index] || 0; // kW
    const gridRequest = chartData.gridRequest[index] || 0; // kW (positive for import, negative for export)

    // Get SVG line elements
    const solarToBatteryLine = document.getElementById('svg-flow-solar-battery');
    const solarToGridLine = document.getElementById('svg-flow-solar-grid');
    const solarToEvsLine = document.getElementById('svg-flow-solar-evs');
    const batteryToEvsLine = document.getElementById('svg-flow-battery-evs');
    const batteryToGridLine = document.getElementById('svg-flow-battery-grid');
    const gridToEvsLine = document.getElementById('svg-flow-grid-evs');
    const gridToBatteryLine = document.getElementById('svg-flow-grid-battery'); // New line

    const allLines = [solarToBatteryLine, solarToGridLine, solarToEvsLine, batteryToEvsLine, batteryToGridLine, gridToEvsLine, gridToBatteryLine]; // Add new line

    // Reset all lines
    allLines.forEach(line => {
        if (line) {
            line.style.visibility = 'hidden';
            line.classList.remove('flow-active-animation');
        }
    });

    // Helper function to set SVG flow properties
    function setSVGFlowProperties(lineElement, powerValue, flowTypeClass) {
        if (!lineElement || powerValue <= 0) {
            if (lineElement) lineElement.style.visibility = 'hidden';
            return;
        }
        lineElement.style.visibility = 'visible';
        lineElement.setAttribute('class', `svg-energy-flow ${flowTypeClass} flow-active-animation`); // Add base class and type class
        
        // Adjust stroke-width based on power (example logic)
        let strokeWidth = 2 + Math.log10(Math.abs(powerValue) + 1) * 2; // Scale stroke width
        strokeWidth = Math.min(Math.max(strokeWidth, 2), 8); // Clamp between 2 and 8
        lineElement.style.strokeWidth = `${strokeWidth}px`;
    }

    // Determine active flows and their properties
    // Note: Power values for setSVGFlowProperties should be positive for intensity calculation

    // Solar PV is generating
    if (pvOutput > 0) {
        const pvOutputKW = pvOutput / 1000;

        // Solar to Battery (if battery is charging)
        if (batteryRecharge > 0) {
            setSVGFlowProperties(solarToBatteryLine, Math.min(pvOutputKW, batteryRecharge), 'flow-solar');
        }

        // Solar to EVs (if EVs are charging and solar can supply it)
        // This logic is simplified; a real system would have more complex power distribution.
        if (evRecharge > 0) {
            // Assume solar contributes some portion to EV charging if available
            setSVGFlowProperties(solarToEvsLine, Math.min(pvOutputKW, evRecharge), 'flow-solar');
        }
        
        // Solar to Grid (if exporting, gridRequest is negative)
        if (gridRequest < 0) {
            setSVGFlowProperties(solarToGridLine, Math.abs(gridRequest), 'flow-solar');
        }
    }

    // Battery is discharging (batteryRecharge is negative)
    if (batteryRecharge < 0) {
        const batteryDischargeKW = Math.abs(batteryRecharge);
        // Battery to EVs
        if (evRecharge > 0) {
            setSVGFlowProperties(batteryToEvsLine, Math.min(batteryDischargeKW, evRecharge), 'flow-battery');
        }
        // Battery to Grid (if exporting and battery is the source)
        // This might overlap with solar to grid; more sophisticated logic needed for precise source attribution.
        // For simplicity, if battery is discharging and grid is exporting, show battery to grid.
        if (gridRequest < 0) {
             // Only show if solar isn't already covering the export
            if (!(pvOutput > 0 && Math.abs(gridRequest) <= pvOutput/1000)) {
                 setSVGFlowProperties(batteryToGridLine, Math.min(batteryDischargeKW, Math.abs(gridRequest)), 'flow-battery');
            }
        }
    }
    
    // Grid is supplying power (gridRequest is positive)
    if (gridRequest > 0) {
        // Grid to EVs (if EVs are charging and grid is supplying)
        if (evRecharge > 0) {
            setSVGFlowProperties(gridToEvsLine, Math.min(gridRequest, evRecharge), 'flow-grid');
        }
        // Grid to Battery (if battery is charging from grid)
        if (batteryRecharge > 0) {
            const pvOutputKW = pvOutput / 1000; // Ensure pvOutputKW is defined here too
            // Calculate power needed by battery that solar doesn't cover
            const chargeFromSolarToBattery = Math.min(pvOutputKW, batteryRecharge);
            const remainingChargeNeededByBattery = batteryRecharge - chargeFromSolarToBattery;
            
            if (remainingChargeNeededByBattery > 0) {
                // Power from grid to battery is the minimum of what's still needed and what grid is supplying overall
                const powerFromGridToBattery = Math.min(remainingChargeNeededByBattery, gridRequest);
                if (powerFromGridToBattery > 0) {
                    setSVGFlowProperties(gridToBatteryLine, powerFromGridToBattery, 'flow-grid');
                }
            }
        }
    }
}

/**
 * Helper function to get the center coordinates of a component relative to the SVG layer.
 * @param {string} selector - The CSS selector for the component.
 * @param {DOMRect} svgRect - The boundingClientRect of the SVG layer.
 * @returns {{x: number, y: number}} - The center coordinates.
 */
function getComponentCenter(selector, svgRect) {
    const component = document.querySelector(selector);
    if (component) {
        const rect = component.getBoundingClientRect();
        return {
            x: rect.left + rect.width / 2 - svgRect.left,
            y: rect.top + rect.height / 2 - svgRect.top
        };
    }
    console.error(`Component with selector ${selector} not found for centering.`);
    // Return a default point or handle error as appropriate
    return { x: 0, y: 0 }; 
}

/**
 * Initialize 2D visualization on page load
 */
function initialize2DVisualization() {
    // Set initial states
    const components = document.querySelectorAll('.component');
    components.forEach(component => {
        component.classList.remove('active', 'warning', 'error');
    });

    const svgLayer = document.getElementById('energy-flow-svg-layer');
    if (!svgLayer) {
        console.error("SVG layer for energy flows not found!");
        return;
    }
    svgLayer.innerHTML = ''; // Clear previous lines if any
    const svgRect = svgLayer.getBoundingClientRect();

    // Define flow paths using component selectors
    const flowPaths = [
        { id: 'svg-flow-solar-battery', fromSelector: '#solar-component', toSelector: '#battery-component', type: 'flow-solar' },
        { id: 'svg-flow-solar-grid', fromSelector: '#solar-component', toSelector: '#grid-component', type: 'flow-solar' },
        { id: 'svg-flow-solar-evs', fromSelector: '#solar-component', toSelector: '.charging-bays-container', type: 'flow-solar' },
        
        { id: 'svg-flow-battery-evs', fromSelector: '#battery-component', toSelector: '.charging-bays-container', type: 'flow-battery' },
        { id: 'svg-flow-battery-grid', fromSelector: '#battery-component', toSelector: '#grid-component', type: 'flow-battery' },
        
        { id: 'svg-flow-grid-evs', fromSelector: '#grid-component', toSelector: '.charging-bays-container', type: 'flow-grid' },
        { id: 'svg-flow-grid-battery', fromSelector: '#grid-component', toSelector: '#battery-component', type: 'flow-grid' } // New path
    ];

    flowPaths.forEach(path => {
        const fromPoint = getComponentCenter(path.fromSelector, svgRect);
        const toPoint = getComponentCenter(path.toSelector, svgRect);

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('id', path.id);
        line.setAttribute('x1', fromPoint.x);
        line.setAttribute('y1', fromPoint.y);
        line.setAttribute('x2', toPoint.x);
        line.setAttribute('y2', toPoint.y);
        line.setAttribute('class', `svg-energy-flow ${path.type}`); // Add base class and type class
        line.style.strokeWidth = '4px'; // Default stroke width
        line.style.visibility = 'hidden'; // Initially hidden
        svgLayer.appendChild(line);
    });
    
    // Initialize all values to zero or default
    update2DVisualization(); // This will call updateEnergyFlows which now uses SVG
    
    console.log('2D System Visualization initialized with SVG flows (center-to-center).');
}

// Update EV charging summary information
function updateEVChargingSummary() {
    // Count active charging bays
    let activeBays = 0;
    const bayOccupiedIds = ['bay1_occupied', 'bay2_occupied', 'bay3_occupied', 'bay4_occupied'];
    
    bayOccupiedIds.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox && checkbox.checked) {
            activeBays++;
        }
    });
    
    // Update active charging bays display
    const activeChargingBaysEl = document.getElementById('active-charging-bays');
    if (activeChargingBaysEl) {
        activeChargingBaysEl.textContent = activeBays;
    }
    
    // Calculate and update charging efficiency
    if (chartData.evRecharge.length > 0) {
        const totalEVRecharge = chartData.evRecharge[chartData.evRecharge.length - 1];
        const chargingEfficiencyEl = document.getElementById('charging-efficiency');
        if (chargingEfficiencyEl) {
            const efficiency = activeBays > 0 ? (totalEVRecharge / activeBays) : 0;
            chargingEfficiencyEl.textContent = `${efficiency.toFixed(2)} kW/bay`;
        }
        
        // Update charging status
        const chargingStatusEl = document.getElementById('charging-status');
        if (chargingStatusEl) {
            if (activeBays === 0) {
                chargingStatusEl.textContent = 'Idle';
                chargingStatusEl.className = 'badge bg-secondary';
            } else if (totalEVRecharge > 0) {
                chargingStatusEl.textContent = 'Active';
                chargingStatusEl.className = 'badge bg-success';
            } else {
                chargingStatusEl.textContent = 'Standby';
                chargingStatusEl.className = 'badge bg-warning';
            }
        }
    }
}

// Update solar performance metrics
function updateSolarPerformance(data) {
    // Update current PV output and track daily peak
    if (data.pv_output_watts !== undefined) {
        const currentPV = data.pv_output_watts / 1000; // Convert to kW
        
        // Extract date from simulation time to track daily peaks
        const simDate = data.time ? data.time.split(' ')[0] : '';
        
        // Reset daily peak if new day
        if (simDate !== currentDate) {
            currentDate = simDate;
            dailyPeakPV = 0;
        }
        
        // Update daily peak
        if (currentPV > dailyPeakPV) {
            dailyPeakPV = currentPV;
        }
        
        // Update PV peak today display
        const pvPeakElement = document.getElementById('pv-peak-today');
        if (pvPeakElement) {
            pvPeakElement.textContent = `${dailyPeakPV.toFixed(2)} kW`;
        }
        
        // Calculate efficiency (assuming 10kW system capacity as typical)
        const systemCapacity = 10.0; // kW - this could be made configurable
        const efficiency = (currentPV / systemCapacity) * 100;
        
        // Update efficiency display
        const pvEfficiencyElement = document.getElementById('pv-efficiency');
        if (pvEfficiencyElement) {
            pvEfficiencyElement.textContent = `${efficiency.toFixed(1)}%`;
        }
    }
    
    // Update weather status based on PV output and other indicators
    updateWeatherStatus(data);
}

// Update weather status display
function updateWeatherStatus(data) {
    const weatherStatusElement = document.getElementById('weather-status');
    if (!weatherStatusElement) return;
    
    let weatherStatus = 'Unknown';
    let statusClass = 'text-muted';
    
    // Determine weather status based on PV output
    if (data.pv_output_watts !== undefined) {
        const currentPV = data.pv_output_watts / 1000; // Convert to kW
        const systemCapacity = 10.0; // kW
        const efficiency = (currentPV / systemCapacity) * 100;
        
        // Simple weather determination based on solar efficiency
        if (efficiency >= 80) {
            weatherStatus = 'Sunny';
            statusClass = 'text-success';
        } else if (efficiency >= 50) {
            weatherStatus = 'Partly Cloudy';
            statusClass = 'text-warning';
        } else if (efficiency >= 20) {
            weatherStatus = 'Cloudy';
            statusClass = 'text-info';
        } else if (efficiency > 0) {
            weatherStatus = 'Overcast';
            statusClass = 'text-secondary';
        } else {
            weatherStatus = 'Night/No Sun';
            statusClass = 'text-dark';
        }
    }
    
    weatherStatusElement.textContent = weatherStatus;
    weatherStatusElement.className = statusClass;
}

// Add new function to update speed display
function updateSpeedDisplay(speed) {
    if (currentSpeedDisplay) {
        const speedText = `Current: ${speed}x`;
        currentSpeedDisplay.textContent = speedText;
        
        // Add visual feedback with color coding
        currentSpeedDisplay.className = 'text-white speed-display';
        if (speed < 1.0) {
            currentSpeedDisplay.classList.add('speed-slow');
        } else if (speed > 1.0) {
            currentSpeedDisplay.classList.add('speed-fast');
        } else {
            currentSpeedDisplay.classList.add('speed-normal');
        }
    }
}
