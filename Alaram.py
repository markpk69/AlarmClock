import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
import time
import threading
import pygame
import json

ALARM_FILE = 'C:/Users/Mark/AppData/Local/Programs/Python/Python312/alarms.json'
SOUND_FILE = 'C:/Users/Mark/AppData/Local/Programs/Python/Python312/alarm_sound.mp3'

class AlarmClock:
    def __init__(self, master):
        self.master = master
        master.title("Alarm Clock")

        pygame.mixer.init()

        self.alarms = []
        self.load_alarms()

        self.current_time_label = tk.Label(master, text="", font=("Helvetica", 48))
        self.current_time_label.pack()

        self.calendar = Calendar(master)
        self.calendar.pack()

        self.hour_var = tk.StringVar(master)
        self.minute_var = tk.StringVar(master)

        self.hour_combobox = ttk.Combobox(master, textvariable=self.hour_var,
                                          values=[f"{i:02d}" for i in range(24)], width=3)
        self.hour_combobox.pack()
        self.hour_combobox.set("00")

        self.minute_combobox = ttk.Combobox(master, textvariable=self.minute_var,
                                            values=[f"{i:02d}" for i in range(60)], width=3)
        self.minute_combobox.pack()
        self.minute_combobox.set("00")

        self.set_alarm_button = tk.Button(master, text="Set Alarm", command=self.set_alarm)
        self.set_alarm_button.pack()

        self.stop_alarm_button = tk.Button(master, text="Stop Alarm", state=tk.DISABLED, command=self.stop_alarm_sound)
        self.stop_alarm_button.pack()

        self.alarms_frame = tk.Frame(master)
        self.alarms_frame.pack()

        self.update_time()
        self.display_alarms()

    def update_time(self):
        now = datetime.now()
        self.current_time_label.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
        self.master.after(1000, self.update_time)

    def set_alarm(self):
        date_str = self.calendar.get_date()
        hour = int(self.hour_combobox.get())
        minute = int(self.minute_combobox.get())
        alarm_time = datetime.strptime(f"{date_str} {hour:02d}:{minute:02d}", '%m/%d/%y %H:%M')

        if alarm_time <= datetime.now():
            messagebox.showerror("Error", "Cannot set alarm for past time.")
            return

        alarm = {
            'time': alarm_time.strftime('%Y-%m-%d %H:%M'),
            'active': True
        }

        self.alarms.append(alarm)
        self.save_alarms()
        self.display_alarms()

    def display_alarms(self):
        for widget in self.alarms_frame.winfo_children():
            widget.destroy()

        for alarm in self.alarms:
            alarm_frame = tk.Frame(self.alarms_frame)
            alarm_frame.pack()

            alarm_label = tk.Label(alarm_frame, text=alarm['time'])
            alarm_label.pack(side=tk.LEFT)

            toggle_button_text = "ON" if alarm['active'] else "OFF"
            toggle_button = tk.Button(alarm_frame, text=toggle_button_text,
                                      command=lambda a=alarm: self.toggle_alarm(a))
            toggle_button.pack(side=tk.LEFT)
            
            delete_button = tk.Button(alarm_frame, text="Delete",
                                      command=lambda a=alarm: self.delete_alarm(a))
            delete_button.pack(side=tk.LEFT)

            if alarm['active']:
                self.schedule_alarm(alarm)

    def toggle_alarm(self, alarm):
        alarm['active'] = not alarm['active']
        self.save_alarms()
        self.display_alarms()

    def delete_alarm(self, alarm):
        self.alarms.remove(alarm)
        self.save_alarms()
        self.display_alarms()

    def schedule_alarm(self, alarm):
        alarm_time = datetime.strptime(alarm['time'], '%Y-%m-%d %H:%M')
        delay = (alarm_time - datetime.now()).total_seconds()
        if delay <= 0:
            return

        t = threading.Timer(delay, self.play_alarm_sound)
        t.start()

    def play_alarm_sound(self):
        self.stop_alarm_button.config(state=tk.NORMAL)
        pygame.mixer.music.load(SOUND_FILE)
        pygame.mixer.music.play(-1)

    def stop_alarm_sound(self):
        pygame.mixer.music.stop()
        self.stop_alarm_button.config(state=tk.DISABLED)

    def load_alarms(self):
        try:
            with open(ALARM_FILE, 'r') as file:
                self.alarms = json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load alarms: {e}")

    def save_alarms(self):
        with open(ALARM_FILE, 'w') as file:
            json.dump(self.alarms, file, indent=4)

def main():
    root = tk.Tk()
    alarm_clock = AlarmClock(root)
    root.mainloop()

if __name__ == "__main__":
    main()
