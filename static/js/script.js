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
let simStartMonthSelect; // Updated for month selection
let simStartDaySelect;   // Updated for day selection
let simStartHourSelect;  // Updated for hour selection

// Charts
let pvOutputChart;
let batteryChart;
let evChargingChart;
let gridChart;

// Data buffers for charts (limit to last 100 points)
const MAX_DATA_POINTS = 100;
const chartData = {
    time: [],
    pvOutput: [],
    batteryValues: [],
    batteryRecharge: [],
    evRecharge: [],
    gridRequest: [],
    vehicle1BatteryLevel: [],
    vehicle2BatteryLevel: [],
    vehicle3BatteryLevel: [],
    vehicle4BatteryLevel: []
};

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
    simStartMonthSelect = document.getElementById('sim-start-month');
    simStartDaySelect = document.getElementById('sim-start-day');
    simStartHourSelect = document.getElementById('sim-start-hour');

    paramInputs = document.querySelectorAll('.param-input');
    rangeValueDisplays = {
        'bay1_percentage': document.getElementById('bay1_percentage_value'),
        'bay2_percentage': document.getElementById('bay2_percentage_value'),
        'bay3_percentage': document.getElementById('bay3_percentage_value'),
        'bay4_percentage': document.getElementById('bay4_percentage_value'),
        'battery_soc': document.getElementById('battery_soc_value')
    };

    // Check if essential elements were found
    if (!startSimulationBtn) {
        console.error("CRITICAL: #start-simulation-btn not found during DOMContentLoaded!");
    }
    // Add more checks for other critical elements if necessary

    initializeCharts();
    setupEventListeners();
    fetchInitialData();
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

    // Update peak status display
    if (data.grid_peak_status !== undefined) {
        const gridPeakStatusEl = document.getElementById('grid-peak-status');
        if (gridPeakStatusEl) {
            gridPeakStatusEl.textContent = data.grid_peak_status;
        } else {
            console.error("DOM element #grid-peak-status not found for grid_peak_status.");
        }
    }
    
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
        }
    } else {
        logMessage(data.message, 'error');
    }
});

// Function to initialize all charts
function initializeCharts() {
    // PV Output Chart
    const pvOutputCtx = document.getElementById('pv-output-chart').getContext('2d');
    pvOutputChart = new Chart(pvOutputCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'PV Output (W)', // Changed from kW to W
                data: [],
                borderColor: 'rgba(255, 193, 7, 1)',
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 0 // Disable animation for better performance
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Simulation Time (s)'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Power (W)' // Changed from kW to W
                    }
                }
            }
        }
    });
    
    // Battery Chart
    const batteryCtx = document.getElementById('battery-chart').getContext('2d');
    batteryChart = new Chart(batteryCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Battery Level',
                    data: [],
                    borderColor: 'rgba(13, 110, 253, 1)',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'Battery Recharge',
                    data: [],
                    borderColor: 'rgba(23, 162, 184, 1)',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            animation: {
                duration: 0
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Simulation Time (s)'
                    }
                },
                y: {
                    position: 'left',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Level (%)'
                    },
                    max: 100
                },
                y1: {
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Recharge (kW)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
    
    // EV Charging Chart
    const evChargingCtx = document.getElementById('ev-charging-chart').getContext('2d');
    evChargingChart = new Chart(evChargingCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'EV Recharge (kW)',
                data: [],
                borderColor: 'rgba(40, 167, 69, 1)',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 0
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Simulation Time (s)'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Power (kW)'
                    }
                }
            }
        }
    });
    
    // Grid Chart
    const gridCtx = document.getElementById('grid-chart').getContext('2d');
    gridChart = new Chart(gridCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Grid Request (kW)',
                data: [],
                borderColor: 'rgba(220, 53, 69, 1)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 0
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Simulation Time (s)'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Power (kW)'
                    }
                }
            }
        }
    });
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
    
    // PVWatts form submission
    pvwattsForm.addEventListener('submit', (e) => {
        e.preventDefault();
        updatePVWattsSettings();
    });
    
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
            socket.emit('set_simulation_speed', { speed: speed });
            logMessage(`Simulation speed set to ${speed}x`, 'info');
        });
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
            // Assuming pvOutput data is also batched here if this event is used
            if (data.pvOutput && i < data.pvOutput.length) chartData.pvOutput.push(data.pvOutput[i]); 
            else if (data.pv_output_watts && i < data.pv_output_watts.length) chartData.pvOutput.push(data.pv_output_watts[i]);

            if (data.batt_values && i < data.batt_values.length) chartData.batteryValues.push(data.batt_values[i]);
            if (data.batt_recharge && i < data.batt_recharge.length) chartData.batteryRecharge.push(data.batt_recharge[i]);
            if (data.ev_recharge && i < data.ev_recharge.length) chartData.evRecharge.push(data.ev_recharge[i]);
            if (data.grid_request && i < data.grid_request.length) chartData.gridRequest.push(data.grid_request[i]);
            if (data.vehicle1_battery_level && i < data.vehicle1_battery_level.length) chartData.vehicle1BatteryLevel.push(data.vehicle1_battery_level[i]);
            if (data.vehicle2_battery_level && i < data.vehicle2_battery_level.length) chartData.vehicle2BatteryLevel.push(data.vehicle2_battery_level[i]);
            if (data.vehicle3_battery_level && i < data.vehicle3_battery_level.length) chartData.vehicle3BatteryLevel.push(data.vehicle3_battery_level[i]);
            if (data.vehicle4_battery_level && i < data.vehicle4_battery_level.length) chartData.vehicle4BatteryLevel.push(data.vehicle4_battery_level[i]);
        }
        
        trimChartData();
        updateCharts();
        updateCurrentValues();
        updateEVBatteryStatus();
    }
}

