"""
╔══════════════════════════════════════════════════════════╗
║        PC & LAPTOP STATUS CHECKER PRO                    ║
║        All-in-one Hardware, License & Audit Suite        ║
║        Windows License · Battery · SMART · Dead Pixel    ║
║        Keyboard Tester · Audio & Camera · Crack Scan     ║
╚══════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading, platform, psutil, datetime, subprocess
import socket, os, sys, json, winreg, ctypes, time, re
import math, struct, io, winsound

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

# ─────────────────────────────────────────────────────────────
#  COLOR PALETTE & STYLES
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
    "purple":    "#a855f7",
    "orange":    "#fb923c",
    "pink":      "#f472b6",
    "text":      "#e6edf3",
    "text2":     "#8b949e",
    "text3":     "#484f58",
    "white":     "#ffffff",
    "key_bg":    "#21262d",
    "key_hit":   "#e3b341",
    "key_done":  "#23d18b",
}

FONTS = {
    "hero":   ("Segoe UI", 22, "bold"),
    "title":  ("Segoe UI", 14, "bold"),
    "header": ("Segoe UI", 11, "bold"),
    "label":  ("Segoe UI", 10, "bold"),
    "body":   ("Segoe UI", 10),
    "small":  ("Segoe UI", 8),
    "mono":   ("Consolas", 9),
    "mono_b": ("Consolas", 10, "bold"),
    "big":    ("Segoe UI", 18, "bold"),
    "emoji":  ("Segoe UI Emoji", 24),
}

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

def bytes2h(b):
    if not isinstance(b, (int, float)):
        return str(b)
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
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except:
            pass
        c = wmi.WMI()
        items = getattr(c, cls)()
        if items and len(items) > idx:
            val = getattr(items[idx], attr)
            return str(val).strip() if val else default
        return default
    except:
        return default

def reg_get(hive, path, key, default="N/A"):
    try:
        k = winreg.OpenKey(hive, path)
        return str(winreg.QueryValueEx(k, key)[0]).strip()
    except:
        return default

# ─────────────────────────────────────────────────────────────
#  DATA FETCHERS
# ─────────────────────────────────────────────────────────────
def get_win_info():
    info = {}
    nt_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    hklm    = winreg.HKEY_LOCAL_MACHINE

    info["product_name"]  = reg_get(hklm, nt_path, "ProductName")
    info["edition"]       = reg_get(hklm, nt_path, "EditionID")
    info["version"]       = reg_get(hklm, nt_path, "DisplayVersion") or reg_get(hklm, nt_path, "ReleaseId")
    info["build"]         = reg_get(hklm, nt_path, "CurrentBuildNumber")
    info["registered"]    = reg_get(hklm, nt_path, "RegisteredOwner")
    info["product_id"]    = reg_get(hklm, nt_path, "ProductId")
    info["arch"]          = platform.machine()
    info["hostname"]      = socket.gethostname()

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

    info["activation_status"] = "Unknown"
    info["license_type"]      = "Unknown"
    info["kms_server"]        = ""
    info["activation_raw"]    = ""

    try:
        slmgr = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "slmgr.vbs")
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

    info["defender"] = "Unknown"
    try:
        r2 = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command",
             "(Get-MpComputerStatus).RealTimeProtectionEnabled"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        v = r2.stdout.strip().lower()
        info["defender"] = "✅  Đang bật" if v == "true" else "❌  Đang tắt (cẩn thận!)"
    except:
        pass

    return info

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

# ── NEW: BATTERY CHECKER ─────────────────────────────────────
def get_battery_info():
    info = {
        "has_battery": False,
        "percent": 0,
        "plugged": False,
        "time_left": "N/A",
        "design_cap": 0,
        "full_cap": 0,
        "cycle_count": "N/A",
        "wear_level": 0.0,
        "health_pct": 100.0,
        "voltage": 0.0,
        "device_name": "N/A",
        "manufacturer": "N/A",
        "chemistry": "Li-Ion",
        "status_text": "N/A",
        "report_path": "",
    }

    sb = psutil.sensors_battery()
    if sb is not None:
        info["has_battery"] = True
        info["percent"] = int(sb.percent)
        info["plugged"] = sb.power_plugged
        if sb.power_plugged:
            info["time_left"] = "⚡ Đang cắm nguồn AC (Đầy hoặc đang sạc)"
        elif sb.secsleft > 0:
            m = sb.secsleft // 60
            info["time_left"] = f"{m//60} giờ {m%60} phút còn lại"
        else:
            info["time_left"] = "Đang ước tính thời gian sử dụng..."

    if WMI_AVAILABLE:
        try:
            import pythoncom
            pythoncom.CoInitialize()
            w = wmi.WMI(namespace="root/wmi")
            for b in w.BatteryStaticData():
                info["has_battery"] = True
                dc = getattr(b, "DesignedCapacity", 0)
                if dc: info["design_cap"] = int(dc)
                dn = getattr(b, "DeviceName", "")
                if dn: info["device_name"] = str(dn).strip()
                mn = getattr(b, "ManufactureName", "")
                if mn: info["manufacturer"] = str(mn).strip()

            for b in w.BatteryFullChargedCapacity():
                fc = getattr(b, "FullChargedCapacity", 0)
                if fc: info["full_cap"] = int(fc)

            for b in w.BatteryStatus():
                v = getattr(b, "Voltage", 0)
                if v: info["voltage"] = round(v / 1000.0, 2)
        except:
            pass

    temp_report = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "pc_checker_battery.html")
    try:
        subprocess.run(
            ["powercfg", "/batteryreport", "/output", temp_report],
            capture_output=True, timeout=8,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if os.path.exists(temp_report):
            info["report_path"] = temp_report
            with open(temp_report, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()

            m_design = re.search(r"DESIGN CAPACITY.*?<td[^>]*>([\d,]+)\s*mWh", html, re.S | re.I)
            m_full   = re.search(r"FULL CHARGE CAPACITY.*?<td[^>]*>([\d,]+)\s*mWh", html, re.S | re.I)
            m_cycle  = re.search(r"CYCLE COUNT.*?<td[^>]*>([\d,]+|\-)", html, re.S | re.I)

            if m_design:
                val = int(m_design.group(1).replace(",", "").strip())
                if val > 0:
                    info["design_cap"] = val
                    info["has_battery"] = True
            if m_full:
                val = int(m_full.group(1).replace(",", "").strip())
                if val > 0:
                    info["full_cap"] = val
            if m_cycle:
                c_str = m_cycle.group(1).replace(",", "").strip()
                if c_str and c_str != "-":
                    info["cycle_count"] = c_str
    except:
        pass

    if info["design_cap"] > 0 and info["full_cap"] > 0:
        health = (info["full_cap"] / info["design_cap"]) * 100.0
        info["health_pct"] = round(min(health, 100.0), 1)
        info["wear_level"] = round(max(0.0, 100.0 - health), 1)
        if info["health_pct"] >= 85:
            info["status_text"] = "🟢 Pin Rất Tốt (Độ chai thấp, còn nguyên dung lượng cao)"
        elif info["health_pct"] >= 70:
            info["status_text"] = "🟡 Pin Trung Bình (Đã chai theo thời gian sử dụng)"
        else:
            info["status_text"] = "🔴 Pin Chai Nhiều (Khuyên dùng: Nên bảo dưỡng hoặc thay thế)"
    elif info["has_battery"]:
        info["status_text"] = "ℹ️ Đang hoạt động trên pin"
    else:
        info["status_text"] = "🖥️ Máy tính để bàn (Desktop PC) - Không có Pin"

    return info

# ── NEW: DISK S.M.A.R.T HEALTH ───────────────────────────────
def get_disk_health_info():
    disks = []
    try:
        ps_cmd = 'Get-PhysicalDisk | Select-Object FriendlyName, DeviceId, MediaType, BusType, HealthStatus, OperationalStatus, Size | ConvertTo-Json'
        p = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command",
             f"[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; {ps_cmd}"],
            capture_output=True, text=True, timeout=12,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if p.stdout.strip():
            data = json.loads(p.stdout.strip())
            if isinstance(data, dict):
                data = [data]
            for item in data:
                sz = item.get("Size") or 0
                disks.append({
                    "model":   str(item.get("FriendlyName") or "Ổ đĩa vật lý"),
                    "dev_id":  str(item.get("DeviceId") or ""),
                    "media":   str(item.get("MediaType") or "Unknown"),
                    "bus":     str(item.get("BusType") or "Unknown"),
                    "health":  str(item.get("HealthStatus") or "OK"),
                    "op":      str(item.get("OperationalStatus") or "OK"),
                    "size":    bytes2h(sz) if isinstance(sz, (int, float)) else str(sz),
                    "temp":    "N/A",
                    "hours":   "N/A",
                    "wear":    "N/A",
                })
    except:
        pass

    if not disks and WMI_AVAILABLE:
        try:
            c = wmi.WMI()
            for d in c.Win32_DiskDrive():
                sz = int(getattr(d, "Size", 0) or 0)
                disks.append({
                    "model":   getattr(d, "Model", "Ổ đĩa cứng"),
                    "dev_id":  str(getattr(d, "Index", "")),
                    "media":   "Ổ đĩa lưu trữ",
                    "bus":     getattr(d, "InterfaceType", "SCSI/SATA"),
                    "health":  getattr(d, "Status", "OK"),
                    "op":      "OK",
                    "size":    bytes2h(sz),
                    "temp":    "N/A",
                    "hours":   "N/A",
                    "wear":    "N/A",
                })
        except:
            pass

    try:
        ps_rel = 'Get-PhysicalDisk | Get-StorageReliabilityCounter | Select-Object DeviceId, Temperature, PowerOnHours, Wear | ConvertTo-Json'
        p2 = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command",
             f"[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; {ps_rel}"],
            capture_output=True, text=True, timeout=8,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if p2.stdout.strip():
            rdata = json.loads(p2.stdout.strip())
            if isinstance(rdata, dict):
                rdata = [rdata]
            rel_map = {str(r.get("DeviceId")): r for r in rdata if "DeviceId" in r}
            for d in disks:
                did = d.get("dev_id")
                if did in rel_map:
                    rc = rel_map[did]
                    t = rc.get("Temperature")
                    if t and t > 0: d["temp"] = f"{t} °C"
                    poh = rc.get("PowerOnHours")
                    if poh is not None: d["hours"] = f"{poh:,} giờ"
                    w = rc.get("Wear")
                    if w is not None: d["wear"] = f"{w}%"
    except:
        pass

    return disks

# ── NEW: DISPLAY & RESOLUTION INFO ───────────────────────────
def get_display_info():
    info = {
        "res": "N/A",
        "freq": "N/A",
        "depth": "N/A",
        "ratio": "N/A",
        "gpu": wmi_get("Win32_VideoController", "Caption"),
    }
    try:
        class DEVMODE(ctypes.Structure):
            _fields_ = [
                ('dmDeviceName', ctypes.c_wchar * 32),
                ('dmSpecVersion', ctypes.c_ushort),
                ('dmDriverVersion', ctypes.c_ushort),
                ('dmSize', ctypes.c_ushort),
                ('dmDriverExtra', ctypes.c_ushort),
                ('dmFields', ctypes.c_ulong),
                ('dmOrientation', ctypes.c_short),
                ('dmPaperSize', ctypes.c_short),
                ('dmPaperLength', ctypes.c_short),
                ('dmPaperWidth', ctypes.c_short),
                ('dmScale', ctypes.c_short),
                ('dmCopies', ctypes.c_short),
                ('dmDefaultSource', ctypes.c_short),
                ('dmPrintQuality', ctypes.c_short),
                ('dmColor', ctypes.c_short),
                ('dmDuplex', ctypes.c_short),
                ('dmYResolution', ctypes.c_short),
                ('dmTTOption', ctypes.c_short),
                ('dmCollate', ctypes.c_short),
                ('dmFormName', ctypes.c_wchar * 32),
                ('dmLogPixels', ctypes.c_ushort),
                ('dmBitsPerPel', ctypes.c_ulong),
                ('dmPelsWidth', ctypes.c_ulong),
                ('dmPelsHeight', ctypes.c_ulong),
                ('dmDisplayFlags', ctypes.c_ulong),
                ('dmDisplayFrequency', ctypes.c_ulong),
            ]
        dm = DEVMODE()
        dm.dmSize = ctypes.sizeof(DEVMODE)
        if ctypes.windll.user32.EnumDisplaySettingsW(None, -1, ctypes.byref(dm)):
            w = dm.dmPelsWidth
            h = dm.dmPelsHeight
            info["res"] = f"{w} × {h}"
            info["freq"] = f"{dm.dmDisplayFrequency} Hz"
            info["depth"] = f"{dm.dmBitsPerPel}-bit (True Color)"
            gcd = math.gcd(w, h)
            rw, rh = w // gcd, h // gcd
            if (rw, rh) in [(8, 5), (16, 10)]: info["ratio"] = "16:10"
            elif (rw, rh) in [(16, 9)]: info["ratio"] = "16:9"
            elif (rw, rh) in [(4, 3)]: info["ratio"] = "4:3"
            elif (rw, rh) in [(21, 9)]: info["ratio"] = "21:9"
            else: info["ratio"] = f"{rw}:{rh}"
    except:
        pass
    return info

# ── NEW: MULTIMEDIA DEVICES & STEREO AUDIO ───────────────────
def get_multimedia_info():
    info = {"audio_devices": [], "cameras": []}
    if WMI_AVAILABLE:
        try:
            import pythoncom
            pythoncom.CoInitialize()
            c = wmi.WMI()
            info["audio_devices"] = [getattr(d, "Name", "Thiết bị âm thanh") for d in c.Win32_SoundDevice()]
            info["cameras"] = [getattr(d, "Name", "Camera") for d in c.Win32_PnPEntity() if getattr(d, "PNPClass", "") in ("Camera", "Image")]
        except:
            pass
    return info

def play_channel_tone(channel="both", freq=500.0, duration_s=0.45):
    def _run():
        try:
            sample_rate = 44100
            n_samples = int(sample_rate * duration_s)
            raw = bytearray()
            for i in range(n_samples):
                t = i / sample_rate
                # Envelope để không bị tiếng tách (pop)
                env = min(1.0, min(i, n_samples - i) / (sample_rate * 0.03))
                val = int(32767 * 0.6 * env * math.sin(2 * math.pi * freq * t))
                l_val = val if channel in ("left", "both") else 0
                r_val = val if channel in ("right", "both") else 0
                raw.extend(struct.pack('<hh', l_val, r_val))

            buf = io.BytesIO()
            buf.write(b'RIFF')
            buf.write(struct.pack('<I', 36 + len(raw)))
            buf.write(b'WAVEfmt ')
            buf.write(struct.pack('<IHHIIHH', 16, 1, 2, sample_rate, sample_rate * 4, 4, 16))
            buf.write(b'data')
            buf.write(struct.pack('<I', len(raw)))
            buf.write(raw)
            winsound.PlaySound(buf.getvalue(), winsound.SND_MEMORY)
        except:
            pass
    threading.Thread(target=_run, daemon=True).start()

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
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))
    return inner

def sec_hdr(parent, text, icon=""):
    f = tk.Frame(parent, bg=C["bg"])
    f.pack(fill="x", padx=16, pady=(14, 4))
    tk.Label(f, text=f"{icon}  {text}" if icon else text,
             font=FONTS["header"], bg=C["bg"], fg=C["text"]).pack(side="left")
    tk.Frame(f, bg=C["accent"], height=2).pack(
        side="left", fill="x", expand=True, padx=8, pady=(6, 0))

def irow(parent, label, value, vc=None, bg=C["surface"]):
    f = tk.Frame(parent, bg=bg, pady=3)
    f.pack(fill="x")
    tk.Label(f, text=f"  {label}", font=FONTS["label"],
             bg=bg, fg=C["text2"], width=24, anchor="w").pack(side="left")
    tk.Label(f, text=value or "—", font=FONTS["body"],
             bg=bg, fg=vc or C["text"], anchor="w",
             wraplength=620).pack(side="left", padx=8)

def card(parent, bg=C["surface"], padx=14, pady=8):
    f = tk.Frame(parent, bg=bg, padx=padx, pady=pady)
    f.pack(fill="x", padx=16, pady=4)
    return f

def topbar(parent, title, app):
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
        hero = tk.Frame(self, bg=C["surface"], pady=16)
        hero.pack(fill="x")
        tk.Label(hero, text="💻  PC & LAPTOP STATUS CHECKER PRO",
                 font=FONTS["hero"], bg=C["surface"], fg=C["text"]).pack()
        tk.Label(hero,
                 text="Kiểm tra Bản quyền · Pin & Sạc Laptop · Ổ cứng S.M.A.R.T · Màn hình · Bàn phím & Loa",
                 font=FONTS["body"], bg=C["surface"], fg=C["text2"]).pack(pady=(4, 0))

        strip = tk.Frame(self, bg=C["surface2"], pady=5)
        strip.pack(fill="x")
        for icon, val in [
            ("🖥", socket.gethostname()),
            ("🪟", platform.release() + " " + platform.version()[:20]),
            ("🕐", datetime.datetime.now().strftime("%d/%m/%Y  %H:%M")),
        ]:
            tk.Label(strip, text=f"  {icon}  {val}  ",
                     font=FONTS["small"], bg=C["surface2"],
                     fg=C["text2"]).pack(side="left")

        # Scrollable container for cards
        body = scrollable(self)

        tk.Label(body, text="Chọn chức năng cần kiểm tra & test máy",
                 font=FONTS["label"], bg=C["bg"],
                 fg=C["text3"], pady=8).pack()

        grid = tk.Frame(body, bg=C["bg"])
        grid.pack(padx=16, pady=4, fill="x")

        CARDS = [
            # Hàng 1: Bản quyền & Hệ thống
            ("🪟", "Bản quyền\nWindows",
             "Trạng thái activation\nKMS detection · Product ID",
             "#0d1a3a", C["blue"], "win"),
            ("🔍", "Phát hiện\nPhần mềm Lậu",
             "Quét crack · Activator\nKeygen · Process lạ",
             "#1a0d0d", C["red"], "piracy"),
            ("📊", "Thông số\nHệ thống",
             "CPU · RAM · GPU · Disk\nMainboard · BIOS · Uptime",
             "#0d1a2a", C["accent_h"], "system"),
            # Hàng 2: Phần cứng Laptop & Sức khỏe
            ("🔋", "Pin & Sạc\nLaptop",
             "Độ chai pin (% Wear) · Dung lượng\nChu kỳ sạc · Battery Report HTML",
             "#0d2a18", C["green"], "battery"),
            ("💾", "Sức khỏe\nỔ cứng",
             "S.M.A.R.T NVMe / SSD / HDD\nNhiệt độ · Giờ chạy · Độ hao mòn",
             "#241d0d", C["yellow"], "disk_health"),
            ("🖥️", "Màn hình &\nĐiểm chết",
             "Dead Pixel Test Fullscreen\nĐộ phân giải · Tần số quét Hz",
             "#18122b", C["purple"], "display"),
            # Hàng 3: Kiểm tra thiết bị ngoại vi
            ("⌨️", "Bàn phím &\nChuột",
             "Test liệt phím · Kẹt nút trực quan\nTest chuột Trái/Phải/Con lăn",
             "#0d232a", C["cyan"], "keyboard"),
            ("🔊", "Loa, Mic &\nWebcam",
             "Test loa Trái/Phải độc lập\nTest Micro & Camera Windows",
             "#2a0d20", C["pink"], "multimedia"),
            ("🧩", "Phần mềm\nĐã cài đặt",
             "Danh sách đầy đủ · Search\nSort · Publisher · Ngày cài",
             C["surface2"], C["text"], "software"),
            # Hàng 4: Process & Báo cáo
            ("⚙️", "Processes\nĐang chạy",
             "Top tiến trình ngốn tài nguyên\nPhát hiện crack process",
             C["surface2"], C["text2"], "process"),
            ("📋", "Xuất\nBáo cáo",
             "Export .txt đầy đủ thông tin\nAudit mua bán máy · Chia sẻ Zalo",
             "#2a150d", C["orange"], "report"),
            ("🔄", "Làm mới\nDữ liệu",
             "Cập nhật lại toàn bộ cảm biến\nQuét lại thông số hệ thống",
             C["surface2"], C["green"], "refresh"),
        ]

        for i, (icon, title, desc, bg, color, pid) in enumerate(CARDS):
            c = tk.Frame(grid, bg=bg, padx=14, pady=12, cursor="hand2")
            c.grid(row=i//3, column=i%3, padx=6, pady=6, sticky="nsew")
            grid.columnconfigure(i % 3, weight=1)

            tk.Label(c, text=icon, font=FONTS["emoji"], bg=bg, fg=color).pack(anchor="w")
            tk.Label(c, text=title, font=FONTS["title"],
                     bg=bg, fg=C["text"], justify="left").pack(anchor="w", pady=(3, 2))
            tk.Label(c, text=desc, font=FONTS["small"],
                     bg=bg, fg=C["text2"], justify="left").pack(anchor="w")
            tk.Frame(c, bg=color, height=3).pack(fill="x", pady=(8, 0))

            def _click(e, p=pid):
                if p == "refresh":
                    self.app.clear_cache()
                    messagebox.showinfo("Thông báo", "Đã làm mới bộ nhớ cache!")
                else:
                    self.app.show(p)

            c.bind("<Button-1>", _click)
            for w in c.winfo_children():
                w.bind("<Button-1>", _click)

        # ── Live stats strip ─────────────────────────────────
        live = tk.Frame(self, bg=C["surface"], pady=6)
        live.pack(fill="x", side="bottom")
        self._cpu_v = tk.Label(live, font=FONTS["mono"], bg=C["surface"], fg=C["cyan"], padx=14)
        self._cpu_v.pack(side="left")
        self._ram_v = tk.Label(live, font=FONTS["mono"], bg=C["surface"], fg=C["green"], padx=8)
        self._ram_v.pack(side="left")
        self._bat_v = tk.Label(live, font=FONTS["mono"], bg=C["surface"], fg=C["yellow"], padx=8)
        self._bat_v.pack(side="left")
        self._upt_v = tk.Label(live, font=FONTS["mono"], bg=C["surface"], fg=C["text2"], padx=8)
        self._upt_v.pack(side="left")
        self._tick()

    def _tick(self):
        try:
            self._cpu_v.config(text=f"⚡ CPU {psutil.cpu_percent():.0f}%")
            self._ram_v.config(text=f"💾 RAM {psutil.virtual_memory().percent:.0f}%")
            sb = psutil.sensors_battery()
            if sb:
                plug = "🔌" if sb.power_plugged else "🔋"
                self._bat_v.config(text=f"{plug} Pin {sb.percent:.0f}%")
            else:
                self._bat_v.config(text="🖥️ PC")
            self._upt_v.config(text=f"⏱ {get_uptime()}")
        except:
            pass
        self.after(2000, self._tick)

# ─────────────────────────────────────────────────────────────
#  PANEL: BATTERY & CHARGER
# ─────────────────────────────────────────────────────────────
class BatteryPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        top = topbar(self, "🔋  Kiểm tra Pin & Sạc Laptop", self.app)
        tk.Button(top, text="🔄 Quét lại", font=FONTS["label"],
                  bg=C["accent"], fg=C["white"], relief="flat",
                  cursor="hand2", padx=10, command=self._load).pack(side="right", padx=10)
        self._body = scrollable(self)
        self._load()

    def _load(self):
        for w in self._body.winfo_children():
            w.destroy()
        tk.Label(self._body, text="⏳ Đang kiểm tra thông số Pin & sạc…",
                 font=FONTS["body"], bg=C["bg"], fg=C["text2"], pady=40).pack()
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        info = get_battery_info()
        self.after(0, lambda: self._render(info))

    def _render(self, info):
        for w in self._body.winfo_children():
            w.destroy()

        if not info["has_battery"]:
            c = card(self._body, bg="#1a140d", pady=24)
            tk.Label(c, text="🖥️", font=FONTS["hero"], bg="#1a140d", fg=C["yellow"]).pack()
            tk.Label(c, text="Không phát hiện Pin trên thiết bị này",
                     font=FONTS["title"], bg="#1a140d", fg=C["text"]).pack(pady=4)
            tk.Label(c, text="Đây là máy tính để bàn (Desktop PC) hoặc thiết bị đang không gắn pin.",
                     font=FONTS["body"], bg="#1a140d", fg=C["text2"]).pack()
            return

        # Overview banner
        h_color = C["green"] if info["health_pct"] >= 85 else (C["yellow"] if info["health_pct"] >= 70 else C["red"])
        h_bg    = C["green_bg"] if info["health_pct"] >= 85 else (C["yellow_bg"] if info["health_pct"] >= 70 else C["red_bg"])

        top_c = card(self._body, bg=h_bg, pady=16)
        tk.Label(top_c, text=f"Sức khỏe Pin: {info['health_pct']}%  ·  Chai Pin: {info['wear_level']}%",
                 font=FONTS["title"], bg=h_bg, fg=h_color).pack()
        tk.Label(top_c, text=info["status_text"],
                 font=FONTS["body"], bg=h_bg, fg=C["text"]).pack(pady=3)

        # Quick gauges
        sec_hdr(self._body, "Trạng thái sạc hiện tại", "⚡")
        c1 = card(self._body)
        irow(c1, "Mức pin hiện tại", f"{info['percent']}%", C["cyan"])
        irow(c1, "Trạng thái cắm sạc", "🔌 Đang cắm sạc AC" if info["plugged"] else "🔋 Đang dùng Pin",
             C["green"] if info["plugged"] else C["yellow"])
        irow(c1, "Thời gian sử dụng", info["time_left"])
        irow(c1, "Điện áp hoạt động", f"{info['voltage']} V" if info["voltage"] else "N/A")

        sec_hdr(self._body, "Chi tiết độ chai & Dung lượng (mWh)", "📊")
        c2 = card(self._body)
        irow(c2, "Dung lượng Thiết kế (Design)", f"{info['design_cap']:,} mWh" if info["design_cap"] else "N/A")
        irow(c2, "Dung lượng Sạc đầy (Full Charge)", f"{info['full_cap']:,} mWh" if info["full_cap"] else "N/A", h_color)
        irow(c2, "Hao hụt dung lượng (Mất đi)",
             f"{info['design_cap'] - info['full_cap']:,} mWh" if (info['design_cap'] and info['full_cap']) else "N/A",
             C["red"] if info["wear_level"] > 15 else C["text"])
        irow(c2, "Số chu kỳ sạc (Cycle Count)", f"{info['cycle_count']} lần", C["orange"])

        sec_hdr(self._body, "Thông tin phần cứng Pin", "🏷️")
        c3 = card(self._body)
        irow(c3, "Tên thiết bị (Model Pin)", info["device_name"])
        irow(c3, "Nhà sản xuất Pin", info["manufacturer"])
        irow(c3, "Loại hóa chất", info["chemistry"])

        # Battery report action
        sec_hdr(self._body, "Báo cáo chuyên sâu Windows", "📑")
        c4 = card(self._body)
        tk.Label(c4, text="Windows có sẵn công cụ xuất báo cáo pin chính thức (Battery Report HTML) gồm lịch sử sạc xả:",
                 font=FONTS["body"], bg=C["surface"], fg=C["text2"]).pack(anchor="w", pady=(0, 6))

        def _open_html():
            if info["report_path"] and os.path.exists(info["report_path"]):
                os.startfile(info["report_path"])
            else:
                messagebox.showwarning("Thông báo", "Chưa tạo được file báo cáo pin.")

        tk.Button(c4, text="🚀 Mở Báo cáo Pin Windows (HTML) trên Trình duyệt",
                  font=FONTS["label"], bg=C["accent"], fg=C["white"],
                  relief="flat", cursor="hand2", padx=14, pady=6,
                  command=_open_html).pack(anchor="w")

# ─────────────────────────────────────────────────────────────
#  PANEL: DISK S.M.A.R.T HEALTH
# ─────────────────────────────────────────────────────────────
class DiskHealthPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        top = topbar(self, "💾  Sức khỏe Ổ cứng & S.M.A.R.T", self.app)
        tk.Button(top, text="🔄 Quét lại", font=FONTS["label"],
                  bg=C["accent"], fg=C["white"], relief="flat",
                  cursor="hand2", padx=10, command=self._load).pack(side="right", padx=10)
        self._body = scrollable(self)
        self._load()

    def _load(self):
        for w in self._body.winfo_children():
            w.destroy()
        tk.Label(self._body, text="⏳ Đang truy xuất thông tin S.M.A.R.T ổ cứng…",
                 font=FONTS["body"], bg=C["bg"], fg=C["text2"], pady=40).pack()
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        disks = get_disk_health_info()
        parts = _disks()
        self.after(0, lambda: self._render(disks, parts))

    def _render(self, disks, parts):
        for w in self._body.winfo_children():
            w.destroy()

        if not disks:
            c = card(self._body, bg="#1a0d0d")
            tk.Label(c, text="Không thể đọc thông tin ổ đĩa vật lý.",
                     font=FONTS["body"], bg="#1a0d0d", fg=C["red"]).pack()
            return

        # Overall Status
        all_ok = all(d["health"].lower() in ("healthy", "ok") for d in disks)
        banner_bg = C["green_bg"] if all_ok else C["yellow_bg"]
        banner_fg = C["green"] if all_ok else C["yellow"]

        top_c = card(self._body, bg=banner_bg, pady=12)
        tk.Label(top_c, text=f"Tình trạng S.M.A.R.T: {'✅ TẤT CẢ Ổ ĐĨA KHỎE MẠNH' if all_ok else '⚠️ PHÁT HIỆN CẢNH BÁO'}",
                 font=FONTS["title"], bg=banner_bg, fg=banner_fg).pack()
        tk.Label(top_c, text=f"Đã kiểm tra {len(disks)} ổ đĩa vật lý gắn trên hệ thống",
                 font=FONTS["body"], bg=banner_bg, fg=C["text"]).pack(pady=2)

        sec_hdr(self._body, "Danh sách Ổ cứng Vật lý", "💽")
        for i, d in enumerate(disks):
            c = card(self._body, pady=10)
            is_healthy = d["health"].lower() in ("healthy", "ok")
            h_color = C["green"] if is_healthy else C["red"]

            hdr = tk.Frame(c, bg=C["surface"])
            hdr.pack(fill="x", pady=(0, 6))
            tk.Label(hdr, text=f"Ổ {i+1}: {d['model']}",
                     font=FONTS["header"], bg=C["surface"], fg=C["text"]).pack(side="left")
            tk.Label(hdr, text=f" {d['health']} ",
                     font=FONTS["label"], bg=C["green_bg"] if is_healthy else C["red_bg"],
                     fg=h_color).pack(side="right")

            irow(c, "Chuẩn giao tiếp / Bus", f"{d['bus']} ({d['media']})", C["cyan"])
            irow(c, "Dung lượng vật lý", d["size"])
            irow(c, "Trạng thái vận hành", d["op"])
            if d["temp"] != "N/A":
                irow(c, "Nhiệt độ ổ cứng", d["temp"], C["orange"])
            if d["hours"] != "N/A":
                irow(c, "Thời gian đã chạy (Power-On)", d["hours"], C["yellow"])
            if d["wear"] != "N/A":
                irow(c, "Mức độ hao mòn SSD (Wear)", d["wear"], C["pink"])

        sec_hdr(self._body, "Các Phân vùng logic đang dùng", "📂")
        for p in parts:
            c = card(self._body)
            pct = p["pct"]
            col = C["red"] if pct > 90 else (C["yellow"] if pct > 75 else C["cyan"])
            irow(c, f"Phân vùng [{p['mount']}]",
                 f"Đã dùng: {bytes2h(p['used'])} / {bytes2h(p['total'])} ({pct:.0f}%)  ·  Trống: {bytes2h(p['free'])}",
                 col)

# ─────────────────────────────────────────────────────────────
#  PANEL: KEYBOARD & MOUSE TESTER
# ─────────────────────────────────────────────────────────────
class KeyboardPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._tested_keys = set()
        self._key_widgets = {}
        self._mouse_clicks = {"L": 0, "M": 0, "R": 0, "W": 0}
        self._build()

    def _build(self):
        top = topbar(self, "⌨️  Kiểm tra Bàn phím & Chuột (Laptop / PC)", self.app)
        tk.Button(top, text="🔄 Reset Test", font=FONTS["label"],
                  bg=C["accent"], fg=C["white"], relief="flat",
                  cursor="hand2", padx=10, command=self._reset).pack(side="right", padx=10)

        # Control & Info Bar
        info_bar = tk.Frame(self, bg=C["surface2"], pady=8, padx=16)
        info_bar.pack(fill="x")

        self._lbl_count = tk.Label(info_bar, text="Đã test: 0 phím",
                                   font=FONTS["header"], bg=C["surface2"], fg=C["green"])
        self._lbl_count.pack(side="left")

        self._lbl_recent = tk.Label(info_bar, text="Nhấn phím bất kỳ trên bàn phím để kiểm tra",
                                    font=FONTS["body"], bg=C["surface2"], fg=C["text2"], padx=20)
        self._lbl_recent.pack(side="left")

        # Visual Keyboard Area
        kb_wrap = tk.Frame(self, bg=C["bg"], pady=12, padx=10)
        kb_wrap.pack(fill="both", expand=True)

        LAYOUT = [
            # Row 0
            [("Esc","esc",4), ("F1","f1",3), ("F2","f2",3), ("F3","f3",3), ("F4","f4",3),
             ("F5","f5",3), ("F6","f6",3), ("F7","f7",3), ("F8","f8",3),
             ("F9","f9",3), ("F10","f10",3), ("F11","f11",3), ("F12","f12",3),
             ("PrtSc","prtsc",4), ("Del","delete",4)],
            # Row 1
            [("~ `","`",3), ("1","1",3), ("2","2",3), ("3","3",3), ("4","4",3),
             ("5","5",3), ("6","6",3), ("7","7",3), ("8","8",3), ("9","9",3),
             ("0","0",3), ("-","-",3), ("=","=",3), ("Backspace","backspace",7)],
            # Row 2
            [("Tab","tab",5), ("Q","q",3), ("W","w",3), ("E","e",3), ("R","r",3),
             ("T","t",3), ("Y","y",3), ("U","u",3), ("I","i",3), ("O","o",3),
             ("P","p",3), ("[","[",3), ("]","]",3), ("\\","\\",5)],
            # Row 3
            [("Caps","caps",6), ("A","a",3), ("S","s",3), ("D","d",3), ("F","f",3),
             ("G","g",3), ("H","h",3), ("J","j",3), ("K","k",3), ("L","l",3),
             (";",";",3), ("'","'",3), ("Enter","enter",7)],
            # Row 4
            [("Shift","shift_l",8), ("Z","z",3), ("X","x",3), ("C","c",3), ("V","v",3),
             ("B","b",3), ("N","n",3), ("M","m",3), (",",",",3), (".",".",3),
             ("/","/",3), ("Shift","shift_r",6), ("▲","up",4)],
            # Row 5
            [("Ctrl","ctrl_l",5), ("Win","win",4), ("Alt","alt_l",4),
             ("Spacebar","space",20), ("Alt","alt_r",4), ("Fn/Ctrl","ctrl_r",4),
             ("◄","left",4), ("▼","down",4), ("►","right",4)],
        ]

        self._total_keys = 0
        for r_idx, row in enumerate(LAYOUT):
            rf = tk.Frame(kb_wrap, bg=C["bg"])
            rf.pack(fill="x", pady=2)
            for label, kid, width in row:
                self._total_keys += 1
                lbl = tk.Label(rf, text=label, width=width, height=2,
                               bg=C["key_bg"], fg=C["text"],
                               font=FONTS["small"], relief="groove", bd=1)
                lbl.pack(side="left", padx=2)
                self._key_widgets[kid] = lbl

        # Mouse Tester Strip
        sec_hdr(kb_wrap, "Test Chuột & Touchpad (Click để kiểm tra)", "🖱️")
        m_frame = tk.Frame(kb_wrap, bg=C["bg"], pady=6)
        m_frame.pack(fill="x")

        self._m_left = tk.Label(m_frame, text="Chuột Trái (Left Click)\n0 lần",
                                font=FONTS["label"], bg=C["surface2"], fg=C["text"],
                                width=22, height=3, relief="ridge", bd=1)
        self._m_left.pack(side="left", padx=6)

        self._m_mid = tk.Label(m_frame, text="Con Lăn / Giữa (Middle)\n0 lần",
                               font=FONTS["label"], bg=C["surface2"], fg=C["text"],
                               width=22, height=3, relief="ridge", bd=1)
        self._m_mid.pack(side="left", padx=6)

        self._m_right = tk.Label(m_frame, text="Chuột Phải (Right Click)\n0 lần",
                                font=FONTS["label"], bg=C["surface2"], fg=C["text"],
                                width=22, height=3, relief="ridge", bd=1)
        self._m_right.pack(side="left", padx=6)

        self._m_left.bind("<Button-1>", lambda e: self._on_mouse("L"))
        self._m_mid.bind("<Button-2>", lambda e: self._on_mouse("M"))
        self._m_right.bind("<Button-3>", lambda e: self._on_mouse("R"))
        kb_wrap.bind_all("<MouseWheel>", self._on_wheel)

        # Global Key Bindings
        self.bind_all("<KeyPress>", self._on_key_press)
        self.bind_all("<KeyRelease>", self._on_key_release)

    def _on_wheel(self, e):
        self._mouse_clicks["W"] += 1
        self._m_mid.config(text=f"Con Lăn / Giữa\n{self._mouse_clicks['M']} click · {self._mouse_clicks['W']} lăn",
                           bg=C["green_bg"], fg=C["green"])

    def _on_mouse(self, btn):
        self._mouse_clicks[btn] += 1
        if btn == "L":
            self._m_left.config(text=f"Chuột Trái\n{self._mouse_clicks['L']} lần [OK]", bg=C["green_bg"], fg=C["green"])
        elif btn == "M":
            self._m_mid.config(text=f"Con Lăn / Giữa\n{self._mouse_clicks['M']} click [OK]", bg=C["green_bg"], fg=C["green"])
        elif btn == "R":
            self._m_right.config(text=f"Chuột Phải\n{self._mouse_clicks['R']} lần [OK]", bg=C["green_bg"], fg=C["green"])

    def _resolve_kid(self, e):
        sym = e.keysym.lower()
        if sym in self._key_widgets: return sym
        # Aliases
        alias = {
            "escape": "esc", "return": "enter", "backspace": "backspace",
            "caps_lock": "caps", "control_l": "ctrl_l", "control_r": "ctrl_r",
            "shift_l": "shift_l", "shift_r": "shift_r", "alt_l": "alt_l", "alt_r": "alt_r",
            "win_l": "win", "win_r": "win", "super_l": "win", "super_r": "win",
            "print": "prtsc", "delete": "delete", "grave": "`", "asciitilde": "`",
            "bracketleft": "[", "bracketright": "]", "backslash": "\\",
            "semicolon": ";", "apostrophe": "'", "comma": ",", "period": ".",
            "slash": "/", "minus": "-", "equal": "=", "space": "space",
        }
        return alias.get(sym, sym)

    def _on_key_press(self, e):
        kid = self._resolve_kid(e)
        self._lbl_recent.config(text=f"Phím vừa bấm: [{e.keysym}]  ·  KeyCode: {e.keycode}  ·  Keysym: {e.keysym}")
        if kid in self._key_widgets:
            self._key_widgets[kid].config(bg=C["key_hit"], fg="#000000")
            self._tested_keys.add(kid)
            pct = int((len(self._tested_keys) / self._total_keys) * 100)
            self._lbl_count.config(text=f"Đã test: {len(self._tested_keys)} / {self._total_keys} phím ({pct}%)")

    def _on_key_release(self, e):
        kid = self._resolve_kid(e)
        if kid in self._key_widgets:
            self._key_widgets[kid].config(bg=C["key_done"], fg="#000000")

    def _reset(self):
        self._tested_keys.clear()
        for lbl in self._key_widgets.values():
            lbl.config(bg=C["key_bg"], fg=C["text"])
        self._mouse_clicks = {"L": 0, "M": 0, "R": 0, "W": 0}
        self._m_left.config(text="Chuột Trái (Left Click)\n0 lần", bg=C["surface2"], fg=C["text"])
        self._m_mid.config(text="Con Lăn / Giữa (Middle)\n0 lần", bg=C["surface2"], fg=C["text"])
        self._m_right.config(text="Chuột Phải (Right Click)\n0 lần", bg=C["surface2"], fg=C["text"])
        self._lbl_count.config(text="Đã test: 0 phím")
        self._lbl_recent.config(text="Đã đặt lại trạng thái bàn phím.")

# ─────────────────────────────────────────────────────────────
#  PANEL: DISPLAY & DEAD PIXEL TEST
# ─────────────────────────────────────────────────────────────
class DisplayPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        topbar(self, "🖥️  Kiểm tra Màn hình & Điểm chết (Dead Pixel)", self.app)
        body = scrollable(self)

        sec_hdr(body, "Thông số Kỹ thuật Màn hình", "📊")
        c = card(body)
        d_info = get_display_info()
        irow(c, "Độ phân giải hiện tại", d_info["res"], C["cyan"])
        irow(c, "Tần số quét (Refresh Rate)", d_info["freq"], C["green"])
        irow(c, "Độ sâu màu (Color Depth)", d_info["depth"])
        irow(c, "Tỷ lệ khung hình (Aspect Ratio)", d_info["ratio"])
        irow(c, "Card màn hình xuất hình (GPU)", d_info["gpu"], C["accent_h"])

        sec_hdr(body, "Công cụ Test Màn hình Toàn màn hình", "🚀")
        action_c = card(body, pady=16)
        tk.Label(action_c,
                 text="Chế độ Fullscreen lần lượt chuyển qua các màu chuẩn:\n"
                      "  • ⬛ Đen tuyền: Soi hở sáng IPS, điểm sáng kẹt (Stuck pixel)\n"
                      "  • ⬜ Trắng tinh: Soi điểm chết đen (Dead pixel), bụi phản quang, ố vàng\n"
                      "  • 🟥 Đỏ, 🟩 Xanh lá, 🟦 Xanh dương: Kiểm tra sub-pixel\n"
                      "  • 🟨 Vàng, 🟪 Xám: Kiểm tra dải màu & độ đồng đều ánh sáng",
                 font=FONTS["body"], bg=C["surface"], fg=C["text2"], justify="left").pack(anchor="w", pady=(0, 14))

        tk.Button(action_c, text="  🚀 BẮT ĐẦU TEST MÀN HÌNH (FULLSCREEN)  ",
                  font=FONTS["title"], bg=C["purple"], fg=C["white"],
                  relief="flat", cursor="hand2", padx=20, pady=10,
                  command=self._start_dead_pixel_test).pack(anchor="w")

        sec_hdr(body, "Hướng dẫn thao tác trong khi Test", "💡")
        tip_c = card(body)
        tk.Label(tip_c,
                 text="  • Click chuột trái hoặc bấm [Space] / [Mũi tên] để chuyển sang màu tiếp theo\n"
                      "  • Bấm [Mũi tên trái] để quay lại màu trước\n"
                      "  • Bấm phím [ESC] hoặc Click chuột phải để THOÁT ra bất cứ lúc nào",
                 font=FONTS["body"], bg=C["surface"], fg=C["yellow"], justify="left").pack(anchor="w")

    def _start_dead_pixel_test(self):
        PALETTE = [
            ("#000000", "Đen tuyền", "Soi hở sáng IPS, điểm sáng (Stuck pixel)"),
            ("#FFFFFF", "Trắng tinh", "Soi điểm chết đen (Dead pixel), bụi màn hình, ố phản quang"),
            ("#FF0000", "Đỏ tươi (Red)", "Kiểm tra bóng sub-pixel Red"),
            ("#00FF00", "Xanh lá (Green)", "Kiểm tra bóng sub-pixel Green"),
            ("#0000FF", "Xanh dương (Blue)", "Kiểm tra bóng sub-pixel Blue"),
            ("#FFFF00", "Vàng chanh (Yellow)", "Kiểm tra dải màu sáng"),
            ("#00FFFF", "Xanh ngọc (Cyan)", "Kiểm tra dải màu trung tính"),
            ("#FF00FF", "Tím hồng (Magenta)", "Kiểm tra dải màu rực rỡ"),
            ("#808080", "Xám 50% (Gray)", "Kiểm tra độ đồng đều dải sáng"),
        ]

        top = tk.Toplevel(self)
        top.attributes('-fullscreen', True)
        top.configure(bg=PALETTE[0][0])
        idx = [0]

        lbl = tk.Label(top, text="", font=FONTS["label"], bg="#111111", fg="#ffffff", padx=14, pady=6)
        lbl.place(relx=0.5, rely=0.92, anchor="center")

        def _update():
            color, name, desc = PALETTE[idx[0]]
            top.configure(bg=color)
            lbl.config(text=f"Màu: {name} ({idx[0]+1}/{len(PALETTE)})  ·  {desc}  ·  [Click/Space: Đổi màu | ESC: Thoát]")
            lbl.lift()
            top.after(3000, lambda: lbl.place_forget())

        def _next(e=None):
            idx[0] = (idx[0] + 1) % len(PALETTE)
            lbl.place(relx=0.5, rely=0.92, anchor="center")
            _update()

        def _prev(e=None):
            idx[0] = (idx[0] - 1 + len(PALETTE)) % len(PALETTE)
            lbl.place(relx=0.5, rely=0.92, anchor="center")
            _update()

        def _quit(e=None):
            top.destroy()

        top.bind("<Button-1>", _next)
        top.bind("<space>", _next)
        top.bind("<Right>", _next)
        top.bind("<Left>", _prev)
        top.bind("<Button-3>", _quit)
        top.bind("<Escape>", _quit)
        _update()

# ─────────────────────────────────────────────────────────────
#  PANEL: MULTIMEDIA (SPEAKER, MIC, WEBCAM)
# ─────────────────────────────────────────────────────────────
class MultimediaPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        topbar(self, "🔊  Kiểm tra Âm thanh, Mic & Webcam", self.app)
        body = scrollable(self)

        sec_hdr(body, "Kiểm tra Loa Stereo Laptop / Tai nghe", "🎧")
        sc = card(body, pady=12)
        tk.Label(sc, text="Phát âm thanh riêng biệt từng kênh để phát hiện loa rè hoặc hỏng 1 bên loa:",
                 font=FONTS["body"], bg=C["surface"], fg=C["text2"]).pack(anchor="w", pady=(0, 10))

        btn_box = tk.Frame(sc, bg=C["surface"])
        btn_box.pack(anchor="w")

        tk.Button(btn_box, text="🔊 Test Loa Trái (Left)", font=FONTS["label"],
                  bg=C["blue"], fg=C["white"], relief="flat", cursor="hand2", padx=12, pady=6,
                  command=lambda: play_channel_tone("left", 440.0)).pack(side="left", padx=4)

        tk.Button(btn_box, text="🔊 Test Loa Phải (Right)", font=FONTS["label"],
                  bg=C["cyan"], fg=C["white"], relief="flat", cursor="hand2", padx=12, pady=6,
                  command=lambda: play_channel_tone("right", 880.0)).pack(side="left", padx=4)

        tk.Button(btn_box, text="🎧 Test Cả 2 Loa (Stereo)", font=FONTS["label"],
                  bg=C["accent"], fg=C["white"], relief="flat", cursor="hand2", padx=12, pady=6,
                  command=lambda: play_channel_tone("both", 660.0)).pack(side="left", padx=4)

        sec_hdr(body, "Kiểm tra Microphone", "🎙️")
        mc = card(body, pady=10)
        tk.Label(mc, text="Mở công cụ kiểm tra độ nhạy mic hoặc ghi âm giọng nói trực tiếp:",
                 font=FONTS["body"], bg=C["surface"], fg=C["text2"]).pack(anchor="w", pady=(0, 8))

        m_btn_box = tk.Frame(mc, bg=C["surface"])
        m_btn_box.pack(anchor="w")

        def _open_sound_rec():
            try: subprocess.Popen(["start", "ms-soundrecorder:"], shell=True)
            except: pass

        def _open_sound_settings():
            try: subprocess.Popen(["start", "ms-settings:sound"], shell=True)
            except: pass

        tk.Button(m_btn_box, text="🎙️ Mở Windows Sound Recorder (Ghi âm)", font=FONTS["label"],
                  bg=C["green"], fg="#000000", relief="flat", cursor="hand2", padx=12, pady=6,
                  command=_open_sound_rec).pack(side="left", padx=4)

        tk.Button(m_btn_box, text="⚙️ Cài đặt Âm thanh Windows", font=FONTS["label"],
                  bg=C["surface2"], fg=C["text"], relief="flat", cursor="hand2", padx=12, pady=6,
                  command=_open_sound_settings).pack(side="left", padx=4)

        sec_hdr(body, "Kiểm tra Webcam & Camera", "📷")
        cc = card(body, pady=10)
        tk.Label(cc, text="Mở ứng dụng Camera gốc của Windows để soi hình ảnh, độ nét và đèn báo webcam:",
                 font=FONTS["body"], bg=C["surface"], fg=C["text2"]).pack(anchor="w", pady=(0, 8))

        def _open_camera():
            try: subprocess.Popen(["start", "microsoft.windows.camera:"], shell=True)
            except: pass

        tk.Button(cc, text="📷 Mở Windows Camera Test Trực Tiếp", font=FONTS["label"],
                  bg=C["pink"], fg=C["white"], relief="flat", cursor="hand2", padx=14, pady=6,
                  command=_open_camera).pack(anchor="w")

        sec_hdr(body, "Thiết bị Phần cứng nhận diện trên máy", "🏷️")
        hw_c = card(body)
        mm_info = get_multimedia_info()
        cams = ", ".join(mm_info["cameras"]) if mm_info["cameras"] else "Không phát hiện camera hoặc driver riêng"
        irow(hw_c, "Camera / Webcam", cams, C["cyan"])
        auds = "\n".join(f"• {a}" for a in mm_info["audio_devices"][:5]) if mm_info["audio_devices"] else "Realtek Audio"
        irow(hw_c, "Card âm thanh (Audio)", auds)

# ─────────────────────────────────────────────────────────────
#  PANEL: WINDOWS LICENSE
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
                  cursor="hand2", padx=10, command=self._load).pack(side="right", padx=10)
        self._body = scrollable(self)
        self._load()

    def _load(self):
        for w in self._body.winfo_children(): w.destroy()
        tk.Label(self._body, text="⏳ Đang kiểm tra bản quyền Windows…",
                 font=FONTS["body"], bg=C["bg"], fg=C["text2"], pady=40).pack()
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        info = get_win_info()
        self.after(0, lambda: self._render(info))

    def _render(self, info):
        for w in self._body.winfo_children(): w.destroy()

        is_lic = "LICENSED" in info["activation_status"]
        is_kms = "KMS" in info["license_type"]

        bg_col = C["green_bg"] if (is_lic and not is_kms) else (C["yellow_bg"] if is_kms else C["red_bg"])
        fg_col = C["green"] if (is_lic and not is_kms) else (C["yellow"] if is_kms else C["red"])

        top_c = card(self._body, bg=bg_col, pady=14)
        tk.Label(top_c, text=info["activation_status"], font=FONTS["title"], bg=bg_col, fg=fg_col).pack()
        tk.Label(top_c, text=info["license_type"], font=FONTS["body"], bg=bg_col, fg=C["text"]).pack(pady=2)

        sec_hdr(self._body, "Thông tin Hệ điều hành", "ℹ️")
        c1 = card(self._body)
        irow(c1, "Tên Windows",       info.get("product_name"))
        irow(c1, "Edition",           info.get("edition"))
        irow(c1, "Phiên bản (Build)", f"{info.get('version')} (Build {info.get('build')})")
        irow(c1, "Kiến trúc",         info.get("arch"))
        irow(c1, "Ngày cài đặt",      info.get("install_date"))
        irow(c1, "Chủ sở hữu",        info.get("registered"))
        irow(c1, "Product ID",        info.get("product_id"))

        sec_hdr(self._body, "Bảo mật & Kích hoạt", "🔒")
        c2 = card(self._body)
        irow(c2, "Windows Defender",  info.get("defender"))
        if info.get("kms_server"):
            irow(c2, "KMS Host Server", info.get("kms_server"), C["red"])

        if info.get("activation_raw"):
            sec_hdr(self._body, "Chi tiết từ slmgr.vbs", "📋")
            c3 = card(self._body)
            t = tk.Text(c3, height=8, bg=C["surface2"], fg=C["text2"],
                        font=FONTS["mono"], relief="flat", wrap="word")
            t.pack(fill="x", padx=4, pady=4)
            t.insert("1.0", info["activation_raw"])
            t.config(state="disabled")

# ─────────────────────────────────────────────────────────────
#  PANEL: PIRACY SCAN
# ─────────────────────────────────────────────────────────────
class PiracyPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        top = topbar(self, "🔍  Phát hiện Phần mềm Lậu / Crack", self.app)
        tk.Button(top, text="🔄 Quét lại", font=FONTS["label"],
                  bg=C["red"], fg=C["white"], relief="flat",
                  cursor="hand2", padx=10, command=self._load).pack(side="right", padx=10)
        self._body = scrollable(self)
        self._load()

    def _load(self):
        for w in self._body.winfo_children(): w.destroy()
        tk.Label(self._body, text="⏳ Đang quét phần mềm nghi vấn…",
                 font=FONTS["body"], bg=C["bg"], fg=C["text2"], pady=40).pack()
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        sw = get_installed_software()
        flagged, cprocs = scan_piracy(sw)
        self.after(0, lambda: self._render(flagged, cprocs, len(sw)))

    def _render(self, flagged, cprocs, total):
        for w in self._body.winfo_children(): w.destroy()

        is_clean = not flagged and not cprocs
        bg_col = C["green_bg"] if is_clean else C["red_bg"]
        fg_col = C["green"] if is_clean else C["red"]

        top_c = card(self._body, bg=bg_col, pady=14)
        tk.Label(top_c, text="✅  HỆ THỐNG SẠCH SẼ" if is_clean else f"⚠️  PHÁT HIỆN {len(flagged) + len(cprocs)} DẤU HIỆU LẬU",
                 font=FONTS["title"], bg=bg_col, fg=fg_col).pack()
        tk.Label(top_c, text=f"Đã quét {total} phần mềm cài đặt",
                 font=FONTS["body"], bg=bg_col, fg=C["text"]).pack(pady=2)

        if cprocs:
            sec_hdr(self._body, f"Crack Process đang chạy ({len(cprocs)})", "🔴")
            c = card(self._body, bg=C["red_bg"])
            for p in cprocs:
                tk.Label(c, text=f"  ⚠  {p}", font=FONTS["mono_b"],
                         bg=C["red_bg"], fg=C["red"]).pack(anchor="w", pady=2)

        if flagged:
            sec_hdr(self._body, f"Phần mềm nghi vấn ({len(flagged)})", "⚠️")
            for item in flagged:
                c = card(self._body, bg="#201010", pady=8)
                tk.Label(c, text=item["name"], font=FONTS["header"],
                         bg="#201010", fg=C["red"]).pack(anchor="w")
                if item.get("publisher"):
                    tk.Label(c, text=f"  Publisher: {item['publisher']}",
                             font=FONTS["small"], bg="#201010", fg=C["text2"]).pack(anchor="w")
                for r in item["reasons"]:
                    tk.Label(c, text=f"    → {r}", font=FONTS["body"],
                             bg="#201010", fg=C["yellow"]).pack(anchor="w")

# ─────────────────────────────────────────────────────────────
#  PANEL: INSTALLED SOFTWARE
# ─────────────────────────────────────────────────────────────
class SoftwarePanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._all = []
        self._build()

    def _build(self):
        topbar(self, "🧩  Phần mềm Đã cài đặt", self.app)

        sb = tk.Frame(self, bg=C["surface2"], pady=8, padx=16)
        sb.pack(fill="x")
        tk.Label(sb, text="🔍 Tìm:", font=FONTS["label"],
                 bg=C["surface2"], fg=C["text2"]).pack(side="left", padx=(0, 6))
        self._q = tk.StringVar()
        self._q.trace_add("write", lambda *_: self._filter())
        tk.Entry(sb, textvariable=self._q, font=FONTS["body"],
                 bg=C["surface"], fg=C["text"], relief="flat", insertbackground=C["text"],
                 width=30).pack(side="left")

        self._cnt = tk.Label(sb, text="", font=FONTS["small"],
                             bg=C["surface2"], fg=C["text2"])
        self._cnt.pack(side="right")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=C["surface"], foreground=C["text"],
                        rowheight=26, fieldbackground=C["surface"],
                        font=FONTS["body"])
        style.configure("Treeview.Heading",
                        background=C["surface2"], foreground=C["text2"],
                        font=FONTS["label"], relief="flat")
        style.map("Treeview",
                  background=[("selected", C["accent"])],
                  foreground=[("selected", C["white"])])

        cols = ("name", "version", "publisher", "date")
        self._tv = ttk.Treeview(self, columns=cols, show="headings", height=20)
        for col, hdr, w in [
            ("name",      "Tên phần mềm",  360),
            ("version",   "Phiên bản",     120),
            ("publisher", "Nhà phát triển", 220),
            ("date",      "Ngày cài",      100),
        ]:
            self._tv.heading(col, text=hdr)
            self._tv.column(col, width=w, anchor="w")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tv.yview)
        self._tv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tv.pack(fill="both", expand=True, padx=8, pady=4)
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        self._all = get_installed_software()
        self.after(0, self._filter)

    def _filter(self):
        q = self._q.get().lower()
        self._tv.delete(*self._tv.get_children())
        filtered = [s for s in self._all if q in s["name"].lower() or q in s["publisher"].lower()]
        for s in filtered:
            self._tv.insert("", "end", values=(s["name"], s["version"], s["publisher"], s["date"]))
        self._cnt.config(text=f"Hiển thị {len(filtered)} / {len(self._all)} phần mềm")

# ─────────────────────────────────────────────────────────────
#  PANEL: SYSTEM INFO
# ─────────────────────────────────────────────────────────────
class SystemPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        topbar(self, "📊  Thông số Hệ thống", self.app)
        body = scrollable(self)
        hw = get_hardware()

        sec_hdr(body, "Bộ vi xử lý (CPU)", "⚡")
        c = card(body)
        irow(c, "Tên CPU", hw["cpu"], C["cyan"])
        irow(c, "Số nhân / Luồng", f"{hw['cores']} nhân vật lý / {hw['logi']} luồng logic")
        irow(c, "Xung nhịp hiện tại", hw["freq"])

        sec_hdr(body, "Bộ nhớ RAM", "💾")
        c2 = card(body)
        irow(c2, "Tổng dung lượng", hw["ram"], C["green"])
        irow(c2, "Khả dụng (Free)", hw["ram_free"])

        sec_hdr(body, "Đồ họa (GPU)", "🎮")
        c3 = card(body)
        irow(c3, "Card màn hình", hw["gpu"], C["accent_h"])

        sec_hdr(body, "Bo mạch chủ & BIOS", "🖥️")
        c4 = card(body)
        irow(c4, "Mainboard", hw["mobo"])
        irow(c4, "Phiên bản BIOS", hw["bios"])
        irow(c4, "Thời gian bật máy (Uptime)", hw["uptime"])

# ─────────────────────────────────────────────────────────────
#  PANEL: PROCESSES
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
                  cursor="hand2", padx=10, command=self._load).pack(side="right", padx=10)

        self._cnt = tk.Label(self, text="", font=FONTS["small"], bg=C["bg"], fg=C["text2"])
        self._cnt.pack(anchor="w", padx=16, pady=4)

        cols = ("pid", "name", "cpu", "mem", "status", "flag")
        self._tv = ttk.Treeview(self, columns=cols, show="headings", height=24)
        for col, hdr, w in [
            ("pid",    "PID",      70),
            ("name",   "Process", 280),
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
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "status"]):
            try: procs.append(p.info)
            except: pass
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
#  PANEL: REPORT
# ─────────────────────────────────────────────────────────────
class ReportPanel(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        topbar(self, "📋  Xuất Báo cáo Máy tính (Audit Report)", self.app)
        body = scrollable(self)

        sec_hdr(body, "Tùy chọn xuất file", "💾")
        for label, color, cmd in [
            ("📄  Báo cáo đầy đủ  (Windows + Pin + SMART + Hardware + Crack + Apps)", C["accent"], self._full),
            ("🔍  Kết quả quét phần mềm lậu & crack", C["red"], self._piracy),
            ("📊  Thông số phần cứng, Pin & Ổ đĩa", C["blue"], self._hw),
        ]:
            f = tk.Frame(body, bg=C["surface"], pady=14, padx=16)
            f.pack(fill="x", padx=16, pady=5)
            tk.Label(f, text=label, font=FONTS["header"], bg=C["surface"], fg=C["text"]).pack(side="left")
            tk.Button(f, text="Xuất file .TXT", font=FONTS["label"],
                      bg=color, fg=C["white"], relief="flat", padx=14, pady=4, cursor="hand2",
                      command=cmd).pack(side="right")

        sec_hdr(body, "Chia sẻ kết quả", "📤")
        sf = card(body)
        tk.Label(sf,
                 text="Sau khi xuất file .txt, bạn có thể:\n"
                      "  • Gửi qua Zalo / Telegram / Email khi mua bán kiểm tra máy\n"
                      "  • Lưu trữ hồ sơ bảo hành và theo dõi độ chai pin định kỳ",
                 font=FONTS["body"], bg=C["surface"], fg=C["text2"], justify="left").pack(anchor="w")

    def _savepath(self, name):
        return filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"{name}_{socket.gethostname()}_{datetime.date.today()}",
            filetypes=[("Text file", "*.txt")])

    def _full(self):
        path = self._savepath("PC_Audit_Report")
        if not path: return
        try:
            wi = get_win_info()
            hw = get_hardware()
            bat = get_battery_info()
            disks = get_disk_health_info()
            sw = get_installed_software()
            flagged, cprocs = scan_piracy(sw)

            lines = [
                "=" * 65,
                "         BÁO CÁO KIỂM TRA MÁY TÍNH & LAPTOP (PC AUDIT)",
                f"  Ngày tạo   : {datetime.datetime.now():%d/%m/%Y %H:%M:%S}",
                f"  Tên máy    : {socket.gethostname()}",
                "=" * 65, "",
                "--- WINDOWS & LICENSE ---",
                f"  Hệ điều hành: {wi.get('product_name')}",
                f"  Phiên bản   : {wi.get('version')} (Build {wi.get('build')})",
                f"  Trạng thái  : {wi.get('activation_status')}",
                f"  Loại bản quyền: {wi.get('license_type')}",
                f"  Product ID  : {wi.get('product_id')}",
                f"  Defender    : {wi.get('defender')}",
                "",
                "--- PIN & NGUỒN (LAPTOP) ---",
                f"  Trạng thái  : {bat['status_text']}",
                f"  Sức khỏe pin: {bat['health_pct']}%  (Chai {bat['wear_level']}%)",
                f"  Dung lượng  : Sạc đầy {bat['full_cap']:,} mWh / Thiết kế {bat['design_cap']:,} mWh",
                f"  Chu kỳ sạc  : {bat['cycle_count']} lần",
                "",
                "--- S.M.A.R.T Ổ CỨNG VẬT LÝ ---",
            ]
            for d in disks:
                lines.append(f"  • {d['model']} [{d['bus']}] - Dung lượng: {d['size']} - Tình trạng: {d['health']}")
                if d['hours'] != 'N/A': lines.append(f"    Giờ chạy: {d['hours']} | Nhiệt độ: {d['temp']} | Hao mòn: {d['wear']}")

            lines += [
                "",
                "--- PHẦN CỨNG CHÍNH ---",
                f"  CPU  : {hw['cpu']}",
                f"  RAM  : {hw['ram']}",
                f"  GPU  : {hw['gpu']}",
                f"  Mobo : {hw['mobo']}",
                f"  BIOS : {hw['bios']}",
                f"  Uptime: {hw['uptime']}",
                "",
                f"--- PHẦN MỀM NGHI VẤN LẬU ({len(flagged)}) ---",
            ]
            for s in flagged:
                lines.append(f"  ⚠ {s['name']}  |  {s['publisher']}")
                for r in s["reasons"]: lines.append(f"      → {r}")
            if cprocs:
                lines.append("  Crack Processes running: " + ", ".join(cprocs))

            lines += ["", f"--- DANH SÁCH TẤT CẢ PHẦN MỀM CÀI ĐẶT ({len(sw)}) ---"]
            for s in sw:
                lines.append(f"  {s['name'][:50]:50s} | {s['version'][:20]:20s} | {s['publisher']}")

            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("✅ Thành công", f"Đã xuất báo cáo tại:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _piracy(self):
        path = self._savepath("Piracy_Scan")
        if not path: return
        try:
            sw = get_installed_software()
            flagged, cprocs = scan_piracy(sw)
            lines = [
                f"PIRACY AUDIT — {datetime.datetime.now():%d/%m/%Y %H:%M}",
                f"Máy: {socket.gethostname()}",
                f"Tổng apps: {len(sw)} | Nghi vấn: {len(flagged)} | Crack procs: {len(cprocs)}", "",
            ]
            for s in flagged:
                lines.append(f"❌ {s['name']}")
                for r in s["reasons"]: lines.append(f"   → {r}")
            with open(path, "w", encoding="utf-8") as f: f.write("\n".join(lines))
            messagebox.showinfo("✅ Thành công", f"Đã lưu tại:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _hw(self):
        path = self._savepath("Hardware_Report")
        if not path: return
        try:
            hw = get_hardware()
            bat = get_battery_info()
            lines = [
                f"HARDWARE & BATTERY — {datetime.datetime.now():%d/%m/%Y %H:%M}",
                f"Máy: {socket.gethostname()}",
                f"CPU: {hw['cpu']}",
                f"RAM: {hw['ram']}",
                f"GPU: {hw['gpu']}",
                f"Mobo: {hw['mobo']}",
                f"Pin: Sức khỏe {bat['health_pct']}%, Chai {bat['wear_level']}%, Chu kỳ sạc {bat['cycle_count']}",
            ]
            with open(path, "w", encoding="utf-8") as f: f.write("\n".join(lines))
            messagebox.showinfo("✅ Thành công", f"Đã lưu tại:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

# ─────────────────────────────────────────────────────────────
#  APP SHELL (ROUTER)
# ─────────────────────────────────────────────────────────────
PANEL_MAP = {
    "home":        HomePanel,
    "win":         WinPanel,
    "piracy":      PiracyPanel,
    "battery":     BatteryPanel,
    "disk_health": DiskHealthPanel,
    "keyboard":    KeyboardPanel,
    "display":     DisplayPanel,
    "multimedia":  MultimediaPanel,
    "software":    SoftwarePanel,
    "system":      SystemPanel,
    "process":     ProcessPanel,
    "report":      ReportPanel,
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💻 PC & Laptop Status Checker Pro")
        self.geometry("1100x750")
        self.minsize(920, 620)
        self.configure(bg=C["bg"])

        try:
            admin_txt = "  [Admin ✓]" if ctypes.windll.shell32.IsUserAnAdmin() else "  [Chạy với Admin để đầy đủ thông số]"
            self.title(f"💻 PC & Laptop Status Checker Pro {admin_txt}")
        except:
            pass

        self._cache  = {}
        self._active = None

        sb = tk.Frame(self, bg=C["surface2"], pady=3)
        sb.pack(fill="x", side="bottom")
        self._st = tk.Label(sb, text="", font=FONTS["small"], bg=C["surface2"], fg=C["text2"], padx=12)
        self._st.pack(side="left")
        self._cl = tk.Label(sb, text="", font=FONTS["small"], bg=C["surface2"], fg=C["text3"], padx=12)
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

    def clear_cache(self):
        for k, v in list(self._cache.items()):
            if k != "home":
                try: v.destroy()
                except: pass
                del self._cache[k]

    def _clock(self):
        self._cl.config(text=f"  {datetime.datetime.now():%A, %d/%m/%Y  %H:%M:%S}  ")
        self.after(1000, self._clock)

if __name__ == "__main__":
    app = App()
    app.mainloop()
