import tkinter as tk
from tkinter import messagebox
import datetime
import json
import os
import time
import winsound
import matplotlib.pyplot as plt
import numpy as np
from tkinter import ttk
# Constants
WORK_TYPES = {"Easy": 0.5, "Medium": 1, "Hard": 1.5}
DEFAULT_TYPE = "Medium"
LOG_FILE = "work_log.json"
DISTRACTION_LIMIT = 60  # 1 minute of inactivity
TOTAL_WEEKLY_TARGET = 128

# Globals
current_session = None
logs = []
last_activity_time = None
elapsed_seconds = 0
timer_running = False
total_hours_worked = 0
root = None
remaining_hours_label = None
timer_label = None

def log_activity(event=None):
    global last_activity_time
    last_activity_time = time.time()


def distraction_alert():
    global last_activity_time
    if current_session:
        idle_time = time.time() - last_activity_time
        if idle_time > DISTRACTION_LIMIT:
            try:
                for _ in range(5):
                    try:
                        winsound.Beep(1000, 300)
                    except RuntimeError as e:
                        print(f"Beep error: {e}")
                    time.sleep(0.3)

                if messagebox.askyesno(
                    "Distraction Alert",
                    "You have been idle for 1 minute. Do you want to continue working?"
                ):
                    log_activity()
                else:
                    stop_work()
            except Exception as e:
                print(f"Error during distraction alert: {e}")

    if root and root.winfo_exists():
        root.after(30000, distraction_alert)


def load_logs():
    """Load logs from the file and calculate total hours worked."""
    global logs, total_hours_worked
    total_hours_worked = 0  # Reset total hours worked
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as file:
                logs = json.load(file)
                if not isinstance(logs, list):
                    logs = []
            # Calculate total hours worked, ensuring all values are treated as floats
            for log in logs:
                duration = log.get("duration", 0)
                if isinstance(duration, (int, float)):
                    total_hours_worked += float(duration)  # Ensure it's a float in hours
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []
    update_remaining_hours_display()  # Update after loading logs

def update_remaining_hours_display():
    global remaining_hours_label, total_hours_worked
    if remaining_hours_label:
        remaining_hours = max(0, TOTAL_WEEKLY_TARGET - total_hours_worked)
        remaining_hours_label.config(text=f"Remaining Hours: {remaining_hours:.2f} hrs")




for log in logs:
    duration = log.get("duration", 0)
    if isinstance(duration, (int, float)):
        # Ensure durations are consistently in hours
        total_hours_worked += float(duration)



def save_logs():
    try:
        with open(LOG_FILE, 'w') as file:
            json.dump(logs, file, indent=4)
    except Exception as e:
        print(f"Error saving logs: {e}")
        messagebox.showerror("Error", "Failed to save logs. Please check permissions.")


def update_timer():
    global elapsed_seconds, timer_running
    if timer_running:
        elapsed_seconds += 1
        formatted_time = str(datetime.timedelta(seconds=elapsed_seconds))
        if root and timer_label.winfo_exists():
            timer_label.config(text=f"Timer: {formatted_time}")
            root.after(1000, update_timer)




def start_work(work_type):
    global current_session, last_activity_time, elapsed_seconds, timer_running
    if current_session:
        messagebox.showinfo("Session Active", "A session is already active!")
        return

    # Ensure description is only editable after session starts
    description_text.config(state=tk.NORMAL)  # Enable the text box
    description_text.delete("1.0", tk.END)  # Clear previous description

    description = description_text.get("1.0", "end").strip()
    if not description:
        description_text.insert("1.0", "Enter task description here...")  # Placeholder text

    current_session = {
        "start": datetime.datetime.now().isoformat(),
        "type": work_type,
        "description": description
    }
    last_activity_time = time.time()
    elapsed_seconds = 0
    timer_running = True
    update_timer()
    start_button.config(state=tk.DISABLED)  # Disable start button
    messagebox.showinfo("Work Started", f"Work session started! Type: {work_type}")


