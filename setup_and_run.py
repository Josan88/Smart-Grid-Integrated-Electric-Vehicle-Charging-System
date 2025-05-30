#!/usr/bin/env python3
"""
Smart Grid-Integrated EV Charging System - Setup and Run Script
Automatically sets up and runs the simulation dashboard
"""

import os
import sys
import subprocess
import argparse
import time
import webbrowser
import socket
from pathlib import Path

def colored_print(message, color='white'):
    """Print colored messages to terminal"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    
    if sys.platform == 'win32':
        # Enable ANSI escape sequences on Windows
        os.system('color')
    
    print(f"{colors.get(color, colors['white'])}{message}{colors['reset']}")

def check_python_version():
    """Check if Python version is 3.9 or higher"""
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 9:
        colored_print(f"✅ Python {version_info.major}.{version_info.minor}.{version_info.micro} detected", 'green')
        return True
    else:
        colored_print(f"❌ Python 3.9+ required, found {version_info.major}.{version_info.minor}.{version_info.micro}", 'red')
        return False

def check_required_files():
    """Check if all required files are present"""
    required_files = [
        'app.py',
        'simulation.py',
        'requirements.txt',
        'CompleteV1.slx',
        'sim_the_model.m',
        'templates/index.html',
        'static/css/style.css',
        'static/js/script.js'
    ]
    
    colored_print("🔍 Checking required files...", 'cyan')
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        colored_print("Missing required files. Please ensure all project files are present.", 'red')
        return False
    
    colored_print("✅ All required files found", 'green')
    return True

def check_matlab():
    """Check if MATLAB is available"""
    colored_print("🔍 Checking MATLAB availability...", 'cyan')
    
    # Try to find MATLAB in PATH
    try:
        result = subprocess.run(['matlab', '-batch', 'exit'], 
                              capture_output=True, timeout=10)
        colored_print("✅ MATLAB found in PATH", 'green')
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Check common installation paths on Windows
    if sys.platform == 'win32':
        matlab_paths = [
            r'C:\Program Files\MATLAB\R2023b\bin\matlab.exe',
            r'C:\Program Files\MATLAB\R2024a\bin\matlab.exe',
            r'C:\Program Files\MATLAB\R2024b\bin\matlab.exe',
        ]
        
        for path in matlab_paths:
            if Path(path).exists():
                colored_print(f"✅ MATLAB found at: {path}", 'green')
                return True
    
    colored_print("⚠️  MATLAB not found. The simulation may not work properly.", 'yellow')
    colored_print("   Please ensure MATLAB R2023b+ is installed and accessible.", 'yellow')
    return False

def install_dependencies():
    """Install Python dependencies from requirements.txt"""
    colored_print("📦 Installing Python dependencies...", 'cyan')
    
    if not Path('requirements.txt').exists():
        colored_print("❌ requirements.txt not found", 'red')
        return False
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # Install requirements
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        
        colored_print("✅ Dependencies installed successfully", 'green')
        return True
    except subprocess.CalledProcessError as e:
        colored_print(f"❌ Failed to install dependencies: {e}", 'red')
        return False

def is_port_available(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_available_port(start_port=5000, max_attempts=100):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")

def get_processes_using_port(port):
    """Get list of processes using a specific port (Windows only)"""
    if sys.platform != 'win32':
        return []
    
    try:
        import psutil
        connections = psutil.net_connections()
        processes = []
        for conn in connections:
            if conn.laddr.port == port:
                try:
                    proc = psutil.Process(conn.pid)
                    processes.append({
                        'pid': conn.pid,
                        'name': proc.name(),
                        'status': conn.status
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return processes
    except ImportError:
        # psutil not available, use netstat
        try:
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            processes = []
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        processes.append({'pid': pid, 'name': 'Unknown', 'status': 'LISTENING'})
            return processes
        except Exception:
            return []

def start_application(port=5000, host='localhost', no_browser=False):
    """Start the Flask application"""
    colored_print("🚀 Starting Smart Grid EV Charging System...", 'cyan')
    print(f"   Port: {port}")
    print(f"   URL: http://{host}:{port}")
    
    # Check port availability one more time before starting
    if not is_port_available(port):
        colored_print(f"⚠️  Port {port} is already in use", 'yellow')
        return False
    
    try:
        colored_print("✅ Application starting...", 'green')
        
        if not no_browser:
            colored_print("🌐 Opening browser in 3 seconds...", 'yellow')
            # Start browser after delay
            import threading
            def open_browser():
                time.sleep(3)
                webbrowser.open(f"http://{host}:{port}")
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
        
        # Run the Flask application
        subprocess.run([sys.executable, 'app.py', '--port', str(port), '--host', host] + 
                      (['--no-browser'] if no_browser else []))
        
    except KeyboardInterrupt:
        colored_print("\n🛑 Application stopped by user", 'yellow')
    except subprocess.CalledProcessError as e:
        colored_print(f"❌ Failed to start application: {e}", 'red')
        return False
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Smart Grid EV Charging System Setup Script')
    parser.add_argument('--skip-install', action='store_true', help='Skip Python package installation')
    parser.add_argument('--quick-start', action='store_true', help='Skip dependency checks and start immediately')
    parser.add_argument('--port', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--host', default='localhost', help='Host address (default: localhost)')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--auto-port', action='store_true', help='Automatically find and use next available port if specified port is busy')
    
    args = parser.parse_args()
    
    # Print header
    colored_print("🔋 Smart Grid-Integrated EV Charging System", 'magenta')
    colored_print("=" * 43, 'magenta')
    print()
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    colored_print(f"📁 Working directory: {script_dir}", 'cyan')
    
    if not args.quick_start:
        colored_print("🔍 Performing system checks...", 'cyan')
        
        # Check Python version
        if not check_python_version():
            colored_print("Please install Python 3.9 or higher", 'red')
            return 1
        
        # Check required files
        if not check_required_files():
            return 1
        
        # Check MATLAB (warning only)
        check_matlab()
        
        # Install dependencies if not skipped
        if not args.skip_install:
            if not install_dependencies():
                return 1
        else:
            colored_print("⚠️  Skipping dependency installation", 'yellow')
    else:
        colored_print("⚡ Quick start mode - skipping checks", 'yellow')
    
    # Check port availability - simplified logic like PowerShell version
    original_port = args.port
    if not is_port_available(args.port):
        colored_print(f"⚠️  Port {args.port} is not available", 'yellow')
        
        # Show processes using the port
        processes = get_processes_using_port(args.port)
        if processes:
            colored_print("   Processes using this port:", 'yellow')
            for proc in processes:
                colored_print(f"   • PID {proc['pid']}: {proc['name']} ({proc['status']})", 'yellow')
        
        # Automatically find and use next available port (like PowerShell version)
        try:
            new_port = find_available_port(args.port)
            colored_print(f"✅ Found available port: {new_port}", 'green')
            args.port = new_port
        except RuntimeError as e:
            colored_print(f"❌ Could not find an available port starting from {original_port}", 'red')
            return 1
    else:
        colored_print(f"✅ Port {args.port} is available", 'green')
    
    colored_print("✅ Setup completed successfully!", 'green')
    
    # Show final configuration if port changed
    if args.port != original_port:
        colored_print(f"📡 Using port {args.port} instead of {original_port}", 'cyan')
    
    print()
    colored_print("=" * 50, 'magenta')
    colored_print("🎯 READY TO START", 'magenta')
    colored_print("=" * 50, 'magenta')
    print()
    
    # Start the application
    if not start_application(args.port, args.host, args.no_browser):
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
