# Virtual Environment Usage Guide

The PowerShell setup script (`setup_and_run.ps1`) has been enhanced to support automatic virtual environment creation and activation.

## New Features Added

### New Parameters:
- `-UseVenv`: Creates and activates a Python virtual environment before installing packages
- `-VenvName`: Specifies the name of the virtual environment directory (default: `.venv`)

## Usage Examples

### Basic usage with virtual environment:
```powershell
.\setup_and_run.ps1 -UseVenv
```

### Custom virtual environment name:
```powershell
.\setup_and_run.ps1 -UseVenv -VenvName "myproject_env"
```

### Skip installation but use virtual environment:
```powershell
.\setup_and_run.ps1 -UseVenv -SkipInstall
```

### Combine with custom port:
```powershell
.\setup_and_run.ps1 -UseVenv -Port 8080
```

## What happens when you use `-UseVenv`:

1. **Check if virtual environment exists**: If the specified venv directory already exists, it will be used
2. **Create virtual environment**: If it doesn't exist, a new one is created using `python -m venv <venv_name>`
3. **Activate virtual environment**: The script activates the virtual environment
4. **Install packages**: Dependencies are installed within the virtual environment
5. **Run application**: The Flask application runs using the virtual environment's Python

## Benefits:

- ✅ **Isolated dependencies**: Packages are installed only in the virtual environment
- ✅ **No system pollution**: Your system Python remains clean
- ✅ **Reproducible setup**: Each project has its own isolated environment
- ✅ **Easy cleanup**: Simply delete the venv folder to remove all packages

## Notes:

- The virtual environment is created in the same directory as the script
- If you already have a virtual environment created manually, the script will detect and use it
- The `.venv` directory is already included in `.gitignore` so it won't be committed to version control