def stop_work():
    """Stop the current work session and log the duration."""
    global current_session, timer_running, total_hours_worked, elapsed_seconds
    if not current_session:
        messagebox.showinfo("No Active Session", "No active session to stop!")
        return

    timer_running = False
    end_time = datetime.datetime.now()
    current_session["end"] = end_time.isoformat()
    start_time = datetime.datetime.fromisoformat(current_session["start"])
    
    # Fix duration calculation to ensure it's in hours
    duration_in_seconds = (end_time - start_time).total_seconds()
    duration = duration_in_seconds / 3600  # Convert seconds to hours
    current_session["duration"] = round(duration, 2)  # Round to 2 decimal places

    logs.append(current_session)
    save_logs()

    # Update total hours worked accurately
    total_hours_worked += round(duration, 2)
    elapsed_seconds = 0
    update_remaining_hours_display()  # Update remaining hours dynamically

    # Reset session
    current_session = None
    description_text.config(state=tk.DISABLED)  # Disable description updates
    description_text.delete("1.0", tk.END)  # Clear description field

    messagebox.showinfo("Work Stopped", f"Work session stopped.\nDuration: {duration:.2f} hours logged.")
    timer_label.config(text="Timer: 00:00:00")
    start_button.config(state=tk.NORMAL)  # Enable start button


def update_description():
    """Allow updating the description only if a session is active."""
    global current_session
    if not current_session:
        messagebox.showinfo("No Active Session", "Please start a session to add or update the description.")
        return

    description = description_text.get("1.0", "end").strip()
    if description:
        current_session["description"] = description
        messagebox.showinfo("Description Updated", "Task description updated successfully!")
    else:
        messagebox.showerror("Error", "Description cannot be empty. Please enter a valid task description.")



def weekly_report():
    now = datetime.datetime.now()
    week_start = now - datetime.timedelta(days=now.weekday())
    total_hours = 0
    type_summary = {"Easy": 0, "Medium": 0, "Hard": 0}

    for log in logs:
        try:
            start = datetime.datetime.fromisoformat(log["start"])
            if start >= week_start:
                total_hours += log["duration"]
                type_summary[log["type"]] += log["duration"]
        except KeyError:
            continue

    report_text = "--- Weekly Report ---\n"
    report_text += f"Total Hours Worked: {total_hours:.2f}\n"
    for t, h in type_summary.items():
        report_text += f"{t} Work: {h:.2f} hrs\n"

    if total_hours == 0:
        report_text += "\nNo work logged this week."

    messagebox.showinfo("Weekly Report", report_text)


