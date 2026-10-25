import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import platform
import psutil
import datetime
import subprocess
import socket
import os
import sys
import json
import winreg
import ctypes
import time

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

# ─────────────────────────────────────────────────────────────
#  THEME / COLORS
# ─────────────────────────────────────────────────────────────
BG_DARK       = "#0f0f1a"
BG_CARD       = "#1a1a2e"
BG_CARD2      = "#16213e"
ACCENT        = "#7c3aed"        # Purple
ACCENT2       = "#06b6d4"        # Cyan
ACCENT3       = "#10b981"        # Green
WARN          = "#f59e0b"        # Amber
DANGER        = "#ef4444"        # Red
TEXT_PRIMARY  = "#f1f5f9"
TEXT_SECONDARY= "#94a3b8"
TEXT_DIM      = "#475569"
BORDER        = "#1e293b"

FONT_TITLE    = ("Segoe UI", 20, "bold")
FONT_HEADER   = ("Segoe UI", 13, "bold")
FONT_LABEL    = ("Segoe UI", 10, "bold")
FONT_VALUE    = ("Segoe UI", 10)
FONT_MONO     = ("Consolas", 9)
FONT_SMALL    = ("Segoe UI", 8)
FONT_BIG_NUM  = ("Segoe UI", 22, "bold")

# ─────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
def bytes_to_human(b):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"

def get_uptime():
    boot = psutil.boot_time()
    delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(boot)
    h, rem = divmod(int(delta.total_seconds()), 3600)
    m, s   = divmod(rem, 60)
    d = h // 24
    h = h % 24
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    parts.append(f"{m}m {s}s")
    return " ".join(parts)

def get_cpu_name():
    if WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            return c.Win32_Processor()[0].Name.strip()
        except:
            pass
    return platform.processor() or "Unknown"

def get_gpu_info():
    gpus = []
    if WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            for g in c.Win32_VideoController():
                ram = ""
                try:
                    vram = int(g.AdapterRAM)
                    ram = f" ({bytes_to_human(vram)})"
                except:
                    pass
                gpus.append(f"{g.Caption.strip()}{ram}")
        except:
            pass
    return gpus or ["N/A"]

def get_motherboard():
    if WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            mb = c.Win32_BaseBoard()[0]
            return f"{mb.Manufacturer.strip()} {mb.Product.strip()}"
        except:
            pass
    return "N/A"

def get_bios():
    if WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            b = c.Win32_BIOS()[0]
            return f"{b.Manufacturer.strip()} v{b.SMBIOSBIOSVersion.strip()}"
        except:
            pass
    return "N/A"

def get_windows_info():
    if WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            os_info = c.Win32_OperatingSystem()[0]
            name    = os_info.Caption.strip()
            build   = os_info.BuildNumber
            arch    = os_info.OSArchitecture
            return name, build, arch
        except:
            pass
    return platform.system() + " " + platform.release(), platform.version(), platform.machine()

