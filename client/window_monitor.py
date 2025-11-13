#!/usr/bin/env python3
import time
import os
import hashlib
from datetime import datetime
import pyautogui
import pytesseract
from PIL import Image

class WindowMonitor:
    def __init__(self, output_dir="screenshots"):
        self.output_dir = output_dir
        self.last_text_hash = None
        os.makedirs(output_dir, exist_ok=True)
        pyautogui.FAILSAFE = True
    
    def capture_screen(self):
        return pyautogui.screenshot()
    
    def extract_text(self, image):
        try:
            return pytesseract.image_to_string(image).strip()
        except:
            return ""
    
    def text_hash(self, text):
        return hashlib.md5(text.encode()).hexdigest()
    
    def save_image(self, image):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        image.save(filepath)
        print(f"Saved: {filepath}")
    
    def run(self):
        print("Starting window monitor... Press Ctrl+C to stop")
        try:
            while True:
                screenshot = self.capture_screen()
                text = self.extract_text(screenshot)
                current_hash = self.text_hash(text)
                
                if self.last_text_hash != current_hash:
                    self.save_image(screenshot)
                    self.last_text_hash = current_hash
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nMonitoring stopped")

if __name__ == "__main__":
    monitor = WindowMonitor()
    monitor.run()