function processSingleDataPoint(data) {
    // Add data to buffers
    chartData.time.push(data.time_abs); // Use absolute time for chart labels
    chartData.pvOutput.push(data.pv_output_watts);
    chartData.batteryValues.push(data.batt_value);
    chartData.batteryRecharge.push(data.batt_recharge);
    chartData.evRecharge.push(data.ev_recharge);
    chartData.gridRequest.push(data.grid_request);
    chartData.vehicle1BatteryLevel.push(data.vehicle1_battery_level);
    chartData.vehicle2BatteryLevel.push(data.vehicle2_battery_level);
    chartData.vehicle3BatteryLevel.push(data.vehicle3_battery_level);
    chartData.vehicle4BatteryLevel.push(data.vehicle4_battery_level);

    trimChartData();
    updateCharts();
    updateCurrentValues(); // Update dashboard numbers
    updateEVBatteryStatus(); // Update EV status displays    // Update current PV output per second display (average PV output per second = current PV output / 3600)
    if (data.pv_output_watts !== undefined) {
        const currentPvOutputEl = document.getElementById('current-pv-output');
        if (currentPvOutputEl) {
            const pvOutputPerSecond = data.pv_output_watts / 3600;
            currentPvOutputEl.textContent = `${pvOutputPerSecond.toFixed(4)} W/s`;
        } else {
            console.error("DOM element #current-pv-output not found for pv_output_watts.");
        }
    }

    // Update peak status display
    if (data.grid_peak_status !== undefined) {
        const gridPeakStatusEl = document.getElementById('grid-peak-status');
        if (gridPeakStatusEl) {
            gridPeakStatusEl.textContent = data.grid_peak_status;
        } else {
            console.error("DOM element #grid-peak-status not found for grid_peak_status.");
        }
    }
    // The time display is now handled directly in the socket.on('new_simulation_point') handler
    // logMessage(`Processed point at time ${data.time_abs.toFixed(2)}s`, 'debug'); 
}

function trimChartData() {
    if (chartData.time.length > MAX_DATA_POINTS) {
        const excess = chartData.time.length - MAX_DATA_POINTS;
        chartData.time.splice(0, excess);
        chartData.pvOutput.splice(0, excess);
        chartData.batteryValues.splice(0, excess);
        chartData.batteryRecharge.splice(0, excess);
        chartData.evRecharge.splice(0, excess);
        chartData.gridRequest.splice(0, excess);
        chartData.vehicle1BatteryLevel.splice(0, excess);
        chartData.vehicle2BatteryLevel.splice(0, excess);
        chartData.vehicle3BatteryLevel.splice(0, excess);
        chartData.vehicle4BatteryLevel.splice(0, excess);
    }
}

