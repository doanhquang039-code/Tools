"""
╔══════════════════════════════════════════════════════════╗
║        PC Status & License Checker                      ║
║        Launcher-style Desktop Tool                      ║
║        GitHub → tải về → double-click run.bat → Done    ║
╚══════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading, platform, psutil, datetime, subprocess
import socket, os, sys, json, winreg, ctypes, time, re

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

# ─────────────────────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────────────────────
C = {
    "bg":        "#0d1117",
    "surface":   "#161b22",
    "surface2":  "#1c2128",
    "border":    "#30363d",
    "accent":    "#7c3aed",
    "accent_h":  "#9f67ff",
    "green":     "#23d18b",
    "green_bg":  "#0d2518",
    "red":       "#f85149",
    "red_bg":    "#2a0d0d",
    "yellow":    "#e3b341",
    "yellow_bg": "#2a1f0d",
    "cyan":      "#39c5cf",
    "blue":      "#58a6ff",
    "text":      "#e6edf3",
    "text2":     "#8b949e",
    "text3":     "#484f58",
    "white":     "#ffffff",
}

FONTS = {
    "hero":   ("Segoe UI", 24, "bold"),
    "title":  ("Segoe UI", 15, "bold"),
    "header": ("Segoe UI", 11, "bold"),
    "label":  ("Segoe UI", 10, "bold"),
    "body":   ("Segoe UI", 10),
    "small":  ("Segoe UI", 8),
    "mono":   ("Consolas", 9),
    "big":    ("Segoe UI", 20, "bold"),
    "emoji":  ("Segoe UI Emoji", 28),
}

# ─────────────────────────────────────────────────────────────
#  PIRACY SIGNATURES DATABASE
# ─────────────────────────────────────────────────────────────
CRACK_KEYWORDS = [
    "kmspico", "kmsauto", "kms_vl_all", "re-loader activator",
    "aact", "hwidgen", "hwid gen", "microsoft activation scripts",
    "ratiborus", "office toolkit", "ez-activator", "windows loader",
    "daz loader", "removewat", "keygen", "keymaker",
    "autocad crack", "adobe crack", "photoshop crack",
    "idm crack", "winrar crack", "iobit uninstaller crack",
    "malwarebytes crack", "activator", "warez",
    "crack", "patch", "serial key", "license key generator",
    "product key generator",
]

SUSPICIOUS_PATHS = [
    r"temp\crack", r"downloads\crack", r"desktop\crack",
    r"temp\keygen", r"downloads\keygen", r"programdata\kms",
]

CRACK_PROCESSES = {
    "kmspico.exe", "kmsauto.exe", "aact.exe", "hwidgen.exe",
    "autokmslite.exe", "kms-r@in.exe", "kmsss.exe",
}

# ─────────────────────────────────────────────────────────────
#  DATA HELPERS
# ─────────────────────────────────────────────────────────────
def bytes2h(b):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} PB"

def get_uptime():
    d = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    h, r = divmod(int(d.total_seconds()), 3600)
    m = r // 60
    return f"{h//24}d {h%24}h {m}m" if h >= 24 else f"{h}h {m}m"

def wmi_get(cls, attr, idx=0, default="N/A"):
    if not WMI_AVAILABLE:
        return default
    try:
        c = wmi.WMI()
        return getattr(getattr(c, cls)()[idx], attr).strip() or default
    except:
        return default

def reg_get(hive, path, key, default="N/A"):
    try:
        k = winreg.OpenKey(hive, path)
        return str(winreg.QueryValueEx(k, key)[0]).strip()
    except:
        return default

# ─────────────────────────────────────────────────────────────
#  WINDOWS LICENSE CHECK
# ─────────────────────────────────────────────────────────────
def get_win_info():
    info = {}
    nt_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    hklm    = winreg.HKEY_LOCAL_MACHINE

    info["product_name"]  = reg_get(hklm, nt_path, "ProductName")
    info["edition"]       = reg_get(hklm, nt_path, "EditionID")
    info["version"]       = reg_get(hklm, nt_path, "DisplayVersion") or \
                            reg_get(hklm, nt_path, "ReleaseId")
    info["build"]         = reg_get(hklm, nt_path, "CurrentBuildNumber")
    info["registered"]    = reg_get(hklm, nt_path, "RegisteredOwner")
    info["product_id"]    = reg_get(hklm, nt_path, "ProductId")
    info["arch"]          = platform.machine()
    info["hostname"]      = socket.gethostname()

    # Nhận diện chính xác Windows 11 (Build >= 22000 trong khi Registry ProductName vẫn giữ nhãn Windows 10)
    try:
        b_num = int(info.get("build", "0"))
        if b_num >= 22000 and "Windows 10" in info.get("product_name", ""):
            info["product_name"] = info["product_name"].replace("Windows 10", "Windows 11")
    except:
        pass

    try:
        ts = int(reg_get(hklm, nt_path, "InstallDate", "0"))
        info["install_date"] = datetime.datetime.fromtimestamp(ts).strftime("%d/%m/%Y")
    except:
        info["install_date"] = "N/A"

    # ── Activation via slmgr ──────────────────────────────────
    info["activation_status"] = "Unknown"
    info["license_type"]      = "Unknown"
    info["kms_server"]        = ""
    info["activation_raw"]    = ""

    try:
        slmgr = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"),
                             "System32", "slmgr.vbs")
        res = subprocess.run(
            ["cscript", "//NoLogo", "//B", slmgr, "/dli"],
            capture_output=True, text=True, timeout=25,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        raw = res.stdout + res.stderr
        info["activation_raw"] = raw
        low = raw.lower()

        if "license status: licensed" in low:
            info["activation_status"] = "✅  LICENSED"
        elif "notification" in low:
            info["activation_status"] = "⚠️  NOTIFICATION MODE"
        elif "grace period" in low:
            info["activation_status"] = "⏳  IN GRACE PERIOD"
        elif "unlicensed" in low:
            info["activation_status"] = "❌  UNLICENSED"

        if "kms machine" in low or "kms host" in low or "key management service" in low:
            info["license_type"] = "🔴  KMS Activated (possibly cracked)"
        elif "oem" in low:
            info["license_type"] = "✅  OEM License (Pre-installed)"
        elif "retail" in low:
            info["license_type"] = "✅  Retail License"
        elif "volume" in low:
            info["license_type"] = "🟡  Volume License (Corporate)"

        for line in raw.splitlines():
            ll = line.lower()
            if "kms machine ip" in ll or "kms machine name" in ll:
                info["kms_server"] = line.strip()
                break
    except Exception as e:
        info["activation_raw"] = str(e)

    # ── Fallback via WMI SoftwareLicensingProduct (cực kỳ chính xác trên Win 11) ──
    if info["activation_status"] == "Unknown" and WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            for p in c.SoftwareLicensingProduct():
                if p.PartialProductKey and ("windows" in (p.Name or "").lower() or "operating system" in (p.Description or "").lower()):
                    st = getattr(p, "LicenseStatus", 0)
                    desc = (p.Description or "").lower()
                    name = (p.Name or "").lower()

                    if st == 1:
                        info["activation_status"] = "✅  LICENSED"
                    elif st == 2:
                        info["activation_status"] = "⏳  IN GRACE PERIOD"
                    elif st == 5:
                        info["activation_status"] = "⚠️  NOTIFICATION MODE"
                    else:
                        info["activation_status"] = "❌  UNLICENSED"

                    if "kms" in desc or "kms" in name:
                        info["license_type"] = "🔴  KMS Activated (possibly cracked)"
                    elif "oem" in desc or "oem" in name:
                        info["license_type"] = "✅  OEM License (Pre-installed)"
                    elif "retail" in desc or "retail" in name:
                        info["license_type"] = "✅  Retail License"
                    elif "volume" in desc:
                        info["license_type"] = "🟡  Volume License (Corporate)"
                    break
        except:
            pass

    if info["activation_status"] == "Unknown":
        info["activation_status"] = "❓  Unknown"
    if info["license_type"] == "Unknown":
        info["license_type"] = "❓  Unknown"

    # ── Windows Defender status ───────────────────────────────
    info["defender"] = "Unknown"
    try:
        r2 = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command",
             "(Get-MpComputerStatus).RealTimeProtectionEnabled"],
            capture_output=True, text=True, timeout=12,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        v = r2.stdout.strip().lower()
        info["defender"] = "✅  Đang bật" if v == "true" else "❌  Đang tắt (cẩn thận!)"
    except:
        pass

    return info

# ─────────────────────────────────────────────────────────────
#  SOFTWARE
# ─────────────────────────────────────────────────────────────
def get_installed_software():
    seen, result = set(), []
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for path in (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                     r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"):
            try:
                root = winreg.OpenKey(hive, path)
                for i in range(winreg.QueryInfoKey(root)[0]):
                    try:
                        sub = winreg.OpenKey(root, winreg.EnumKey(root, i))
                        def qv(k):
                            try: return winreg.QueryValueEx(sub, k)[0].strip()
                            except: return ""
                        name = qv("DisplayName")
                        if not name or name in seen:
                            continue
                        seen.add(name)
                        result.append({
                            "name":      name,
                            "version":   qv("DisplayVersion"),
                            "publisher": qv("Publisher"),
                            "date":      qv("InstallDate"),
                            "location":  qv("InstallLocation"),
                        })
                    except:
                        pass
            except:
                pass
    return sorted(result, key=lambda x: x["name"].lower())

def scan_piracy(software_list):
    flagged = []
    for s in software_list:
        nl   = s["name"].lower()
        ll   = s["location"].lower()
        reasons = []

        for kw in CRACK_KEYWORDS:
            if kw in nl:
                reasons.append(f"Từ khóa crack đã biết: '{kw}'")
                break

        if any(p in ll for p in SUSPICIOUS_PATHS):
            reasons.append(f"Cài từ đường dẫn đáng ngờ")

        if not s["publisher"] and any(
            w in nl for w in ["crack","patch","keygen","loader","activat","serial"]
        ):
            reasons.append("Không có Publisher + tên đáng ngờ")

        if reasons:
            flagged.append({**s, "reasons": reasons})

    crack_procs = []
    for p in psutil.process_iter(["name"]):
        try:
            if (p.info["name"] or "").lower() in CRACK_PROCESSES:
                crack_procs.append(p.info["name"])
        except:
            pass

    return flagged, crack_procs

# ─────────────────────────────────────────────────────────────
#  HARDWARE
# ─────────────────────────────────────────────────────────────
def get_hardware():
    vm = psutil.virtual_memory()
    cf = psutil.cpu_freq()
    return {
        "cpu":      wmi_get("Win32_Processor", "Name"),
        "cores":    psutil.cpu_count(logical=False),
        "logi":     psutil.cpu_count(logical=True),
        "freq":     f"{cf.current:.0f} MHz" if cf else "N/A",
        "ram":      bytes2h(vm.total),
        "ram_free": bytes2h(vm.available),
        "gpu":      wmi_get("Win32_VideoController", "Caption"),
        "mobo":     f"{wmi_get('Win32_BaseBoard','Manufacturer')} {wmi_get('Win32_BaseBoard','Product')}",
        "bios":     wmi_get("Win32_BIOS", "SMBIOSBIOSVersion"),
        "uptime":   get_uptime(),
        "disks":    _disks(),
    }

def _disks():
    out = []
    for p in psutil.disk_partitions():
        try:
            u = psutil.disk_usage(p.mountpoint)
            out.append({"dev": p.device, "mount": p.mountpoint, "fs": p.fstype,
                        "total": u.total, "used": u.used,
                        "free":  u.free,  "pct":  u.percent})
        except:
            pass
    return out

# ─────────────────────────────────────────────────────────────
#  UI UTILITIES
# ─────────────────────────────────────────────────────────────
def scrollable(parent):
    canvas = tk.Canvas(parent, bg=C["bg"], highlightthickness=0)
    vsb    = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner = tk.Frame(canvas, bg=C["bg"])
    wid   = canvas.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>",
                lambda e: canvas.itemconfig(wid, width=e.width))
    canvas.bind_all("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))
    return inner

def sec_hdr(parent, text, icon=""):
    f = tk.Frame(parent, bg=C["bg"])
    f.pack(fill="x", padx=16, pady=(14, 3))
    tk.Label(f, text=f"{icon}  {text}" if icon else text,
             font=FONTS["header"], bg=C["bg"], fg=C["text"]).pack(side="left")
    tk.Frame(f, bg=C["accent"], height=2).pack(
        side="left", fill="x", expand=True, padx=8, pady=(6, 0))

def irow(parent, label, value, vc=None, bg=C["surface"]):
    f = tk.Frame(parent, bg=bg, pady=3)
    f.pack(fill="x")
    tk.Label(f, text=f"  {label}", font=FONTS["label"],
             bg=bg, fg=C["text2"], width=22, anchor="w").pack(side="left")
    tk.Label(f, text=value or "—", font=FONTS["body"],
             bg=bg, fg=vc or C["text"], anchor="w",
             wraplength=580).pack(side="left", padx=8)

def card(parent, bg=C["surface"], padx=14, pady=8):
    f = tk.Frame(parent, bg=bg, padx=padx, pady=pady)
    f.pack(fill="x", padx=16, pady=4)
    return f

def topbar(parent, title, app, accent=C["accent"]):
    top = tk.Frame(parent, bg=C["surface"], pady=10)
    top.pack(fill="x")
    tk.Button(top, text="  ← Trang chủ  ", font=FONTS["label"],
              bg=C["surface2"], fg=C["text2"], relief="flat", cursor="hand2",
              command=lambda: app.show("home")).pack(side="left", padx=10)
    tk.Label(top, text=title, font=FONTS["title"],
             bg=C["surface"], fg=C["text"]).pack(side="left", padx=8)
    return top

# ─────────────────────────────────────────────────────────────
#  HOME PANEL
# ─────────────────────────────────────────────────────────────
class HomePanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        # ── Hero ─────────────────────────────────────────────
        hero = tk.Frame(self, bg=C["surface"], pady=24)
        hero.pack(fill="x")
        tk.Label(hero, text="🖥️  PC Status & License Checker",
                 font=FONTS["hero"], bg=C["surface"], fg=C["text"]).pack()
        tk.Label(hero,
                 text="Kiểm tra bản quyền Windows  ·  Phát hiện phần mềm lậu  ·  Thông số hệ thống",
                 font=FONTS["body"], bg=C["surface"], fg=C["text2"]).pack(pady=(4, 0))

        # ── Quick info strip ─────────────────────────────────
        strip = tk.Frame(self, bg=C["surface2"], pady=6)
        strip.pack(fill="x")
        for icon, val in [
            ("🖥", socket.gethostname()),
            ("🪟", platform.release() + " " + platform.version()[:20]),
            ("🕐", datetime.datetime.now().strftime("%d/%m/%Y  %H:%M")),
        ]:
            tk.Label(strip, text=f"  {icon}  {val}  ",
                     font=FONTS["small"], bg=C["surface2"],
                     fg=C["text2"]).pack(side="left")

        # ── Feature cards ────────────────────────────────────
        tk.Label(self, text="Chọn chức năng cần kiểm tra",
                 font=FONTS["label"], bg=C["bg"],
                 fg=C["text3"], pady=10).pack()

        grid = tk.Frame(self, bg=C["bg"])
        grid.pack(padx=20, pady=4, fill="x")

        CARDS = [
            ("🪟", "Bản quyền\nWindows",
             "Trạng thái activation\nKMS detection · Product ID",
             "#0d1a3a", C["blue"], "win"),
            ("🔍", "Phát hiện\nPhần mềm Lậu",
             "Quét crack · Activator\nKeygen · Process lạ",
             "#1a0d0d", C["red"], "piracy"),
            ("🧩", "Phần mềm\nĐã cài đặt",
             "Danh sách đầy đủ · Search\nSort · Publisher",
             C["surface2"], C["cyan"], "software"),
            ("📊", "Thông số\nHệ thống",
             "CPU · RAM · GPU · Disk\nNetwork · Uptime",
             "#0d1a2a", C["accent_h"], "system"),
            ("⚙️", "Processes\nĐang chạy",
             "Top 200 process\nPhát hiện process lạ",
             C["surface2"], C["text2"], "process"),
            ("📋", "Xuất\nBáo cáo",
             "Export .txt đầy đủ\nAudit · Chia sẻ",
             "#1a0d1a", C["yellow"], "report"),
        ]

        for i, (icon, title, desc, bg, color, pid) in enumerate(CARDS):
            c = tk.Frame(grid, bg=bg, padx=16, pady=14, cursor="hand2")
            c.grid(row=i//3, column=i%3, padx=8, pady=8, sticky="nsew")
            grid.columnconfigure(i % 3, weight=1)

            tk.Label(c, text=icon, font=FONTS["emoji"],
                     bg=bg, fg=color).pack(anchor="w")
            tk.Label(c, text=title, font=FONTS["title"],
                     bg=bg, fg=C["text"], justify="left").pack(anchor="w", pady=(4, 2))
            tk.Label(c, text=desc, font=FONTS["small"],
                     bg=bg, fg=C["text2"], justify="left").pack(anchor="w")
            tk.Frame(c, bg=color, height=3).pack(fill="x", pady=(10, 0))

            def _click(e, p=pid): self.app.show(p)
            c.bind("<Button-1>", _click)
            for w in c.winfo_children():
                w.bind("<Button-1>", _click)

        # ── Live stats ───────────────────────────────────────
        live = tk.Frame(self, bg=C["surface"], pady=8)
        live.pack(fill="x", side="bottom")
        self._cpu_v = tk.Label(live, font=FONTS["mono"],
                               bg=C["surface"], fg=C["cyan"], padx=16)
        self._cpu_v.pack(side="left")
        self._ram_v = tk.Label(live, font=FONTS["mono"],
                               bg=C["surface"], fg=C["green"], padx=8)
        self._ram_v.pack(side="left")
        self._upt_v = tk.Label(live, font=FONTS["mono"],
                               bg=C["surface"], fg=C["text2"], padx=8)
        self._upt_v.pack(side="left")
        self._tick()

    def _tick(self):
        try:
            self._cpu_v.config(text=f"⚡ CPU {psutil.cpu_percent():.0f}%")
            self._ram_v.config(text=f"💾 RAM {psutil.virtual_memory().percent:.0f}%")
            self._upt_v.config(text=f"⏱ {get_uptime()}")
        except:
            pass
        self.after(2000, self._tick)


# ─────────────────────────────────────────────────────────────
#  WINDOWS LICENSE PANEL
# ─────────────────────────────────────────────────────────────
class WinPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        top = topbar(self, "🪟  Kiểm tra Bản quyền Windows", self.app)
        tk.Button(top, text="🔄 Refresh", font=FONTS["label"],
                  bg=C["accent"], fg=C["white"], relief="flat",
                  cursor="hand2", padx=10,
                  command=self._load).pack(side="right", padx=10)

        self._body = scrollable(self)
        self._load()

    def _load(self):
        for w in self._body.winfo_children():
            w.destroy()
        tk.Label(self._body,
                 text="⏳ Đang kiểm tra bản quyền Windows…\n(slmgr có thể mất 15-25 giây)",
                 font=FONTS["body"], bg=C["bg"], fg=C["text2"]).pack(pady=50)
        threading.Thread(target=lambda: self.after(
            0, lambda d=get_win_info(): self._render(d)), daemon=True).start()

    def _render(self, d):
        for w in self._body.winfo_children():
            w.destroy()

        status   = d.get("activation_status", "Unknown")
        lic_type = d.get("license_type", "Unknown")
        is_ok    = "✅" in status
        is_kms   = "KMS" in lic_type and "🔴" in lic_type
        is_warn  = "⚠️" in status or "⏳" in status or "❓" in status

        # ── Status banner ─────────────────────────────────────
        ban_bg = C["green_bg"] if is_ok and not is_kms else \
                 C["red_bg"]   if is_kms else C["yellow_bg"]
        ban_fg = C["green"]   if is_ok and not is_kms else \
                 C["red"]     if is_kms else C["yellow"]

        ban = tk.Frame(self._body, bg=ban_bg, pady=22)
        ban.pack(fill="x", padx=16, pady=12)
        tk.Label(ban, text=status,
                 font=("Segoe UI", 17, "bold"), bg=ban_bg, fg=ban_fg).pack()
        tk.Label(ban, text=lic_type,
                 font=FONTS["body"], bg=ban_bg, fg=ban_fg).pack(pady=2)
        if is_kms:
            tk.Label(ban,
                     text="⚠️  Phát hiện KMS Activation — Windows có thể là bản lậu (KMSpico, KMSAuto, v.v.)",
                     font=FONTS["label"], bg=ban_bg, fg=C["red"]).pack(pady=4)

        # ── Windows details ───────────────────────────────────
        sec_hdr(self._body, "Thông tin Windows", "🪟")
        det = card(self._body)
        for lbl, key in [
            ("Tên OS",       "product_name"),
            ("Edition",      "edition"),
            ("Version",      "version"),
            ("Build",        "build"),
            ("Architecture", "arch"),
            ("Computer Name","hostname"),
            ("Đăng ký cho",  "registered"),
            ("Product ID",   "product_id"),
            ("Ngày cài",     "install_date"),
        ]:
            irow(det, lbl, d.get(key, "N/A"))

        # ── Security ──────────────────────────────────────────
        sec_hdr(self._body, "Bảo mật", "🛡️")
        sec = card(self._body)
        df  = d.get("defender", "Unknown")
        irow(sec, "Windows Defender",
             df, vc=C["green"] if "✅" in df else C["red"])
        ks  = d.get("kms_server") or "Không phát hiện"
        irow(sec, "KMS Server",
             ks, vc=C["red"] if d.get("kms_server") else C["green"])

        # ── Raw output ────────────────────────────────────────
        raw = d.get("activation_raw", "").strip()
        if raw:
            sec_hdr(self._body, "Chi tiết slmgr /dli", "📄")
            rb = tk.Frame(self._body, bg=C["surface2"], pady=8)
            rb.pack(fill="x", padx=16, pady=4)
            txt = tk.Text(rb, font=FONTS["mono"], bg=C["surface2"],
                          fg=C["text2"], relief="flat", height=9,
                          wrap="word", state="normal")
            txt.insert("1.0", raw)
            txt.config(state="disabled")
            txt.pack(fill="x", padx=10)

        # ── Kết luận ──────────────────────────────────────────
        sec_hdr(self._body, "Kết luận", "📋")
        vbg = C["green_bg"] if is_ok and not is_kms else \
              C["red_bg"]   if is_kms else C["yellow_bg"]
        vf  = card(self._body, bg=vbg)
        if is_ok and not is_kms:
            tk.Label(vf, text="✅  Windows có vẻ hợp lệ — bản quyền chính hãng.",
                     font=FONTS["label"], bg=vbg, fg=C["green"]).pack(anchor="w")
        elif is_kms:
            tk.Label(vf, text="🔴  KMS Activation — nghi ngờ dùng tool crack!",
                     font=FONTS["label"], bg=vbg, fg=C["red"]).pack(anchor="w")
            tk.Label(vf, text="    → Khuyến nghị: Mua Windows chính hãng tại Microsoft Store.",
                     font=FONTS["body"], bg=vbg, fg=C["text2"]).pack(anchor="w", pady=(2,0))
        else:
            tk.Label(vf, text="⚠️  Không xác định được. Hãy chạy tool với quyền Administrator.",
                     font=FONTS["label"], bg=vbg, fg=C["yellow"]).pack(anchor="w")


# ─────────────────────────────────────────────────────────────
#  PIRACY SCANNER PANEL
# ─────────────────────────────────────────────────────────────
class PiracyPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        top = topbar(self, "🔍  Phát hiện Phần mềm Lậu / Crack", self.app)
        tk.Button(top, text="🔄 Scan lại", font=FONTS["label"],
                  bg=C["red"], fg=C["white"], relief="flat",
                  cursor="hand2", padx=10,
                  command=self._load).pack(side="right", padx=10)
        self._body = scrollable(self)
        self._load()

    def _load(self):
        for w in self._body.winfo_children():
            w.destroy()
        tk.Label(self._body, text="🔍 Đang quét phần mềm đã cài đặt…",
                 font=FONTS["body"], bg=C["bg"], fg=C["text2"]).pack(pady=50)

        def _run():
            sw = get_installed_software()
            flagged, cprocs = scan_piracy(sw)
            self.after(0, lambda: self._render(sw, flagged, cprocs))

        threading.Thread(target=_run, daemon=True).start()

    def _render(self, all_sw, flagged, crack_procs):
        for w in self._body.winfo_children():
            w.destroy()

        total    = len(all_sw)
        nf       = len(flagged)
        np       = len(crack_procs)
        clean    = nf == 0 and np == 0

        # Banner
        bbg = C["green_bg"] if clean else C["red_bg"]
        bfg = C["green"]    if clean else C["red"]
        ban = tk.Frame(self._body, bg=bbg, pady=18)
        ban.pack(fill="x", padx=16, pady=12)
        ic  = "✅" if clean else "🔴"
        msg = "Không phát hiện phần mềm lậu rõ ràng!" if clean else \
              f"Phát hiện {nf} phần mềm đáng ngờ" + (f" · {np} process lạ" if np else "") + "!"
        tk.Label(ban, text=f"{ic}  {msg}",
                 font=("Segoe UI", 14, "bold"), bg=bbg, fg=bfg).pack()
        tk.Label(ban, text=f"Đã quét tổng cộng {total} phần mềm cài đặt",
                 font=FONTS["body"], bg=bbg, fg=C["text2"]).pack(pady=2)

        # Crack processes
        if crack_procs:
            sec_hdr(self._body, "🚨 Process crack đang chạy NGAY BÂY GIỜ!", "🔴")
            pf = card(self._body, bg=C["red_bg"])
            for proc in crack_procs:
                tk.Label(pf, text=f"  🔴  {proc}  ← Đang chạy!",
                         font=FONTS["label"], bg=C["red_bg"],
                         fg=C["red"]).pack(anchor="w", pady=2)

        # Flagged software
        if flagged:
            sec_hdr(self._body, f"Phần mềm nghi vấn ({nf})", "⚠️")
            for s in flagged:
                itm = tk.Frame(self._body, bg=C["red_bg"], pady=10)
                itm.pack(fill="x", padx=16, pady=3)
                tk.Label(itm, text=f"  🔴  {s['name']}",
                         font=FONTS["label"], bg=C["red_bg"],
                         fg=C["red"]).pack(anchor="w")
                if s["publisher"]:
                    tk.Label(itm, text=f"       Publisher: {s['publisher']}",
                             font=FONTS["small"], bg=C["red_bg"],
                             fg=C["text2"]).pack(anchor="w")
                for r in s["reasons"]:
                    tk.Label(itm, text=f"       ⚠️  {r}",
                             font=FONTS["small"], bg=C["red_bg"],
                             fg=C["yellow"]).pack(anchor="w")
        else:
            sec_hdr(self._body, "Kết quả quét", "✅")
            ok = card(self._body, bg=C["green_bg"])
            tk.Label(ok, text="✅  Không tìm thấy phần mềm lậu rõ ràng trong danh sách cài đặt.",
                     font=FONTS["body"], bg=C["green_bg"], fg=C["green"]).pack(anchor="w")

        # Disclaimer
        sec_hdr(self._body, "Lưu ý", "ℹ️")
        nt = card(self._body, bg=C["surface2"])
        tk.Label(nt,
                 text="• Công cụ này dựa trên chữ ký tên đã biết — không phải antivirus.\n"
                      "• Phần mềm crack tinh vi hơn có thể không bị phát hiện.\n"
                      "• Dùng Windows Defender / Malwarebytes để quét sâu hơn.\n"
                      "• KMS tổ chức (doanh nghiệp) có thể bị nhận nhầm — kiểm tra với IT.",
                 font=FONTS["small"], bg=C["surface2"], fg=C["text2"],
                 justify="left").pack(anchor="w", padx=4)


# ─────────────────────────────────────────────────────────────
#  SOFTWARE LIST PANEL
# ─────────────────────────────────────────────────────────────
class SoftwarePanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app    = app
        self._cache = []
        self._build()
        threading.Thread(target=self._fetch, daemon=True).start()

    def _build(self):
        topbar(self, "🧩  Phần mềm Đã cài đặt", self.app)

        # Search
        sb = tk.Frame(self, bg=C["surface2"], pady=7)
        sb.pack(fill="x")
        tk.Label(sb, text="  🔍 ", font=FONTS["body"],
                 bg=C["surface2"], fg=C["text2"]).pack(side="left")
        self._q = tk.StringVar()
        self._q.trace_add("write", lambda *_: self._filter())
        tk.Entry(sb, textvariable=self._q, font=FONTS["body"],
                 bg=C["surface"], fg=C["text"],
                 insertbackground=C["text"], relief="flat",
                 width=42, bd=0).pack(side="left", padx=4, ipady=4)
        self._cnt = tk.Label(sb, text="Đang tải…", font=FONTS["small"],
                              bg=C["surface2"], fg=C["text2"], padx=12)
        self._cnt.pack(side="left")

        # Tree
        style = ttk.Style()
        style.configure("SW.Treeview",
                        background=C["surface"], foreground=C["text"],
                        rowheight=26, fieldbackground=C["surface"],
                        font=FONTS["body"])
        style.configure("SW.Treeview.Heading",
                        background=C["surface2"], foreground=C["text2"],
                        font=FONTS["label"], relief="flat")
        style.map("SW.Treeview",
                  background=[("selected", C["accent"])],
                  foreground=[("selected", C["white"])])

        cols = ("name", "version", "publisher", "date")
        self._tv = ttk.Treeview(self, columns=cols, show="headings",
                                 style="SW.Treeview", height=30)
        for col, hdr, w in [
            ("name",      "Tên phần mềm", 380),
            ("version",   "Phiên bản",    130),
            ("publisher", "Nhà phát hành",230),
            ("date",      "Ngày cài",     110),
        ]:
            self._tv.heading(col, text=hdr,
                             command=lambda c=col: self._sort(c))
            self._tv.column(col, width=w, anchor="w")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tv.yview)
        self._tv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tv.pack(fill="both", expand=True, padx=8, pady=4)

    def _fetch(self):
        self._cache = get_installed_software()
        self.after(0, self._filter)

    def _filter(self):
        q = self._q.get().lower()
        self._tv.delete(*self._tv.get_children())
        rows = [s for s in self._cache
                if q in s["name"].lower() or q in s["publisher"].lower()]
        for s in rows:
            self._tv.insert("", "end", values=(
                s["name"], s["version"], s["publisher"], s["date"]))
        self._cnt.config(
            text=f"  {len(rows)}/{len(self._cache)} phần mềm" if q
            else f"  {len(self._cache)} phần mềm")

    def _sort(self, col):
        items = [(self._tv.set(k, col), k)
                 for k in self._tv.get_children("")]
        items.sort(key=lambda x: x[0].lower())
        for i, (_, k) in enumerate(items):
            self._tv.move(k, "", i)


# ─────────────────────────────────────────────────────────────
#  SYSTEM INFO PANEL
# ─────────────────────────────────────────────────────────────
class SystemPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        topbar(self, "📊  Thông số Hệ thống", self.app)
        self._body = scrollable(self)
        tk.Label(self._body, text="⏳ Đang thu thập thông số phần cứng…",
                 font=FONTS["body"], bg=C["bg"], fg=C["text2"]).pack(pady=50)
        threading.Thread(
            target=lambda: self.after(0, lambda h=get_hardware(): self._render(h)),
            daemon=True).start()

    def _render(self, hw):
        for w in self._body.winfo_children():
            w.destroy()

        # Live bar
        live = tk.Frame(self._body, bg=C["surface2"], pady=12)
        live.pack(fill="x", padx=16, pady=8)
        for lbl, val, clr in [
            ("🧠 CPU",   f"{psutil.cpu_percent():.0f}%",              C["blue"]),
            ("💾 RAM",   f"{psutil.virtual_memory().percent:.0f}%",   C["green"]),
            ("⏱ Uptime", get_uptime(),                                C["cyan"]),
            ("🖥",       socket.gethostname(),                        C["text2"]),
        ]:
            col = tk.Frame(live, bg=C["surface2"], padx=22)
            col.pack(side="left")
            tk.Label(col, text=lbl, font=FONTS["small"],
                     bg=C["surface2"], fg=C["text2"]).pack()
            tk.Label(col, text=val, font=FONTS["big"],
                     bg=C["surface2"], fg=clr).pack()

        def sec(title, icon, rows, bg=C["surface"]):
            sec_hdr(self._body, title, icon)
            f = card(self._body, bg=bg)
            for l, v in rows:
                irow(f, l, v, bg=bg)

        sec("Processor", "🧠", [
            ("CPU Name",      hw["cpu"]),
            ("Physical Cores",str(hw["cores"])),
            ("Logical Cores", str(hw["logi"])),
            ("Clock Speed",   hw["freq"]),
            ("Current Load",  f"{psutil.cpu_percent()}%"),
        ])

        vm = psutil.virtual_memory()
        sec("Memory (RAM)", "💾", [
            ("Total RAM",  hw["ram"]),
            ("Available",  hw["ram_free"]),
            ("Used",       bytes2h(vm.used)),
            ("Usage",      f"{vm.percent:.0f}%"),
        ])

        sec("Graphics (GPU)", "🎮", [("GPU", hw["gpu"])])

        sec("Mainboard & BIOS", "📟", [
            ("Mainboard", hw["mobo"]),
            ("BIOS",      hw["bios"]),
        ])

        # Disks
        sec_hdr(self._body, "Storage Drives", "💽")
        for d in hw["disks"]:
            df = tk.Frame(self._body, bg=C["surface"], pady=10)
            df.pack(fill="x", padx=16, pady=3)
            pct = d["pct"]
            clr = C["green"] if pct < 70 else C["yellow"] if pct < 90 else C["red"]
            hdr = tk.Frame(df, bg=C["surface"])
            hdr.pack(fill="x", padx=12)
            tk.Label(hdr, text=f"💽  {d['dev']}  [{d['mount']}]  {d['fs']}",
                     font=FONTS["label"], bg=C["surface"], fg=C["text"]).pack(side="left")
            tk.Label(hdr, text=f"  {pct:.0f}%",
                     font=FONTS["small"], bg=C["surface"], fg=clr).pack(side="left")

            # Progress bar via Canvas
            cv = tk.Canvas(df, bg="#1e293b", height=8,
                           highlightthickness=0)
            cv.pack(fill="x", padx=12, pady=5)

            def _draw(c=cv, p=pct, color=clr):
                def _d(e):
                    w2 = c.winfo_width()
                    c.delete("all")
                    c.create_rectangle(0, 0, max(4, int(w2 * p / 100)), 8,
                                       fill=color, outline="")
                c.bind("<Configure>", _d)
            _draw()

            tk.Label(df,
                     text=f"  Total: {bytes2h(d['total'])}   "
                          f"Used: {bytes2h(d['used'])}   "
                          f"Free: {bytes2h(d['free'])}",
                     font=FONTS["small"], bg=C["surface"],
                     fg=C["text2"]).pack(anchor="w")


# ─────────────────────────────────────────────────────────────
#  PROCESS PANEL
# ─────────────────────────────────────────────────────────────
class ProcessPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()
        self._load()

    def _build(self):
        top = topbar(self, "⚙️  Processes Đang chạy", self.app)
        tk.Button(top, text="🔄 Refresh", font=FONTS["label"],
                  bg=C["surface2"], fg=C["text"], relief="flat",
                  cursor="hand2", padx=10,
                  command=self._load).pack(side="right", padx=10)

        self._cnt = tk.Label(self, text="", font=FONTS["small"],
                             bg=C["bg"], fg=C["text2"])
        self._cnt.pack(anchor="w", padx=16, pady=4)

        style = ttk.Style()
        style.configure("Proc.Treeview",
                        background=C["surface"], foreground=C["text"],
                        rowheight=24, fieldbackground=C["surface"],
                        font=FONTS["mono"])
        style.configure("Proc.Treeview.Heading",
                        background=C["surface2"], foreground=C["text2"],
                        font=FONTS["label"], relief="flat")
        style.map("Proc.Treeview",
                  background=[("selected", C["accent"])],
                  foreground=[("selected", C["white"])])

        cols = ("pid", "name", "cpu", "mem", "status", "flag")
        self._tv = ttk.Treeview(self, columns=cols, show="headings",
                                 style="Proc.Treeview", height=30)
        for col, hdr, w in [
            ("pid",    "PID",      70),
            ("name",   "Process", 300),
            ("cpu",    "CPU %",    80),
            ("mem",    "RAM",     100),
            ("status", "Status",   90),
            ("flag",   "⚠️",       50),
        ]:
            self._tv.heading(col, text=hdr)
            self._tv.column(col, width=w, anchor="w")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tv.yview)
        self._tv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tv.pack(fill="both", expand=True, padx=8, pady=4)

    def _load(self):
        self._tv.delete(*self._tv.get_children())
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent",
                                       "memory_info", "status"]):
            try:
                procs.append(p.info)
            except:
                pass
        procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)
        for p in procs[:250]:
            mem  = bytes2h(p["memory_info"].rss) if p.get("memory_info") else "—"
            name = (p.get("name") or "").lower()
            flag = "🔴" if name in CRACK_PROCESSES else ""
            self._tv.insert("", "end", values=(
                p["pid"], p.get("name", "?"),
                f"{p.get('cpu_percent', 0):.1f}",
                mem, p.get("status", "?"), flag))
        self._cnt.config(text=f"  {len(procs)} processes đang chạy")


# ─────────────────────────────────────────────────────────────
#  REPORT PANEL
# ─────────────────────────────────────────────────────────────
class ReportPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        topbar(self, "📋  Xuất Báo cáo", self.app)
        body = scrollable(self)

        sec_hdr(body, "Tùy chọn xuất", "💾")
        for label, color, cmd in [
            ("📄  Báo cáo đầy đủ  (Windows + Hardware + Phần mềm lậu + Tất cả apps)",
             C["accent"], self._full),
            ("🔍  Kết quả quét phần mềm lậu",
             C["red"],    self._piracy),
            ("📊  Thông số phần cứng",
             C["blue"],   self._hw),
        ]:
            f = tk.Frame(body, bg=C["surface"], pady=14, padx=16)
            f.pack(fill="x", padx=16, pady=5)
            tk.Label(f, text=label, font=FONTS["header"],
                     bg=C["surface"], fg=C["text"]).pack(side="left")
            tk.Button(f, text="Xuất ngay", font=FONTS["label"],
                      bg=color, fg=C["white"], relief="flat",
                      padx=12, pady=4, cursor="hand2",
                      command=cmd).pack(side="right")

        sec_hdr(body, "Chia sẻ kết quả", "📤")
        sf = card(body)
        tk.Label(sf,
                 text="Sau khi xuất file .txt, bạn có thể:\n"
                      "  • Gửi qua Zalo / Telegram / Email\n"
                      "  • Chụp màn hình kết quả trong tool\n"
                      "  • Upload Google Drive / OneDrive để lưu lại",
                 font=FONTS["body"], bg=C["surface"], fg=C["text2"],
                 justify="left").pack(anchor="w")

    def _savepath(self, name):
        return filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"{name}_{socket.gethostname()}_{datetime.date.today()}",
            filetypes=[("Text file", "*.txt")])

    def _full(self):
        path = self._savepath("PC_Report")
        if not path:
            return
        try:
            wi = get_win_info()
            hw = get_hardware()
            sw = get_installed_software()
            flagged, cprocs = scan_piracy(sw)
            lines = [
                "=" * 60,
                "  BÁO CÁO PC CHECKER",
                f"  Ngày   : {datetime.datetime.now():%d/%m/%Y %H:%M:%S}",
                f"  Máy    : {socket.gethostname()}",
                "=" * 60, "",
                "--- WINDOWS ---",
                f"  OS          : {wi.get('product_name')}",
                f"  Version     : {wi.get('version')}",
                f"  Build       : {wi.get('build')}",
                f"  Activation  : {wi.get('activation_status')}",
                f"  License     : {wi.get('license_type')}",
                f"  Product ID  : {wi.get('product_id')}",
                f"  Defender    : {wi.get('defender')}",
                f"  KMS Server  : {wi.get('kms_server') or 'None'}",
                "",
                "--- HARDWARE ---",
                f"  CPU  : {hw['cpu']}",
                f"  RAM  : {hw['ram']}",
                f"  GPU  : {hw['gpu']}",
                f"  Mobo : {hw['mobo']}",
                f"  BIOS : {hw['bios']}",
                "",
                "--- DISKS ---",
            ]
            for d in hw["disks"]:
                lines.append(f"  {d['dev']} [{d['mount']}] "
                             f"Total:{bytes2h(d['total'])} "
                             f"Used:{bytes2h(d['used'])} ({d['pct']:.0f}%)")
            lines += ["", f"--- PHẦN MỀM NGHI VẤN ({len(flagged)}) ---"]
            for s in flagged:
                lines.append(f"  ⚠ {s['name']}  |  {s['publisher']}")
                for r in s["reasons"]:
                    lines.append(f"      → {r}")
            lines += ["", f"--- TẤT CẢ PHẦN MỀM ({len(sw)}) ---"]
            for s in sw:
                lines.append(f"  {s['name'][:50]:50s} | {s['version'][:20]:20s} | {s['publisher']}")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("✅ Thành công", f"Đã lưu:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _piracy(self):
        path = self._savepath("Piracy_Scan")
        if not path:
            return
        try:
            sw = get_installed_software()
            flagged, cprocs = scan_piracy(sw)
            lines = [
                f"PIRACY SCAN — {datetime.datetime.now():%d/%m/%Y %H:%M}",
                f"Máy: {socket.gethostname()}",
                f"Tổng apps: {len(sw)}  |  Nghi vấn: {len(flagged)}  |  Crack process: {len(cprocs)}",
                "",
            ]
            for s in flagged:
                lines.append(f"❌  {s['name']}")
                for r in s["reasons"]:
                    lines.append(f"    → {r}")
            if cprocs:
                lines.append("\nCRACK PROCESSES DETECTED:")
                for p in cprocs:
                    lines.append(f"  🔴 {p}")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("✅ Thành công", f"Đã lưu:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _hw(self):
        path = self._savepath("System_Info")
        if not path:
            return
        try:
            hw = get_hardware()
            vm = psutil.virtual_memory()
            lines = [
                f"SYSTEM INFO — {datetime.datetime.now():%d/%m/%Y %H:%M}",
                f"Hostname : {socket.gethostname()}",
                f"CPU      : {hw['cpu']}",
                f"Cores    : {hw['cores']}P / {hw['logi']}L",
                f"RAM      : {hw['ram']} total / {bytes2h(vm.available)} free",
                f"GPU      : {hw['gpu']}",
                f"Mobo     : {hw['mobo']}",
                f"BIOS     : {hw['bios']}",
                f"Uptime   : {hw['uptime']}",
                "",
            ]
            for d in hw["disks"]:
                lines.append(f"Disk {d['dev']}: {bytes2h(d['total'])} "
                             f"({d['pct']:.0f}% used)")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("✅ Thành công", f"Đã lưu:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


# ─────────────────────────────────────────────────────────────
#  APP SHELL (Router)
# ─────────────────────────────────────────────────────────────
PANEL_MAP = {
    "home":     HomePanel,
    "win":      WinPanel,
    "piracy":   PiracyPanel,
    "software": SoftwarePanel,
    "system":   SystemPanel,
    "process":  ProcessPanel,
    "report":   ReportPanel,
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🖥️  PC Status & License Checker")
        self.geometry("1080x720")
        self.minsize(860, 580)
        self.configure(bg=C["bg"])
        self.resizable(True, True)

        try:
            admin_txt = "  [Admin ✓]" if ctypes.windll.shell32.IsUserAnAdmin() \
                        else "  [chạy với Admin để đầy đủ thông tin]"
            self.title(f"🖥️  PC Status & License Checker  {admin_txt}")
        except:
            pass

        self._cache  = {}
        self._active = None

        # Status bar
        sb = tk.Frame(self, bg=C["surface2"], pady=3)
        sb.pack(fill="x", side="bottom")
        self._st = tk.Label(sb, text="", font=FONTS["small"],
                            bg=C["surface2"], fg=C["text2"], padx=12)
        self._st.pack(side="left")
        self._cl = tk.Label(sb, text="", font=FONTS["small"],
                            bg=C["surface2"], fg=C["text3"], padx=12)
        self._cl.pack(side="right")
        self._clock()

        self.show("home")

    def show(self, panel_id):
        if self._active:
            self._active.pack_forget()
        if panel_id not in self._cache:
            self._cache[panel_id] = PANEL_MAP[panel_id](self, self)
        p = self._cache[panel_id]
        p.pack(fill="both", expand=True)
        self._active = p
        self._st.config(text=f"  📍 {panel_id.upper()}")

    def _clock(self):
        self._cl.config(
            text=f"  {datetime.datetime.now():%A, %d/%m/%Y  %H:%M:%S}  ")
        self.after(1000, self._clock)

    def on_close(self):
        self.destroy()


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
