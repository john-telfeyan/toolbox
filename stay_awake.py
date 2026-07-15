"""
stay_awake.py — keep a Windows laptop awake for 45 minutes, then press Enter.

Quick + dirty. Windows only (uses ctypes / WinAPI).

Primary method: SetThreadExecutionState — tells Windows not to sleep/dim.
Backup method: nudge the mouse 1px every few seconds so you can *see* it working
               and to defeat idle policies that watch for input.
Finale:        sends an Enter keypress when the timer hits zero.

Run:  python stay_awake.py
"""

import ctypes
import random
import tkinter as tk
from tkinter import ttk

# ---- WinAPI bits --------------------------------------------------------
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_RETURN = 0x0D
KEYEVENTF_KEYUP = 0x0002


def keep_system_awake(on: bool):
    """Prevent (or allow) sleep + display-off via the OS itself."""
    if on:
        kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )
    else:
        kernel32.SetThreadExecutionState(ES_CONTINUOUS)


def jiggle_mouse():
    """Move the cursor 1px right then back — cheap, non-disruptive."""
    user32.mouse_event(0x0001, 1, 0, 0, 0)   # MOUSEEVENTF_MOVE
    user32.mouse_event(0x0001, -1, 0, 0, 0)


def press_enter():
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)


# ---- App ----------------------------------------------------------------
DURATION_SECONDS = 45 * 60


def next_jiggle_ms():
    """1 minute plus a random float of 1.000–90.000 s, returned in ms."""
    return int((60.0 + random.uniform(1.0, 90.0)) * 1000)


class StayAwakeApp:
    def __init__(self, root):
        self.root = root
        self.remaining = DURATION_SECONDS
        self.running = False
        self._tick_job = None
        self._jiggle_job = None

        root.title("Stay Awake")
        root.geometry("300x210")
        root.resizable(False, False)

        self.time_var = tk.StringVar(value=self._fmt(self.remaining))
        self.status_var = tk.StringVar(value="Ready")
        self.minutes_var = tk.StringVar(value="45")

        ttk.Label(root, textvariable=self.time_var,
                  font=("Segoe UI", 32)).pack(pady=(18, 0))
        ttk.Label(root, textvariable=self.status_var,
                  font=("Segoe UI", 9)).pack()

        dur = ttk.Frame(root)
        dur.pack(pady=(10, 0))
        ttk.Label(dur, text="Minutes:").grid(row=0, column=0, padx=(0, 4))
        self.minutes_entry = ttk.Entry(dur, textvariable=self.minutes_var,
                                       width=8, justify="center")
        self.minutes_entry.grid(row=0, column=1)

        btns = ttk.Frame(root)
        btns.pack(pady=12)
        self.start_btn = ttk.Button(btns, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=4)
        self.stop_btn = ttk.Button(btns, text="Stop", command=self.stop,
                                   state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=4)

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    @staticmethod
    def _fmt(secs):
        return f"{secs // 60:02d}:{secs % 60:02d}"

    def start(self):
        if self.running:
            return
        try:
            minutes = float(self.minutes_var.get())
            if minutes <= 0:
                raise ValueError
        except ValueError:
            self.status_var.set("Enter a positive number of minutes")
            return
        self.running = True
        self.remaining = round(minutes * 60)
        keep_system_awake(True)
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.minutes_entry.config(state="disabled")
        self.status_var.set("Awake — jiggling mouse…")
        self._tick()
        self._jiggle()

    def stop(self, finished=False):
        self.running = False
        keep_system_awake(False)
        for job in (self._tick_job, self._jiggle_job):
            if job:
                self.root.after_cancel(job)
        self._tick_job = self._jiggle_job = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.minutes_entry.config(state="normal")
        if not finished:
            self.status_var.set("Stopped")

    def _tick(self):
        self.time_var.set(self._fmt(self.remaining))
        if self.remaining <= 0:
            self.status_var.set("Time! Pressing Enter…")
            press_enter()
            self.stop(finished=True)
            self.status_var.set("Done — Enter pressed")
            return
        self.remaining -= 1
        self._tick_job = self.root.after(1000, self._tick)

    def _jiggle(self):
        if not self.running:
            return
        jiggle_mouse()
        self._jiggle_job = self.root.after(next_jiggle_ms(), self._jiggle)

    def on_close(self):
        keep_system_awake(False)  # never leave the flag stuck on
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    StayAwakeApp(root)
    root.mainloop()
