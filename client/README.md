# Window Monitor

Cross-platform Python desktop application that captures screen content, performs OCR, and saves images when text changes.

## Features

- Captures desktop screenshots every second
- Performs OCR to extract text content
- Saves images only when text content changes
- Cross-platform compatibility (Windows, macOS, Linux)
- Virtual environment support

## Prerequisites

- Python 3.8+ (works on 3.8–3.14)
- Tesseract OCR engine

### Install Tesseract:

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

## Setup

1. Run the setup script:

	 - Windows PowerShell
		 ```powershell
		 python .\setup.py
		 ```

	 - Linux/macOS
		 ```bash
		 python setup.py
		 ```

2. Activate virtual environment:

	 - Windows PowerShell
		 ```powershell
		 .\venv\Scripts\Activate.ps1
		 ```
		 If you see a scripts execution error, allow scripts for this session and try again:
		 ```powershell
		 Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
		 .\venv\Scripts\Activate.ps1
		 ```

	 - Windows CMD
		 ```bat
		 venv\Scripts\activate.bat
		 ```

	 - Linux/macOS
		 ```bash
		 source venv/bin/activate
		 ```

3. Run the application:

	 - Windows PowerShell
		 ```powershell
		 python .\window_monitor.py
		 ```

	 - Linux/macOS
		 ```bash
		 python window_monitor.py
		 ```

	4. Deactivate the virtual environment (when you’re done):

		 - Any shell
			 ```
			 deactivate
			 ```

### Troubleshooting

- If you are on Python 3.13+, older wheels like Pillow 10.1.0 may not install. The included setup and requirements automatically install compatible versions for newer Python.
- If installation still fails on Windows, upgrade tools inside the venv and retry setup:
	```powershell
	.\venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
	python .\setup.py
	```
- If activation fails in PowerShell with an error about `source`, use `Activate.ps1` as shown above.
- Ensure Tesseract is installed and on PATH. If not, set the path in code, e.g.:
	```python
	import pytesseract
	pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
	```

- macOS permissions: grant the terminal app Screen Recording and Accessibility permissions in
	System Settings → Privacy & Security, otherwise screenshots/automation may fail.
- Linux Wayland: on Wayland sessions, some screenshot backends are restricted. If captures fail,
	try using an X11 session or a screenshot backend compatible with your environment.
- PyAutoGUI fail-safe: moving the mouse to the top-left corner aborts the program by design. Keep
	the cursor away from (0,0) while monitoring, or disable with `pyautogui.FAILSAFE = False` (not recommended).
- OCR language: for non-English text, install the corresponding Tesseract language pack and call
	`pytesseract.image_to_string(image, lang='chi_sim')` (replace with your language code).

## Usage

- The application will start monitoring and create a `screenshots` directory
- Images are saved when text content changes
- Press Ctrl+C to stop monitoring
- Screenshots are named with timestamp: `capture_YYYYMMDD_HHMMSS.png`

## Configuration

Modify `window_monitor.py` to change:
- Screenshot directory
- Capture interval
- OCR settings
