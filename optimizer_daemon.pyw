import os
import sys
import shutil
import getpass
import time
import threading
import winreg
import psutil
import wmi
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

# --- Visual Theme Configuration (Navy Blue & Gold) ---
COLORS = {
    "navy_bg": "#0d1b2a",      # Primary deep navy background
    "navy_card": "#1b263b",    # Secondary navy for cards and frames
    "gold": "#c9a227",         # Executive gold accent for titles and active states
    "gold_hover": "#e2c780",   # Muted gold for button hover states
    "text_light": "#f6ead1",   # Premium cream text for high readability
    "text_muted": "#a1b1c2"    # Grayish-blue text for background details
}

ctk.set_appearance_mode("dark")

class OptimizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Base Window Configurations
        self.title("OPTIMIZER PRO v2.0 - Command Center")
        self.geometry("1050x600")
        self.configure(fg_color=COLORS["navy_bg"])
        self.resizable(False, False)

        # Real-time System Statistics Counters
        self.stats_deleted_files = 0
        self.stats_deleted_folders = 0
        self.stats_browser_cache = 0
        self.stats_killed_apps = 0
        self.usb_logs = []

        # Initialize UI Components
        self.setup_ui()

        # Initialize Background Daemons and Event Listeners
        self.start_background_engines()

    def setup_ui(self):
        # 1. Sidebar Navigation Panel
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COLORS["navy_card"], border_width=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Application Logo
        self.logo_label = ctk.CTkLabel(self.sidebar, text="OPTIMIZER PRO",
                                       font=ctk.CTkFont(family="Poppins", size=22, weight="bold"),
                                       text_color=COLORS["gold"])
        self.logo_label.pack(pady=(40, 30), padx=20)

        # Navigation Buttons
        self.btn_dashboard = self.create_sidebar_btn("📊 Dashboard", self.show_dashboard)
        self.btn_security = self.create_sidebar_btn("🛡️ USB Shield", self.show_security)

        # Dedicated Absolute Purge Trigger
        self.btn_purge = ctk.CTkButton(self.sidebar, text="⚡ PURGE NOW", fg_color=COLORS["gold"],
                                      text_color=COLORS["navy_bg"], hover_color=COLORS["gold_hover"],
                                      font=ctk.CTkFont(size=14, weight="bold"), height=40,
                                      command=self.manual_purge)
        self.btn_purge.pack(side="bottom", pady=40, padx=20, fill="x")

        # 2. Main Content Display Area
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        # Load Default Dashboard View on Startup
        self.show_dashboard()

    def create_sidebar_btn(self, text, command):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent",
                            text_color=COLORS["text_light"], hover_color="#2a3b52",
                            font=ctk.CTkFont(size=15, weight="normal"),
                            anchor="w", height=45, corner_radius=8, command=command)
        btn.pack(fill="x", padx=15, pady=5)
        return btn

    def show_dashboard(self):
        self.clear_main_view()

        # Section Header
        header = ctk.CTkLabel(self.main_view, text="Live Performance Monitors",
                              font=ctk.CTkFont(size=26, weight="bold"), text_color=COLORS["gold"])
        header.pack(anchor="w", pady=(0, 25))

        # Metric Cards Container Layout
        self.cards_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=10)

        # Create Dynamic Stat Cards
        self.cpu_card = self.create_stat_card(self.cards_frame, "CPU CORE LOAD", "0%")
        self.ram_card = self.create_stat_card(self.cards_frame, "RAM VOLATILITY", "0%")
        self.storage_card = self.create_stat_card(self.cards_frame, "SYSTEM CLEANED", "0 Items")

    def show_security(self):
        self.clear_main_view()

        # Section Header
        header = ctk.CTkLabel(self.main_view, text="USB Shield - Live Incident Logs",
                              font=ctk.CTkFont(size=26, weight="bold"), text_color=COLORS["gold"])
        header.pack(anchor="w", pady=(0, 25))

        # Terminal Style Logging Interface
        self.log_box = ctk.CTkTextbox(self.main_view, fg_color=COLORS["navy_card"],
                                      text_color=COLORS["text_light"], font=("Consolas", 14),
                                      border_color="#3a3018", border_width=1, corner_radius=12)
        self.log_box.pack(fill="both", expand=True)

        # Populate Historical Logs
        if not self.usb_logs:
            self.log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ Security Agent Online. Monitoring host endpoints...\n")
        else:
            for log in self.usb_logs:
                self.log_box.insert("end", log + "\n")
        self.log_box.configure(state="disabled")

    def create_stat_card(self, parent, title, value):
        card = ctk.CTkFrame(parent, fg_color=COLORS["navy_card"], width=240, height=140,
                            corner_radius=15, border_width=1, border_color="#3a3018")
        card.pack(side="left", padx=10, expand=True)
        card.pack_propagate(False)

        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_muted"])
        lbl_title.pack(pady=(25, 5))

        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=34, weight="bold"), text_color=COLORS["gold"])
        lbl_val.pack()
        return lbl_val

    def clear_main_view(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

    # --- Background Execution Framework ---
    def start_background_engines(self):
        # 1. Initialize Real-Time Resource Monitoring Thread
        threading.Thread(target=self.resource_monitor_loop, daemon=True).start()
        # 2. Initialize Event-Driven USB Hardware Detection Thread
        threading.Thread(target=self.usb_guard_listener, daemon=True).start()

    def resource_monitor_loop(self):
        while True:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent

            # Update Dashboard Widgets Object Properties Safely
            try:
                self.cpu_card.configure(text=f"{cpu}%")
                self.ram_card.configure(text=f"{ram}%")

                total_cleaned = self.stats_deleted_files + self.stats_browser_cache
                self.storage_card.configure(text=f"{total_cleaned} Items")

                # Automated RAM mitigation threshold if memory exceeds 85.0%
                if ram > 85.0:
                    self.auto_kill_heavy_apps()
            except:
                pass

            time.sleep(1)

    def usb_guard_listener(self):
        try:
            c = wmi.WMI()
            watcher = c.Win32_Volume.watch_for("creation")
            while True:
                usb_drive = watcher()
                drive_letter = usb_drive.DriveLetter

                if drive_letter:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_entry = f"[{timestamp}] 🔌 Peripheral Detected: External Drive mapped to ({drive_letter})"
                    self.usb_logs.append(log_entry)

                    # File-level Root Signature Scanning for Dangerous Scripts/Executables
                    suspicious_files = []
                    danger_extensions = ('.exe', '.bat', '.vbs', '.cmd', '.inf', '.lnk')
                    try:
                        for item in os.listdir(drive_letter + "\\"):
                            if item.lower().endswith(danger_extensions):
                                suspicious_files.append(item)
                    except:
                        continue

                    if suspicious_files:
                        alert_msg = f"[{timestamp}] 🚨 SECURITY ALERT: Executable payload detected on {drive_letter} -> {suspicious_files}"
                        self.usb_logs.append(alert_msg)

                        # Generate Instant UI Warning Dialog via Thread Isolation
                        popup_text = f"🛡️ USB Shield Alert!\n\nSuspicious files found on {drive_letter}:\n" + "\n".join([f"• {f}" for f in suspicious_files])
                        threading.Thread(target=lambda: messagebox.showwarning("Security Shield", popup_text), daemon=True).start()

                    # Dynamic Refresh of Security Log Panel if Active
                    try:
                        self.show_security()
                    except: pass
        except:
            pass

    def auto_kill_heavy_apps(self):
        heavy_process = None
        max_memory = 0
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                proc_mem = proc.info['memory_percent']
                if proc_mem > max_memory:
                    max_memory = proc_mem
                    heavy_process = proc
            except: continue

        if heavy_process and heavy_process.info['name'] not in ['System', 'svchost.exe', 'explorer.exe']:
            try:
                heavy_process.terminate()
                self.stats_killed_apps += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.usb_logs.append(f"[{timestamp}] 🛡️ Memory Guard terminated heavy app: {heavy_process.info['name']}")
            except: pass

    def manual_purge(self):
        """Triggers the Deep Cleaning Subprocess instantly."""
        self.btn_purge.configure(text="⚡ PURGING...", state="disabled")
        threading.Thread(target=self.run_deep_clean).start()

    def run_deep_clean(self):
        username = getpass.getuser()
        paths_to_clean = [r"C:\Windows\Temp", f"C:\\Users\\{username}\\AppData\\Local\\Temp", r"C:\Windows\Prefetch"]
        browser_paths = [
            f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache\\Cache_Data",
            f"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache\\Cache_Data"
        ]

        # 1. System Temporary Directory Wipe Execution Loop
        for dir_path in paths_to_clean:
            if not os.path.exists(dir_path): continue
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                        self.stats_deleted_files += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        self.stats_deleted_folders += 1
                except: pass

        # 2. Advanced Browser Cache Garbage Collection
        for path in browser_paths:
            if not os.path.exists(path): continue
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                        self.stats_browser_cache += 1
                except: pass

        # Reset UI State and Throw Executive Completion Dialog
        self.btn_purge.configure(text="⚡ PURGE NOW", state="normal")


if __name__ == "__main__":
    # Command Line Arguments Evaluation Core
    if len(sys.argv) > 1 and sys.argv[1] == "--silent-purge":
        # Full Silent Background Execution Loop (Triggered every 12 hours)
        app = OptimizerApp()
        app.run_deep_clean()
        sys.exit()

    elif len(sys.argv) > 1 and sys.argv[1] == "--startup-report":
        # Scheduled Windows OnLogon Boot Sequence Optimization
        app = OptimizerApp()
        app.run_deep_clean()

        total_items = app.stats_deleted_files + app.stats_browser_cache
        messagebox.showinfo(
            "Executive Report - Optimizer Pro",
            f"Welcome back, Boss!\n\n"
            f"While your system was booting up, Optimizer Pro initialized a rapid deployment sweep:\n"
            f"• Vaporized {total_items} junk files, logs, and locked browser cache items.\n\n"
            f"Your environment is highly optimized. Active USB Shield is standing guard in the background!"
        )
        app.mainloop()

    else:
        # Standard Active User UI Deployment
        app = OptimizerApp()
        app.mainloop()
