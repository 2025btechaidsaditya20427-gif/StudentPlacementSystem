import tkinter as tk
import subprocess
import sys
import os
import math
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_PATH = os.path.join(BASE_DIR, "dashboard.py")

# Colors
BG = "#10172A"
PANEL = "#151F36"
CYAN = "#246373"
WHITE = "#F4F8FF"
MUTED = "#9FB3D9"

WIDTH = 760
HEIGHT = 500

root = tk.Tk()
root.title("College Management System")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.resizable(False, False)
root.configure(bg=BG)

# Center window
root.update_idletasks()
x = (root.winfo_screenwidth() - WIDTH) // 2
y = (root.winfo_screenheight() - HEIGHT) // 2
root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

# Main canvas for animations
canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT,
    bg=BG,
    highlightthickness=0
)
canvas.pack(fill="both", expand=True)

# Background glow circles
canvas.create_oval(
    -180, -200, 350, 330,
    fill="#132747", outline=""
)
canvas.create_oval(
    500, 260, 920, 680,
    fill="#152441", outline=""
)

# Decorative lines
for i in range(8):
    canvas.create_line(
        0, 70 + i * 55,
        WIDTH, 70 + i * 55,
        fill="#17243B",
        width=1
    )

# Floating particles
particles = []

for _ in range(42):
    px = random.randint(0, WIDTH)
    py = random.randint(0, HEIGHT)
    size = random.choice([2, 3, 4])

    particle = canvas.create_oval(
        px, py, px + size, py + size,
        fill=random.choice(["#35D5FF", "#4777C7", "#8B9EFF"]),
        outline=""
    )

    particles.append({
        "id": particle,
        "x": px,
        "y": py,
        "size": size,
        "speed": random.uniform(0.3, 1.2)
    })

# Graduation icon and title
icon = canvas.create_text(
    WIDTH // 2, 72,
    text="🎓",
    font=("Arial", 35),
    fill=CYAN
)

title = canvas.create_text(
    WIDTH // 2, 135,
    text="COLLEGE MANAGEMENT SYSTEM",
    font=("Arial", 22, "bold"),
    fill=CYAN
)

subtitle = canvas.create_text(
    WIDTH // 2, 177,
    text="S M A R T   •   S I M P L E   •   E F F I C I E N T",
    font=("Arial", 10, "bold"),
    fill=WHITE
)

canvas.create_line(
    230, 205, 530, 205,
    fill="#2A496A",
    width=2
)

welcome_text = canvas.create_text(
    WIDTH // 2, 245,
    text="Welcome! Let's get started...",
    font=("Arial", 17, "bold"),
    fill=WHITE
)

description = canvas.create_text(
    WIDTH // 2, 275,
    text="Your campus, organized in one place.",
    font=("Arial", 11),
    fill=MUTED
)

# Progress bar background
BAR_X = 175
BAR_Y = 335
BAR_W = 410
BAR_H = 12

canvas.create_rectangle(
    BAR_X, BAR_Y,
    BAR_X + BAR_W, BAR_Y + BAR_H,
    fill="#293650",
    outline=""
)

progress_fill = canvas.create_rectangle(
    BAR_X, BAR_Y,
    BAR_X, BAR_Y + BAR_H,
    fill=CYAN,
    outline=""
)

status_text = canvas.create_text(
    WIDTH // 2, 365,
    text="Preparing your workspace... 0%",
    font=("Arial", 10),
    fill=MUTED
)

# Animated glowing highlight
glow = canvas.create_oval(
    BAR_X - 5, BAR_Y - 4,
    BAR_X + 5, BAR_Y + BAR_H + 4,
    fill=WHITE,
    outline=""
)

# Start button (shown after loading)
button = tk.Button(
    root,
    text="  OPEN DASHBOARD  ➜  ",
    font=("Arial", 11, "bold"),
    bg="#087FA8",
    fg="white",
    activebackground="#13A9D3",
    activeforeground="white",
    relief="flat",
    bd=0,
    padx=18,
    pady=10,
    cursor="hand2",
    command=lambda: open_dashboard()
)

button_window = canvas.create_window(
    WIDTH // 2, 425,
    window=button
)

button_window_item = button_window
canvas.itemconfigure(button_window_item, state="hidden")

progress = 0
loading_done = False
launching = False
pulse = 0
status_messages = [
    "Preparing your workspace...",
    "Loading college modules...",
    "Connecting application components...",
    "Almost ready..."
]


def animate_particles():
    for p in particles:
        p["y"] -= p["speed"]

        if p["y"] < -5:
            p["y"] = HEIGHT + 5
            p["x"] = random.randint(0, WIDTH)

        canvas.coords(
            p["id"],
            p["x"], p["y"],
            p["x"] + p["size"],
            p["y"] + p["size"]
        )

    root.after(35, animate_particles)


def animate_title():
    global pulse

    pulse += 1
    colors = ["#35D5FF", "#63DFFF", "#A4F0FF", "#63DFFF"]
    canvas.itemconfigure(title, fill=colors[(pulse // 8) % len(colors)])

    # Gentle vertical floating effect
    offset = math.sin(pulse / 12) * 2
    canvas.coords(icon, WIDTH // 2, 72 + offset)

    root.after(70, animate_title)


def animate_progress():
    global progress, loading_done

    if loading_done or launching:
        return

    progress = min(progress + random.choice([1, 1, 2]), 100)

    fill_width = BAR_W * progress / 100

    canvas.coords(
        progress_fill,
        BAR_X, BAR_Y,
        BAR_X + fill_width, BAR_Y + BAR_H
    )

    # Keep glow highlight near the leading edge
    glow_x = BAR_X + fill_width

    canvas.coords(
        glow,
        glow_x - 5, BAR_Y - 4,
        glow_x + 5, BAR_Y + BAR_H + 4
    )

    canvas.itemconfigure(
        status_text,
        text=f"{status_messages[min(progress // 25, 3)]} {progress}%"
    )

    if progress < 100:
        root.after(45, animate_progress)
    else:
        loading_done = True

        canvas.itemconfigure(
            status_text,
            text="Ready! Your workspace is waiting."
        )

        canvas.itemconfigure(button_window_item, state="normal")


def open_dashboard():
    global launching

    if launching:
        return

    if not os.path.isfile(DASHBOARD_PATH):
        canvas.itemconfigure(
            status_text,
            text="Error: dashboard.py not found!"
        )
        return

    launching = True
    button.configure(state="disabled", text="OPENING DASHBOARD...")

    try:
        subprocess.Popen(
            [sys.executable, DASHBOARD_PATH],
            cwd=BASE_DIR
        )
        root.destroy()

    except Exception as error:
        launching = False
        button.configure(
            state="normal",
            text="  OPEN DASHBOARD  ➜  "
        )
        canvas.itemconfigure(
            status_text,
            text=f"Could not open dashboard: {error}"
        )


def on_close():
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)

# Start animations
root.after(100, animate_particles)
root.after(100, animate_title)
root.after(500, animate_progress)

root.mainloop()