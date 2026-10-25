# 🖥️ PC Status Checker

Tool kiểm tra thông số PC/Laptop chạy Windows — giao diện đẹp, không cần cài gì thêm.

---

## ✨ Tính năng

| Tab | Nội dung |
|-----|----------|
| 📊 Dashboard | Live CPU/RAM/Disk/Network realtime, battery, uptime |
| 🖥️ System | OS, CPU, RAM, GPU, Mainboard, BIOS |
| 💾 Storage | Tất cả ổ đĩa + dung lượng (progress bar đẹp) |
| 🌐 Network | Adapter, IP, subnet + tốc độ mạng thực |
| 📦 Software | Danh sách phần mềm đã cài + search + sort |
| ⚙️ Processes | Top 200 process đang chạy (PID, CPU%, RAM) |

- 💾 **Export Report** → lưu file `.txt` đầy đủ thông số
- 🔄 **Refresh** bất kỳ lúc nào
- ⏱️ Live monitor cập nhật mỗi 2 giây

---

## 🚀 Cách dùng

### Cách 1: Chạy thẳng (cần Python)
```
pip install psutil wmi
python pc_checker.py
```
hoặc double-click `run.bat`

### Cách 2: Build thành .exe (đóng gói chạy mọi máy)
```
build.bat
```
→ File `dist\PC_Status_Checker.exe` — copy sang bất kỳ máy Windows nào, double-click là chạy, **không cần cài Python**.

---

## 📦 Cấu trúc

```
Tools Check Status PC/
├── pc_checker.py       ← Source code chính
├── run.bat             ← Chạy thẳng (cần Python)
├── build.bat           ← Đóng gói thành .exe
├── requirements.txt    ← Dependencies
└── dist/
    └── PC_Status_Checker.exe   ← File chạy sau khi build
```

---

## ⚙️ Yêu cầu (để build)
- Python 3.8+
- Windows 7/8/10/11

---

Made with ❤️ using Python + tkinter