// Export simulation data to CSV
function exportSimulationData() {
    if (chartData.time.length === 0) {
        logMessage('No data to export', 'warning');
        return;
    }
    
    // Create CSV content
    let csvContent = 'Time (s),PV Output (kW),Battery Level (%),Battery Recharge (kW),EV Recharge (kW),Grid Request (kW),Vehicle 1 Battery (%),Vehicle 2 Battery (%),Vehicle 3 Battery (%),Vehicle 4 Battery (%)\n';
    
    // Combine all data points
    for (let i = 0; i < chartData.time.length; i++) {
        const row = [
            chartData.time[i] || '',
            chartData.pvOutput[i] || '',
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

// Update all charts with current data
function updateCharts() {
    // Update PV Output Chart
    pvOutputChart.data.labels = chartData.time;
    pvOutputChart.data.datasets[0].data = chartData.pvOutput;
    pvOutputChart.update();
    
    // Update Battery Chart
    batteryChart.data.labels = chartData.time;
    batteryChart.data.datasets[0].data = chartData.batteryValues;
    batteryChart.data.datasets[1].data = chartData.batteryRecharge;
    batteryChart.update();
    
    // Update EV Charging Chart
    evChargingChart.data.labels = chartData.time;
    evChargingChart.data.datasets[0].data = chartData.evRecharge;
    evChargingChart.update();
    
    // Update Grid Chart
    gridChart.data.labels = chartData.time;
    gridChart.data.datasets[0].data = chartData.gridRequest;
    gridChart.update();
}

// Update current values displayed in the dashboard
function updateCurrentValues() {
    if (chartData.batteryValues.length > 0) {
        const lastBatteryValue = chartData.batteryValues[chartData.batteryValues.length - 1];
        document.getElementById('current-battery-level').textContent = 
            `${lastBatteryValue.toFixed(1)}%`;
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
}

// Update EV battery status displays
function updateEVBatteryStatus() {
    // Update EV 1 status
    if (chartData.vehicle1BatteryLevel.length > 0) {
        const ev1Level = chartData.vehicle1BatteryLevel[chartData.vehicle1BatteryLevel.length - 1];
        const ev1Occupied = document.getElementById('bay1_occupied').checked;
        
        updateEVDisplay('ev1', ev1Level, ev1Occupied);
    }
    
    // Update EV 2 status
    if (chartData.vehicle2BatteryLevel.length > 0) {
        const ev2Level = chartData.vehicle2BatteryLevel[chartData.vehicle2BatteryLevel.length - 1];
        const ev2Occupied = document.getElementById('bay2_occupied').checked;
        
        updateEVDisplay('ev2', ev2Level, ev2Occupied);
    }
    
    // Update EV 3 status
    if (chartData.vehicle3BatteryLevel.length > 0) {
        const ev3Level = chartData.vehicle3BatteryLevel[chartData.vehicle3BatteryLevel.length - 1];
        const ev3Occupied = document.getElementById('bay3_occupied').checked;
        
        updateEVDisplay('ev3', ev3Level, ev3Occupied);
    }
    
    // Update EV 4 status
    if (chartData.vehicle4BatteryLevel.length > 0) {
        const ev4Level = chartData.vehicle4BatteryLevel[chartData.vehicle4BatteryLevel.length - 1];
        const ev4Occupied = document.getElementById('bay4_occupied').checked;
        
        updateEVDisplay('ev4', ev4Level, ev4Occupied);
    }
}

// Helper function to update an EV display
function updateEVDisplay(evId, level, occupied) {
    const progressBar = document.getElementById(`${evId}-progress`);
    const statusBadge = document.getElementById(`${evId}-status`);
    
    if (!progressBar || !statusBadge) return;
    
    // Set progress bar value
    progressBar.style.width = `${level}%`;
    progressBar.textContent = `${level.toFixed(1)}%`;
    progressBar.setAttribute('aria-valuenow', level);
    
    // Set the appropriate color based on charge level
    if (level >= 80) {
        progressBar.className = 'progress-bar bg-success';
    } else if (level >= 50) {
        progressBar.className = 'progress-bar bg-info';
    } else if (level >= 20) {
        progressBar.className = 'progress-bar bg-warning';
    } else {
        progressBar.className = 'progress-bar bg-danger';
    }
    
    // Set status badge
    if (!occupied) {
        statusBadge.textContent = 'Empty';
        statusBadge.className = 'mb-0 badge bg-secondary';
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
    } else if (level >= 100) {
        statusBadge.textContent = 'Fully Charged';
        statusBadge.className = 'mb-0 badge bg-success';
    } else if (level > 0) {
        statusBadge.textContent = 'Charging';
        statusBadge.className = 'mb-0 badge bg-primary';
    } else {
        statusBadge.textContent = 'Connected';
        statusBadge.className = 'mb-0 badge bg-warning';
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