def show_progress():
    daily_hours = {day: 0 for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
    for log in logs:
        try:
            start_time = datetime.datetime.fromisoformat(log["start"])
            day_name = start_time.strftime("%a")
            daily_hours[day_name] += log.get("duration", 0)
        except KeyError:
            continue

    days = list(daily_hours.keys())
    hours_worked = list(daily_hours.values())

    if sum(hours_worked) == 0:
        messagebox.showinfo("Progress Chart", "No work data available to display.")
        return

    plt.figure(figsize=(10, 6))
    plt.bar(days, hours_worked, color='skyblue', edgecolor='blue')
    plt.xlabel("Days of the Week")
    plt.ylabel("Hours Worked")
    plt.title("Weekly Productivity Chart")
    plt.ylim(0, max(hours_worked) + 1)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def create_gui_modern():
    global root, timer_label, work_type_var, description_text, start_button, remaining_hours_label

    # Create the root window
    root = tk.Tk()
    root.title("Weekly Time Tracking System")
    root.geometry("450x450")  # Adjusted size for compact layout

    # Create a canvas for the gradient background
    gradient_canvas = tk.Canvas(root, width=450, height=450)
    gradient_canvas.pack(fill="both", expand=True)

    # Draw the gradient background
    def draw_gradient(canvas, width, height, color1, color2):
        r1, g1, b1 = root.winfo_rgb(color1)
        r2, g2, b2 = root.winfo_rgb(color2)

        r_ratio = (r2 - r1) / height
        g_ratio = (g2 - g1) / height
        b_ratio = (b2 - b1) / height

        for i in range(height):
            r = int(r1 + (r_ratio * i))
            g = int(g1 + (g_ratio * i))
            b = int(b1 + (b_ratio * i))
            color = f"#{r >> 8:02x}{g >> 8:02x}{b >> 8:02x}"
            canvas.create_rectangle(0, i, width, i + 1, outline=color, fill=color)

    draw_gradient(gradient_canvas, 450, 450, "#d9eaf7", "#fff4d9")  # Light blue to light yellow gradient

    # Create a frame for content
    content_frame = tk.Frame(gradient_canvas, bg="#ffffff", bd=2, relief="ridge")
    content_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=400)

    # Add a heading
    heading_label = tk.Label(
        content_frame, 
        text="Weekly Time Tracking System", 
        font=("Arial", 12, "bold"), 
        bg="#ffffff", 
        fg="#2c2c2c"
    )
    heading_label.pack(pady=5)

    # Timer and Remaining Hours Section
    timer_frame = tk.Frame(content_frame, bg="#f0f8ff", bd=1, relief="solid")
    timer_frame.pack(fill="x", padx=5, pady=5)

    timer_label = tk.Label(
        timer_frame, 
        text="Timer: 00:00:00", 
        font=("Arial", 12), 
        bg="#f0f8ff", 
        fg="#2c2c2c"
    )
    timer_label.pack(pady=2)

    remaining_hours_label = tk.Label(
        timer_frame, 
        text="Remaining Hours: 128.00 hrs", 
        font=("Arial", 10), 
        bg="#f0f8ff", 
        fg="#2c2c2c"
    )
    remaining_hours_label.pack(pady=2)

    # Work Type Section
    work_type_frame = tk.Frame(content_frame, bg="#e8f4fa", bd=1, relief="solid")
    work_type_frame.pack(fill="x", padx=5, pady=5)

    work_type_label = tk.Label(
        work_type_frame, 
        text="Select Work Type:", 
        font=("Arial", 10), 
        bg="#e8f4fa", 
        fg="#2c2c2c"
    )
    work_type_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")

    work_type_var = tk.StringVar(value=DEFAULT_TYPE)
    for i, (text, value) in enumerate(WORK_TYPES.items()):
        tk.Radiobutton(
            work_type_frame, 
            text=text, 
            variable=work_type_var, 
            value=text, 
            bg="#e8f4fa", 
            fg="#2c2c2c", 
            selectcolor="#e8f4fa"
        ).grid(row=i + 1, column=0, padx=5, pady=1, sticky="w")

    # Task Description Section
    description_frame = tk.Frame(content_frame, bg="#f4f9fd", bd=1, relief="solid")
    description_frame.pack(fill="x", padx=5, pady=5)

    description_label = tk.Label(
        description_frame, 
        text="Task Description:", 
        font=("Arial", 10), 
        bg="#f4f9fd", 
        fg="#2c2c2c"
    )
    description_label.pack(anchor="w", padx=5, pady=2)

    description_text = tk.Text(description_frame, height=3, width=35, font=("Arial", 9), bg="#ffffff", fg="#2c2c2c")
    description_text.pack(padx=5, pady=2)

    # Action Buttons
    action_frame = tk.Frame(content_frame, bg="#ffffff")
    action_frame.pack(fill="x", padx=5, pady=5)

    def create_gradient_button(parent, text, command):
        return tk.Button(
            parent, 
            text=text, 
            command=command, 
            font=("Arial", 8), 
            bg="#d9eaf7", 
            fg="#2c2c2c", 
            relief="flat", 
            activebackground="#fff4d9", 
            activeforeground="#2c2c2c"
        )

    start_button = create_gradient_button(action_frame, "Start Work", lambda: start_work(work_type_var.get()))
    stop_button = create_gradient_button(action_frame, "Stop Work", stop_work)

    start_button.pack(side="left", padx=5, pady=2)
    stop_button.pack(side="right", padx=5, pady=2)

    # Centered Update Description Button
    update_desc_button = create_gradient_button(action_frame, "Update Description", update_description)
    update_desc_button.pack(pady=5)

    # Report Buttons
    report_frame = tk.Frame(content_frame, bg="#ffffff")
    report_frame.pack(fill="x", padx=5, pady=5)

    weekly_report_button = create_gradient_button(report_frame, "Weekly Report", weekly_report)
    progress_chart_button = create_gradient_button(report_frame, "Progress Chart", show_progress)

    weekly_report_button.pack(side="left", padx=5, pady=2)
    progress_chart_button.pack(side="right", padx=5, pady=2)

    # Bind activity logging
    root.bind("<Motion>", log_activity)
    root.bind("<Key>", log_activity)

    distraction_alert()  # Start distraction alerts
    root.mainloop()



if __name__ == "__main__":
    
    create_gui_modern()  # Start the GUI

