# Window Monitor

Cross-platform Python desktop application that captures screen content, performs OCR, and saves images when text changes.

## Features

- Captures desktop screenshots every second
- Performs OCR to extract text content
- Saves images only when text content changes
- Cross-platform compatibility (Windows, macOS, Linux)
- Virtual environment support

## Prerequisites

- Python 3.7+
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
```bash
python setup.py
```

2. Activate virtual environment:
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Run the application:
```bash
python window_monitor.py
```

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
