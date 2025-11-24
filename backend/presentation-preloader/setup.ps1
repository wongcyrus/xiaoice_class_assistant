# PowerShell setup script for admin tools

# Install virtualenv if not already installed
pip install virtualenv

# Create virtual environment
python -m venv venv

# Activate virtual environment and install requirements
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Write-Host "`nSetup complete! Virtual environment is activated." -ForegroundColor Green
Write-Host "To activate in future sessions, run: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
