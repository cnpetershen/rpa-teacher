import json
import time
import os
from pynput import mouse, keyboard
import pygetwindow as gw

class RPARecorder:

    def __init__(self):
        self.events = []
        self.recording = False

    # -------------------------
    # start recording
    # -------------------------
    def start(self):
        self.recording = True
        self.events = []

        print("[Hermes] Recording started... Press Enter in terminal to stop.")

        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)

        self.mouse_listener.start()
        self.keyboard_listener.start()

    # -------------------------
    # stop recording
    # -------------------------
    def stop(self):
        self.recording = False

        self.mouse_listener.stop()
        self.keyboard_listener.stop()

        os.makedirs("logs", exist_ok=True)
        with open("logs/raw_events.json", "w", encoding="utf-8") as f:
            json.dump(self.events, f, indent=2, ensure_ascii=False)

        print(f"[Hermes] Saved {len(self.events)} events")
        return self.events

    # -------------------------
    # mouse click
    # -------------------------
    def on_click(self, x, y, button, pressed):
        if not self.recording or not pressed:
            return

        try:
            win = gw.getActiveWindow()
            title = win.title if win else "unknown"
            rel_x = x - win.left
            rel_y = y - win.top
        except:
            title = "unknown"
            rel_x = x
            rel_y = y

        self.events.append({
            "type": "click",
            "x": x,
            "y": y,
            "rel_x": rel_x,
            "rel_y": rel_y,
            "window": title,
            "ts": time.time()
        })

    # -------------------------
    # keyboard input
    # -------------------------
    def on_press(self, key):
        if not self.recording:
            return

        # Enter stops recording (event handled by run.py)
        if key == keyboard.Key.enter:
            self.recording = False
            return False

        try:
            k = key.char
        except:
            k = str(key)

        self.events.append({
            "type": "key",
            "key": k,
            "ts": time.time()
        })