import tkinter as tk
from tkinter import messagebox
import hashlib
import time
import os
import threading
import wmi  
import ctypes
import sys
import pythoncom   
import base64
import io
from PIL import Image, ImageTk

# ---------------- CONFIG ----------------
APP_NAME = "AURA USB SECURITY"
PASSWORD_HASH = hashlib.sha256("11".encode()).hexdigest()
attempts = 0



# ---------------- ADMIN CHECK ----------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

# ---------------- LOG ----------------
def log_event(text):
    with open("usb_log.txt", "a") as f:
        f.write(f"{text} at {time.ctime()}\n")


# ---------------- IMAGE LOAD ----------------
def load_logo():
    try:
        image_data = base64.b64decode(image_base64.strip())
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((120, 120), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        return photo
    except Exception as e:
        print("Image error:", e)
        return None

# ---------------- LOGIN ----------------
def login(event=None):   # event=None allows both Button click and Enter key
    global attempts
    entered = hashlib.sha256(entry.get().encode()).hexdigest()

    if entered == PASSWORD_HASH:
        log_event("Login Success")
        login_frame.pack_forget()
        main_frame.pack(expand=True)
    else:
        attempts += 1
        log_event("Wrong Password Attempt")
        messagebox.showerror("Error", "Wrong Password ❌")

        if attempts >= 3:
            messagebox.showwarning("Alert", "🚨 Intruder Detected!")
            disable_usb()

# ---------------- USB CONTROL ----------------
def disable_usb():
    os.system("reg add HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR /v Start /t REG_DWORD /d 4 /f")
    status.config(text="USB Disabled ❌", fg="#ef4444")
    log_event("USB Disabled")

def enable_usb():
    os.system("reg add HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR /v Start /t REG_DWORD /d 3 /f")
    status.config(text="USB Enabled ✅", fg="#22c55e")
    log_event("USB Enabled")

# ---------------- USB DETECTION ----------------
def monitor_usb():
    pythoncom.CoInitialize()
    c = wmi.WMI()
    known = set()

    while True:
        try:
            devices = c.Win32_USBHub()
            current = set([d.DeviceID for d in devices])

            for dev in current - known:
                log_event(f"USB Inserted: {dev}")
                status.config(text="USB Inserted 🔌", fg="#facc15")

            for dev in known - current:
                log_event(f"USB Removed: {dev}")
                status.config(text="USB Removed ❌", fg="#fb923c")

            known = current
            time.sleep(3)
        except:
            pass

# ---------------- PROJECT INFO ----------------
def show_project_info():
    if os.path.exists("project_info.pdf"):
        os.startfile("project_info.pdf")
    else:
        messagebox.showinfo(
            "Project Info",
            "AURA USB SECURITY\n\n"
            "• USB Enable / Disable\n"
            "• USB Monitoring\n"
            "• Intruder Detection\n"
            "• Secure Login System\n"
            "• Base64 Logo Encryption\n"
            "• Built using Python Tkinter"
        )

# ---------------- UI ----------------
root = tk.Tk()
root.title(APP_NAME)
root.geometry("600x540")
root.configure(bg="#0a0f1c")

# -------- LOGIN FRAME --------
login_frame = tk.Frame(root, bg="#0a0f1c")
login_frame.pack(expand=True)

# AURA LOGO
logo = load_logo()
if logo:
    lbl = tk.Label(login_frame, image=logo, bg="#0a0f1c")
    lbl.image = logo
    lbl.pack(pady=10)

tk.Label(login_frame, text=" 🔐 AURA USB SECURITY",
         fg="#00f7ff", bg="#0a0f1c",
         font=("Consolas", 20, "bold")).pack(pady=10)

tk.Label(login_frame, text="Enter Password",
         fg="#cbd5f5", bg="#0a0f1c",
         font=("Consolas", 12)).pack()

entry = tk.Entry(login_frame, show="*", width=25,
                 bg="#111827", fg="white",
                 insertbackground="white",
                 justify="center",
                 font=("Consolas", 12))
entry.pack(pady=10)
entry.focus()                      # Auto-focus on launch
entry.bind("<Return>", login)      # Press Enter to login

tk.Button(login_frame, text="LOGIN",
          command=login,
          bg="#00f7ff", fg="black",
          width=18,
          font=("Consolas", 11, "bold")).pack(pady=10)

# -------- MAIN FRAME --------
main_frame = tk.Frame(root, bg="#0a0f1c")

# -------- DASHBOARD LOGO --------
dash_logo = load_logo()
if dash_logo:
    dash_lbl = tk.Label(main_frame, image=dash_logo, bg="#0a0f1c")
    dash_lbl.image = dash_logo
    dash_lbl.pack(pady=(15, 5))

tk.Label(main_frame, text="🔓 AURA USB SECURITY DASHBOARD ",
         fg="#00f7ff", bg="#0a0f1c",
         font=("Consolas", 18, "bold")).pack(pady=(0, 10))
status = tk.Label(main_frame, text="Status: Monitoring...",
                  fg="#facc15", bg="#0a0f1c",
                  font=("Consolas", 12))
status.pack(pady=10)

def btn(text, cmd, color):
    return tk.Button(main_frame,
                     text=text,
                     command=cmd,
                     bg=color,
                     fg="white",
                     width=25,
                     font=("Consolas", 10, "bold"))

btn("🔴 Disable USB", disable_usb, "#dc2626").pack(pady=6)
btn("🟢 Enable USB",  enable_usb,  "#16a34a").pack(pady=6)
btn("📄 Project Info", show_project_info, "#6b7280").pack(pady=6)

tk.Button(main_frame, text="EXIT",
          command=root.quit,
          bg="black", fg="white",
          width=25).pack(pady=20)

# ---------------- THREAD ----------------
threading.Thread(target=monitor_usb, daemon=True).start()

# ---------------- RUN ----------------
root.mainloop()