def get_installed_software():
    software = []
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
    seen  = set()
    for hive in hives:
        for path in reg_paths:
            try:
                key = winreg.OpenKey(hive, path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub_name = winreg.EnumKey(key, i)
                        sub_key  = winreg.OpenKey(key, sub_name)
                        name     = winreg.QueryValueEx(sub_key, "DisplayName")[0].strip()
                        if not name or name in seen:
                            continue
                        seen.add(name)
                        version = ""
                        publisher = ""
                        install_date = ""
                        try: version      = winreg.QueryValueEx(sub_key, "DisplayVersion")[0].strip()
                        except: pass
                        try: publisher    = winreg.QueryValueEx(sub_key, "Publisher")[0].strip()
                        except: pass
                        try: install_date = winreg.QueryValueEx(sub_key, "InstallDate")[0].strip()
                        except: pass
                        software.append({
                            "name": name,
                            "version": version,
                            "publisher": publisher,
                            "install_date": install_date,
                        })
                    except:
                        pass
            except:
                pass
    return sorted(software, key=lambda x: x["name"].lower())

def get_network_info():
    info = []
    for name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                info.append({"adapter": name, "ip": addr.address, "mask": addr.netmask})
    return info

def get_battery():
    batt = psutil.sensors_battery()
    if batt is None:
        return None
    status = "Charging ⚡" if batt.power_plugged else "On Battery 🔋"
    secs   = batt.secsleft
    remain = ""
    if secs != psutil.POWER_TIME_UNLIMITED and secs > 0:
        h, m = divmod(secs // 60, 60)
        remain = f"  ~{h}h {m}m remaining"
    return {"percent": batt.percent, "status": status, "remain": remain}

def get_disk_info():
    disks = []
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disks.append({
                "device": p.device,
                "mount":  p.mountpoint,
                "fs":     p.fstype,
                "total":  usage.total,
                "used":   usage.used,
                "free":   usage.free,
                "pct":    usage.percent,
            })
        except:
            pass
    return disks

def get_temperatures():
    temps = {}
    try:
        sensors = psutil.sensors_temperatures()
        for name, entries in sensors.items():
            for e in entries:
                key = f"{name} – {e.label}" if e.label else name
                temps[key] = e.current
    except:
        pass
    return temps

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# ─────────────────────────────────────────────────────────────
#  CUSTOM WIDGETS
# ─────────────────────────────────────────────────────────────
class RoundedFrame(tk.Canvas):
    def __init__(self, parent, radius=12, bg=BG_CARD, border_color=BORDER, **kw):
        super().__init__(parent, bg=parent["bg"] if hasattr(parent, "__getitem__") else BG_DARK,
                         highlightthickness=0, **kw)
        self._radius = radius
        self._bg     = bg
        self._border = border_color
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        self.delete("bg_rect")
        w, h, r = self.winfo_width(), self.winfo_height(), self._radius
        self.create_rounded_rect(2, 2, w-2, h-2, r, fill=self._bg,
                                 outline=self._border, width=1, tags="bg_rect")
        self.tag_lower("bg_rect")

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1+r, y1,   x2-r, y1,
            x2,   y1,   x2,   y1+r,
            x2,   y2-r, x2,   y2,
            x2-r, y2,   x1+r, y2,
            x1,   y2,   x1,   y2-r,
            x1,   y1+r, x1,   y1,
            x1+r, y1,
        ]
        return self.create_polygon(pts, smooth=True, **kw)


class StatCard(tk.Frame):
    """Small stat card: icon + label + big value."""
    def __init__(self, parent, icon, label, value="—", color=ACCENT2, **kw):
        super().__init__(parent, bg=BG_CARD2, bd=0, **kw)
        self.configure(padx=14, pady=12)
        tk.Label(self, text=icon, font=("Segoe UI Emoji", 20),
                 bg=BG_CARD2, fg=color).pack(anchor="w")
        tk.Label(self, text=label, font=FONT_SMALL,
                 bg=BG_CARD2, fg=TEXT_SECONDARY).pack(anchor="w")
        self.val_lbl = tk.Label(self, text=value, font=FONT_BIG_NUM,
                                bg=BG_CARD2, fg=color)
        self.val_lbl.pack(anchor="w")

    def update_value(self, v):
        self.val_lbl.config(text=v)


class SectionHeader(tk.Frame):
    def __init__(self, parent, title, icon="", **kw):
        super().__init__(parent, bg=BG_DARK, **kw)
        tk.Label(self, text=f"  {icon}  {title}",
                 font=FONT_HEADER, bg=BG_DARK, fg=TEXT_PRIMARY,
                 pady=6).pack(side="left")
        sep = tk.Frame(self, bg=ACCENT, height=2)
        sep.pack(side="left", fill="x", expand=True, padx=(4,0), pady=(10,0))


class InfoRow(tk.Frame):
    def __init__(self, parent, label, value, lbl_w=200, val_color=TEXT_PRIMARY, **kw):
        super().__init__(parent, bg=BG_CARD, **kw)
        tk.Label(self, text=label, font=FONT_LABEL, bg=BG_CARD,
                 fg=TEXT_SECONDARY, width=lbl_w//8, anchor="w").pack(side="left", padx=(12,4), pady=3)
        tk.Label(self, text=value, font=FONT_VALUE, bg=BG_CARD,
                 fg=val_color, anchor="w", wraplength=500).pack(side="left", padx=4, pady=3)


class ColoredProgressBar(tk.Canvas):
    def __init__(self, parent, width=300, height=10, value=0, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=BG_CARD2, highlightthickness=0, **kw)
        self._bar_w = width
        self._bar_h = height
        self._pending_value = value
        self._ready = False
        # Draw only after widget is rendered to screen
        self.bind("<Map>", self._on_map)

    def _on_map(self, event=None):
        self._ready = True
        self.set(self._pending_value)

    def set(self, value):
        self._pending_value = value
        if not self._ready:
            return
        try:
            self.delete("all")
        except Exception:
            return
        w, h = self._bar_w, self._bar_h
        r = h // 2
        # Background track
        self._rounded_rect(0, 0, w, h, r, fill="#1e293b", outline="")
        # Fill
        if value > 0:
            fw = max(r * 2, int(w * value / 100))
            color = ACCENT3 if value < 60 else (WARN if value < 85 else DANGER)
            self._rounded_rect(0, 0, fw, h, r, fill=color, outline="")
        # Percentage text
        self.create_text(w // 2, h // 2,
                         text=f"{value:.0f}%", font=("Segoe UI", 7, "bold"),
                         fill=TEXT_PRIMARY)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1+r, y1,  x2-r, y1,
            x2,   y1,  x2,   y1+r,
            x2,   y2-r, x2,  y2,
            x2-r, y2,  x1+r, y2,
            x1,   y2,  x1,   y2-r,
            x1,   y1+r, x1,  y1,
            x1+r, y1,
        ]
        self.create_polygon(pts, smooth=True, **kw)


# ─────────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────────
class PCCheckerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🖥️  PC Status Checker  –  by Tools Team")
        self.geometry("1100x760")
        self.minsize(900, 620)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # Try to set taskbar icon
        try:
            self.iconbitmap(default="")
        except:
            pass

        self._live_running = True
        self._software_cache = None

        self._build_ui()
        self._load_data_async()
        self._start_live_monitor()

    # ── Build UI ──────────────────────────────────────────────
    def _build_ui(self):
        # ── Title bar ──
        title_bar = tk.Frame(self, bg=BG_CARD2, pady=8)
        title_bar.pack(fill="x")

        tk.Label(title_bar, text="🖥️  PC Status Checker",
                 font=FONT_TITLE, bg=BG_CARD2, fg=TEXT_PRIMARY,
                 padx=18).pack(side="left")

        self._admin_badge = tk.Label(
            title_bar,
            text="  ✅ Admin  " if is_admin() else "  ⚠️ Limited (no admin)  ",
            font=FONT_SMALL, bg=ACCENT3 if is_admin() else WARN,
            fg="#000", padx=6, pady=3, relief="flat"
        )
        self._admin_badge.pack(side="right", padx=12, pady=4)

        # Export button
        tk.Button(title_bar, text="💾  Export Report",
                  font=FONT_LABEL, bg=ACCENT, fg="#fff",
                  activebackground="#6d28d9", activeforeground="#fff",
                  relief="flat", padx=12, pady=4, cursor="hand2",
                  command=self._export_report).pack(side="right", padx=6, pady=4)

        # Refresh button
        tk.Button(title_bar, text="🔄  Refresh",
                  font=FONT_LABEL, bg=ACCENT2, fg="#000",
                  activebackground="#0891b2", activeforeground="#000",
                  relief="flat", padx=12, pady=4, cursor="hand2",
                  command=self._load_data_async).pack(side="right", padx=6, pady=4)

        # ── Notebook tabs ──
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Dark.TNotebook",
                        background=BG_DARK, borderwidth=0, tabmargins=0)
        style.configure("Dark.TNotebook.Tab",
                        background=BG_CARD2, foreground=TEXT_SECONDARY,
                        font=FONT_LABEL, padding=[14, 8],
                        borderwidth=0)
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#fff")])

        self._nb = ttk.Notebook(self, style="Dark.TNotebook")
        self._nb.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._tab_dashboard = self._make_scrollable_tab("📊  Dashboard")
        self._tab_system    = self._make_scrollable_tab("🖥️  System")
        self._tab_storage   = self._make_scrollable_tab("💾  Storage")
        self._tab_network   = self._make_scrollable_tab("🌐  Network")
        self._tab_software  = self._make_scrollable_tab("📦  Software")
        self._tab_process   = self._make_scrollable_tab("⚙️  Processes")

        self._build_dashboard_tab(self._tab_dashboard)
        self._build_system_tab(self._tab_system)
        self._build_storage_tab(self._tab_storage)
        self._build_network_tab(self._tab_network)
        self._build_software_tab(self._tab_software)
        self._build_process_tab(self._tab_process)

        # Status bar
        self._status_var = tk.StringVar(value="⏳ Loading system information…")
        status_bar = tk.Frame(self, bg=BG_CARD2, pady=3)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(status_bar, textvariable=self._status_var,
                 font=FONT_SMALL, bg=BG_CARD2, fg=TEXT_SECONDARY,
                 padx=12).pack(side="left")
        self._time_lbl = tk.Label(status_bar, text="", font=FONT_SMALL,
                                  bg=BG_CARD2, fg=TEXT_DIM, padx=12)
        self._time_lbl.pack(side="right")
        self._update_clock()

    def _make_scrollable_tab(self, title):
        frame = tk.Frame(self._nb, bg=BG_DARK)
        self._nb.add(frame, text=title)
        canvas = tk.Canvas(frame, bg=BG_DARK, highlightthickness=0)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=BG_DARK)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        def on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", on_configure)
        def on_canvas_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", on_canvas_resize)
        def on_mouse_wheel(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        return inner

    # ── Dashboard Tab ─────────────────────────────────────────
    def _build_dashboard_tab(self, parent):
        pad = dict(padx=10, pady=6)
        SectionHeader(parent, "Live Monitor", "📡").pack(fill="x", **pad)

        # Stat cards row
        cards_frame = tk.Frame(parent, bg=BG_DARK)
        cards_frame.pack(fill="x", padx=10, pady=4)

        self._card_cpu  = StatCard(cards_frame, "🧠", "CPU Usage",   color=ACCENT)
        self._card_mem  = StatCard(cards_frame, "💾", "RAM Usage",   color=ACCENT2)
        self._card_disk = StatCard(cards_frame, "💿", "Disk (C:)",   color=ACCENT3)
        self._card_up   = StatCard(cards_frame, "⏱️", "Uptime",      color=WARN)

        for c in (self._card_cpu, self._card_mem, self._card_disk, self._card_up):
            c.pack(side="left", fill="both", expand=True, padx=5, pady=4,
                   ipadx=4, ipady=4)

        # Progress bars
        SectionHeader(parent, "Resource Usage", "📈").pack(fill="x", **pad)

        bars_outer = tk.Frame(parent, bg=BG_CARD, bd=0)
        bars_outer.pack(fill="x", padx=10, pady=4)

        self._bars = {}
        for label, key, color in [
            ("CPU",           "cpu",  ACCENT),
            ("RAM",           "ram",  ACCENT2),
            ("Disk Read",     "dr",   ACCENT3),
            ("Disk Write",    "dw",   WARN),
            ("Network Send",  "ns",   "#a855f7"),
            ("Network Recv",  "nr",   "#ec4899"),
        ]:
            row = tk.Frame(bars_outer, bg=BG_CARD, pady=4)
            row.pack(fill="x", padx=14, pady=2)
            tk.Label(row, text=label, font=FONT_SMALL, bg=BG_CARD,
                     fg=TEXT_SECONDARY, width=14, anchor="w").pack(side="left")
            pb = ColoredProgressBar(row, width=500, height=14, value=0)
            pb.pack(side="left", padx=8)
            self._bars[key] = pb

        # Battery
        SectionHeader(parent, "Battery", "🔋").pack(fill="x", **pad)
        self._batt_frame = tk.Frame(parent, bg=BG_CARD)
        self._batt_frame.pack(fill="x", padx=10, pady=4)
        self._batt_lbl = tk.Label(self._batt_frame, text="Detecting…",
                                  font=FONT_VALUE, bg=BG_CARD, fg=TEXT_SECONDARY,
                                  padx=14, pady=8)
        self._batt_lbl.pack(anchor="w")

        # Quick info
        SectionHeader(parent, "Quick Info", "ℹ️").pack(fill="x", **pad)
        self._quick_frame = tk.Frame(parent, bg=BG_CARD)
        self._quick_frame.pack(fill="x", padx=10, pady=(4, 12))

    def _update_dashboard_quick(self, data):
        for w in self._quick_frame.winfo_children():
            w.destroy()
        rows = [
            ("Hostname",    data.get("hostname", "N/A")),
            ("OS",          data.get("os_name", "N/A")),
            ("CPU",         data.get("cpu_name", "N/A")),
            ("Total RAM",   data.get("ram_total", "N/A")),
            ("Windows Key", data.get("win_key",  "N/A")),
        ]
        for lbl, val in rows:
            InfoRow(self._quick_frame, lbl, val).pack(fill="x", pady=1)

    # ── System Tab ────────────────────────────────────────────
    def _build_system_tab(self, parent):
        pad = dict(padx=10, pady=6)
        self._sys_sections = {}
        for title, icon, key in [
            ("Operating System", "🪟", "os"),
            ("Processor (CPU)",  "🧠", "cpu"),
            ("Memory (RAM)",     "💾", "ram"),
            ("Graphics (GPU)",   "🎮", "gpu"),
            ("Motherboard & BIOS", "📟", "mb"),
        ]:
            SectionHeader(parent, title, icon).pack(fill="x", **pad)
            frame = tk.Frame(parent, bg=BG_CARD)
            frame.pack(fill="x", padx=10, pady=4)
            self._sys_sections[key] = frame

    def _populate_system_tab(self, data):
        def clear_fill(frame, rows, lbl_w=200):
            for w in frame.winfo_children():
                w.destroy()
            for lbl, val, *rest in rows:
                color = rest[0] if rest else TEXT_PRIMARY
                InfoRow(frame, lbl, val, lbl_w=lbl_w,
                        val_color=color).pack(fill="x", pady=1)

        os_name, build, arch = data["os_tuple"]
        clear_fill(self._sys_sections["os"], [
            ("OS Name",          os_name),
            ("Build",            build),
            ("Architecture",     arch),
            ("Computer Name",    data["hostname"]),
            ("Current User",     os.getlogin()),
            ("System Drive",     os.environ.get("SystemDrive", "C:")),
            ("Install Date",     data.get("win_install", "N/A")),
        ])

        cpu_f  = psutil.cpu_freq()
        cpu_c  = psutil.cpu_count(logical=False)
        cpu_lc = psutil.cpu_count(logical=True)
        freq   = f"{cpu_f.current:.0f} MHz (max {cpu_f.max:.0f} MHz)" if cpu_f else "N/A"
        clear_fill(self._sys_sections["cpu"], [
            ("CPU Name",         data["cpu_name"]),
            ("Physical Cores",   str(cpu_c)),
            ("Logical Cores",    str(cpu_lc)),
            ("Clock Speed",      freq),
            ("Current Usage",    f"{psutil.cpu_percent()}%"),
        ])

        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        clear_fill(self._sys_sections["ram"], [
            ("Total RAM",        bytes_to_human(vm.total)),
            ("Available",        bytes_to_human(vm.available)),
            ("Used",             bytes_to_human(vm.used)),
            ("Usage %",          f"{vm.percent}%"),
            ("Swap Total",       bytes_to_human(sm.total)),
            ("Swap Used",        bytes_to_human(sm.used)),
        ])

        for w in self._sys_sections["gpu"].winfo_children():
            w.destroy()
        for g in data["gpus"]:
            InfoRow(self._sys_sections["gpu"], "GPU", g).pack(fill="x", pady=1)

        clear_fill(self._sys_sections["mb"], [
            ("Motherboard",      data["motherboard"]),
            ("BIOS",             data["bios"]),
        ])

    # ── Storage Tab ───────────────────────────────────────────
    def _build_storage_tab(self, parent):
        SectionHeader(parent, "Disk Drives", "💽").pack(fill="x", padx=10, pady=6)
        self._disk_frame = tk.Frame(parent, bg=BG_DARK)
        self._disk_frame.pack(fill="x", padx=10, pady=4)

    def _populate_storage_tab(self, disks):
        for w in self._disk_frame.winfo_children():
            w.destroy()
        for d in disks:
            card = tk.Frame(self._disk_frame, bg=BG_CARD, pady=8)
            card.pack(fill="x", pady=4)
            header = tk.Frame(card, bg=BG_CARD)
            header.pack(fill="x", padx=12)
            tk.Label(header, text=f"💽  {d['device']}  [{d['mount']}]",
                     font=FONT_LABEL, bg=BG_CARD, fg=TEXT_PRIMARY).pack(side="left")
            tk.Label(header, text=f"  {d['fs']}",
                     font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM).pack(side="left")

            pb = ColoredProgressBar(card, width=600, height=16, value=d["pct"])
            pb.pack(padx=12, pady=6, anchor="w")

            info = tk.Frame(card, bg=BG_CARD)
            info.pack(fill="x", padx=12)
            for lbl, val in [
                ("Total", bytes_to_human(d["total"])),
                ("Used",  bytes_to_human(d["used"])),
                ("Free",  bytes_to_human(d["free"])),
                ("Used %", f"{d['pct']:.1f}%"),
            ]:
                col = tk.Frame(info, bg=BG_CARD, padx=20)
                col.pack(side="left")
                tk.Label(col, text=lbl, font=FONT_SMALL,
                         bg=BG_CARD, fg=TEXT_DIM).pack()
                tk.Label(col, text=val, font=FONT_LABEL,
                         bg=BG_CARD, fg=TEXT_PRIMARY).pack()

    # ── Network Tab ───────────────────────────────────────────
    def _build_network_tab(self, parent):
        SectionHeader(parent, "Network Adapters", "🌐").pack(fill="x", padx=10, pady=6)
        self._net_frame = tk.Frame(parent, bg=BG_DARK)
        self._net_frame.pack(fill="x", padx=10, pady=4)

        SectionHeader(parent, "Live Traffic", "📶").pack(fill="x", padx=10, pady=6)
        self._net_live_frame = tk.Frame(parent, bg=BG_CARD)
        self._net_live_frame.pack(fill="x", padx=10, pady=4)
        self._net_live_lbl = tk.Label(self._net_live_frame,
                                      text="Measuring…",
                                      font=FONT_VALUE, bg=BG_CARD,
                                      fg=TEXT_SECONDARY, padx=14, pady=8)
        self._net_live_lbl.pack(anchor="w")

    def _populate_network_tab(self, nets):
        for w in self._net_frame.winfo_children():
            w.destroy()
        if not nets:
            tk.Label(self._net_frame, text="No active adapters found.",
                     font=FONT_VALUE, bg=BG_DARK, fg=TEXT_DIM).pack()
            return
        for n in nets:
            card = tk.Frame(self._net_frame, bg=BG_CARD, pady=6)
            card.pack(fill="x", pady=3)
            InfoRow(card, "Adapter", n["adapter"]).pack(fill="x")
            InfoRow(card, "IP Address", n["ip"]).pack(fill="x")
            InfoRow(card, "Subnet Mask", n["mask"] or "N/A").pack(fill="x")

    # ── Software Tab ──────────────────────────────────────────
    def _build_software_tab(self, parent):
        SectionHeader(parent, "Installed Software", "📦").pack(fill="x", padx=10, pady=6)

        # Search bar
        search_frame = tk.Frame(parent, bg=BG_DARK)
        search_frame.pack(fill="x", padx=10, pady=4)
        tk.Label(search_frame, text="🔍 Search:", font=FONT_LABEL,
                 bg=BG_DARK, fg=TEXT_SECONDARY).pack(side="left")
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._filter_software)
        entry = tk.Entry(search_frame, textvariable=self._search_var,
                         font=FONT_VALUE, bg=BG_CARD2, fg=TEXT_PRIMARY,
                         insertbackground=TEXT_PRIMARY, relief="flat",
                         width=40, bd=0)
        entry.pack(side="left", padx=8, ipady=4)
        self._sw_count_lbl = tk.Label(search_frame, text="",
                                      font=FONT_SMALL, bg=BG_DARK,
                                      fg=TEXT_SECONDARY)
        self._sw_count_lbl.pack(side="left", padx=8)

        # Treeview
        tree_frame = tk.Frame(parent, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=4)

        cols = ("name", "version", "publisher", "install_date")
        style = ttk.Style()
        style.configure("SW.Treeview",
                        background=BG_CARD2, foreground=TEXT_PRIMARY,
                        rowheight=26, fieldbackground=BG_CARD2,
                        font=FONT_VALUE, borderwidth=0)
        style.configure("SW.Treeview.Heading",
                        background=BG_CARD, foreground=TEXT_SECONDARY,
                        font=FONT_LABEL, relief="flat")
        style.map("SW.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#fff")])

        self._sw_tree = ttk.Treeview(tree_frame, columns=cols,
                                      show="headings", style="SW.Treeview",
                                      height=22)
        for col, title, w in [
            ("name",         "Software Name",   360),
            ("version",      "Version",         120),
            ("publisher",    "Publisher",        220),
            ("install_date", "Install Date",     110),
        ]:
            self._sw_tree.heading(col, text=title,
                                  command=lambda c=col: self._sort_tree(c))
            self._sw_tree.column(col, width=w, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self._sw_tree.yview)
        self._sw_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._sw_tree.pack(fill="both", expand=True)

    def _fill_software_tree(self, software):
        self._software_cache = software
        self._sw_count_lbl.config(
            text=f"  {len(software)} apps installed")
        self._filter_software()

    def _filter_software(self, *_):
        query = self._search_var.get().lower()
        self._sw_tree.delete(*self._sw_tree.get_children())
        if not self._software_cache:
            return
        filtered = [s for s in self._software_cache
                    if query in s["name"].lower()
                    or query in s["publisher"].lower()]
        for s in filtered:
            self._sw_tree.insert("", "end", values=(
                s["name"], s["version"], s["publisher"], s["install_date"]))
        if query:
            self._sw_count_lbl.config(
                text=f"  {len(filtered)} / {len(self._software_cache)} apps")

    def _sort_tree(self, col):
        items = [(self._sw_tree.set(k, col), k)
                 for k in self._sw_tree.get_children("")]
        items.sort(key=lambda x: x[0].lower())
        for idx, (_, k) in enumerate(items):
            self._sw_tree.move(k, "", idx)

    # ── Process Tab ───────────────────────────────────────────
    def _build_process_tab(self, parent):
        SectionHeader(parent, "Running Processes", "⚙️").pack(fill="x", padx=10, pady=6)

        ctrl = tk.Frame(parent, bg=BG_DARK)
        ctrl.pack(fill="x", padx=10, pady=4)
        tk.Button(ctrl, text="🔄 Refresh Processes",
                  font=FONT_LABEL, bg=ACCENT2, fg="#000",
                  activebackground="#0891b2", relief="flat",
                  padx=10, pady=4, cursor="hand2",
                  command=self._load_processes).pack(side="left")
        self._proc_count_lbl = tk.Label(ctrl, text="",
                                        font=FONT_SMALL, bg=BG_DARK,
                                        fg=TEXT_SECONDARY, padx=10)
        self._proc_count_lbl.pack(side="left")

        proc_frame = tk.Frame(parent, bg=BG_DARK)
        proc_frame.pack(fill="both", expand=True, padx=10, pady=4)

        cols = ("pid", "name", "cpu", "mem", "status")
        style = ttk.Style()
        style.configure("Proc.Treeview",
                        background=BG_CARD2, foreground=TEXT_PRIMARY,
                        rowheight=24, fieldbackground=BG_CARD2,
                        font=FONT_MONO, borderwidth=0)
        style.configure("Proc.Treeview.Heading",
                        background=BG_CARD, foreground=TEXT_SECONDARY,
                        font=FONT_LABEL, relief="flat")
        style.map("Proc.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#fff")])

        self._proc_tree = ttk.Treeview(proc_frame, columns=cols,
                                        show="headings", style="Proc.Treeview",
                                        height=24)
        for col, title, w in [
            ("pid",    "PID",     70),
            ("name",   "Process", 260),
            ("cpu",    "CPU %",   90),
            ("mem",    "RAM",     100),
            ("status", "Status",  90),
        ]:
            self._proc_tree.heading(col, text=title)
            self._proc_tree.column(col, width=w, anchor="w")

        vsb2 = ttk.Scrollbar(proc_frame, orient="vertical",
                              command=self._proc_tree.yview)
        self._proc_tree.configure(yscrollcommand=vsb2.set)
        vsb2.pack(side="right", fill="y")
        self._proc_tree.pack(fill="both", expand=True)

    def _load_processes(self):
        self._proc_tree.delete(*self._proc_tree.get_children())
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent",
                                       "memory_info", "status"]):
            try:
                procs.append(p.info)
            except:
                pass
        # Sort by CPU
        procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)
        for p in procs[:200]:
            mem = bytes_to_human(p["memory_info"].rss) if p.get("memory_info") else "N/A"
            self._proc_tree.insert("", "end", values=(
                p["pid"],
                p["name"] or "?",
                f"{p.get('cpu_percent', 0):.1f}",
                mem,
                p.get("status", "?"),
            ))
        self._proc_count_lbl.config(text=f"  {len(procs)} processes")

    # ── Data Loading ──────────────────────────────────────────
    def _load_data_async(self):
        self._status_var.set("⏳ Collecting system information…")
        t = threading.Thread(target=self._collect_and_update, daemon=True)
        t.start()

    def _collect_and_update(self):
        data = {}
        try:
            data["hostname"]  = socket.gethostname()
            data["os_tuple"]  = get_windows_info()
            data["os_name"]   = data["os_tuple"][0]
            data["cpu_name"]  = get_cpu_name()
            data["gpus"]      = get_gpu_info()
            data["motherboard"] = get_motherboard()
            data["bios"]      = get_bios()
            vm = psutil.virtual_memory()
            data["ram_total"] = bytes_to_human(vm.total)
            # Windows product key (may require admin)
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                )
                data["win_key"] = winreg.QueryValueEx(key, "ProductId")[0]
            except:
                data["win_key"] = "N/A (needs admin)"
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                )
                data["win_install"] = winreg.QueryValueEx(key, "InstallDate")[0]
                ts = int(data["win_install"])
                data["win_install"] = str(datetime.datetime.fromtimestamp(ts).strftime("%d/%m/%Y"))
            except:
                data["win_install"] = "N/A"

            software = get_installed_software()
            nets     = get_network_info()
            disks    = get_disk_info()

            self.after(0, lambda: self._apply_data(data, software, nets, disks))
        except Exception as e:
            self.after(0, lambda: self._status_var.set(f"❌ Error: {e}"))

    def _apply_data(self, data, software, nets, disks):
        self._data = data
        self._update_dashboard_quick(data)
        self._populate_system_tab(data)
        self._populate_storage_tab(disks)
        self._populate_network_tab(nets)
        self._fill_software_tree(software)
        self._load_processes()
        self._status_var.set(
            f"✅ Loaded  ·  {len(software)} apps  ·  {socket.gethostname()}")

    # ── Live Monitor ──────────────────────────────────────────
    def _start_live_monitor(self):
        self._net_io_prev = psutil.net_io_counters()
        self._disk_io_prev = psutil.disk_io_counters()
        self._live_tick()

    def _live_tick(self):
        if not self._live_running:
            return
        try:
            cpu   = psutil.cpu_percent(interval=None)
            vm    = psutil.virtual_memory()
            ram   = vm.percent

            # Disk C:
            try:
                c_usage = psutil.disk_usage("C:\\").percent
            except:
                c_usage = 0

            self._card_cpu.update_value(f"{cpu:.0f}%")
            self._card_mem.update_value(f"{ram:.0f}%")
            self._card_disk.update_value(f"{c_usage:.0f}%")
            self._card_up.update_value(get_uptime())

            # Progress bars
            self._bars["cpu"].set(cpu)
            self._bars["ram"].set(ram)

            # Disk IO (as % of some max throughput – visual only)
            dio = psutil.disk_io_counters()
            if self._disk_io_prev:
                dr = (dio.read_bytes  - self._disk_io_prev.read_bytes)  / 1024 / 1024
                dw = (dio.write_bytes - self._disk_io_prev.write_bytes) / 1024 / 1024
                self._bars["dr"].set(min(100, dr * 2))
                self._bars["dw"].set(min(100, dw * 2))
            self._disk_io_prev = dio

            # Network IO
            nio = psutil.net_io_counters()
            if self._net_io_prev:
                ns = (nio.bytes_sent - self._net_io_prev.bytes_sent) / 1024
                nr = (nio.bytes_recv - self._net_io_prev.bytes_recv) / 1024
                self._bars["ns"].set(min(100, ns / 5))
                self._bars["nr"].set(min(100, nr / 5))
                self._net_live_lbl.config(
                    text=f"  ⬆ Send: {bytes_to_human(int(ns*1024))}/s     ⬇ Recv: {bytes_to_human(int(nr*1024))}/s")
            self._net_io_prev = nio

            # Battery
            batt = get_battery()
            if batt:
                txt = f"  {batt['status']}   {batt['percent']:.0f}%{batt['remain']}"
                color = ACCENT3 if batt["percent"] > 30 else DANGER
                self._batt_lbl.config(text=txt, fg=color)
            else:
                self._batt_lbl.config(text="  🔌 No battery (Desktop PC)", fg=TEXT_DIM)

        except Exception:
            pass

        self.after(2000, self._live_tick)

    # ── Clock ─────────────────────────────────────────────────
    def _update_clock(self):
        now = datetime.datetime.now().strftime("%A, %d/%m/%Y  %H:%M:%S")
        self._time_lbl.config(text=now)
        self.after(1000, self._update_clock)

    # ── Export Report ─────────────────────────────────────────
    def _export_report(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Report", "*.txt"), ("JSON", "*.json"), ("All", "*.*")],
            title="Save PC Report",
            initialfile=f"PC_Report_{socket.gethostname()}_{datetime.date.today()}"
        )
        if not path:
            return
        try:
            data = getattr(self, "_data", {})
            lines = []
            lines.append("=" * 60)
            lines.append("  PC STATUS REPORT")
            lines.append(f"  Generated: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            lines.append("=" * 60)
            lines.append(f"\nHostname   : {data.get('hostname', 'N/A')}")
            lines.append(f"OS         : {data.get('os_name', 'N/A')}")
            lines.append(f"CPU        : {data.get('cpu_name', 'N/A')}")
            lines.append(f"RAM        : {data.get('ram_total', 'N/A')}")
            lines.append(f"GPU(s)     : {', '.join(data.get('gpus', ['N/A']))}")
            lines.append(f"Motherboard: {data.get('motherboard', 'N/A')}")
            lines.append(f"BIOS       : {data.get('bios', 'N/A')}")
            lines.append(f"Product ID : {data.get('win_key', 'N/A')}")
            lines.append(f"Win Install: {data.get('win_install', 'N/A')}")
            lines.append(f"Uptime     : {get_uptime()}")

            lines.append("\n--- DISKS ---")
            for d in get_disk_info():
                lines.append(
                    f"  {d['device']} [{d['mount']}] {d['fs']} | "
                    f"Total:{bytes_to_human(d['total'])} "
                    f"Used:{bytes_to_human(d['used'])} "
                    f"Free:{bytes_to_human(d['free'])} "
                    f"({d['pct']:.1f}%)"
                )

            lines.append("\n--- NETWORK ---")
            for n in get_network_info():
                lines.append(f"  {n['adapter']} → {n['ip']}")

            if self._software_cache:
                lines.append(f"\n--- INSTALLED SOFTWARE ({len(self._software_cache)}) ---")
                for s in self._software_cache:
                    lines.append(
                        f"  {s['name']:50s} | {s['version']:20s} | {s['publisher']}")

            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            messagebox.showinfo("Export Successful",
                                f"Report saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ── Cleanup ───────────────────────────────────────────────
    def on_close(self):
        self._live_running = False
        self.destroy()


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = PCCheckerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
