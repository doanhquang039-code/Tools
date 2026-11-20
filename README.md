# 💻 PC & Laptop Status Checker Pro

> **Kiểm tra Bản quyền Windows · Độ chai Pin Laptop · S.M.A.R.T Ổ cứng · Test Bàn phím & Chuột · Test Màn hình Điểm chết · Test Loa, Mic & Webcam**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightblue)](https://microsoft.com)
[![License](https://img.shields.io/badge/License-MIT-green)]()

Bộ công cụ Desktop Launcher kiểm tra toàn diện phần cứng, hệ điều hành và thiết bị ngoại vi chuyên dụng khi **mua bán, test máy cũ/mới, audit kỹ thuật**.

---

## 🚀 Cách dùng nhanh

### ⚡ Cách 1 — Chạy ngay không cần cài Python (Khuyên dùng)
> Máy bất kỳ (Windows 10/11) chỉ cần tải về là chạy:
```
1. Vào thư mục dist/ → Chạy PC_Status_Checker.exe
(hoặc click run.bat ngoài thư mục gốc)
```

### 🐍 Cách 2 — Chạy từ mã nguồn Python
```
1. Cài Python 3.8+ (tích "Add python to PATH")
2. Chạy run.bat (tự cài thư viện psutil, wmi nếu thiếu và khởi chạy app)
```

### 🛠️ Cách 3 — Đóng gói lại thành file .EXE độc lập
```
1. Chạy build.bat
2. File .exe mới sẽ nằm trong thư mục dist\PC_Status_Checker.exe
```

---

## ✨ Danh sách 11 Chức năng Kiểm tra

| Chức năng | Mô tả chi tiết |
|-----------|----------------|
| 🪟 **Bản quyền Windows** | Check Activation status, OEM / Retail / KMS, phát hiện crack bản quyền |
| 🔍 **Phát hiện phần mềm lậu** | Quét tên & đường dẫn cài đặt, phát hiện activator/keygen/crack |
| 🔋 **Pin & Sạc Laptop** *(Mới)* | **Độ chai pin (% Wear Level)**, Dung lượng thiết kế vs Sạc đầy (mWh), Số lần sạc (Cycle Count), Xuất báo cáo Pin Windows Battery Report HTML |
| 💾 **Sức khỏe Ổ cứng** *(Mới)* | **S.M.A.R.T NVMe / SSD / HDD**, Chuẩn giao tiếp BusType, Nhiệt độ ổ cứng, Giờ hoạt động (Power-On Hours), Độ hao mòn Wear % |
| ⌨️ **Bàn phím & Chuột** *(Mới)* | **Bàn phím ảo trực quan**: bấm phím nào sáng phím đó, phát hiện liệt phím/kẹt nút; Test Click chuột Trái, Phải, Con lăn & Cuộn |
| 🖥️ **Màn hình & Điểm chết** *(Mới)* | Đọc Độ phân giải & Tần số quét (Hz); **Dead Pixel Test Fullscreen** chuyển 9 màu (Đen, Trắng, Đỏ, Xanh lá, Xanh dương...) soi điểm chết & hở sáng IPS |
| 🔊 **Loa, Mic & Webcam** *(Mới)* | **Test Loa Trái (Left) & Loa Phải (Right) độc lập**, mở nhanh Windows Sound Recorder & Camera Windows test webcam |
| 📊 **Thông số hệ thống** | Chi tiết CPU, RAM, GPU, Mainboard, BIOS, Uptime |
| 🧩 **Phần mềm đã cài** | Danh sách phần mềm đã cài, tìm kiếm nhanh theo tên & nhà sản xuất |
| ⚙️ **Processes** | Top tiến trình ngốn CPU / RAM, gắn cờ process lạ |
| 📋 **Xuất báo cáo .TXT** | Xuất báo cáo kiểm tra chi tiết để gửi Zalo / Email khi giao dịch máy |

---

## 📁 Cấu trúc Thư mục

```
📂 Tools Check Status PC/
├── 📄 pc_checker.py      ← Source code hoàn chỉnh
├── ▶️  run.bat            ← Khởi chạy nhanh
├── 📦 build.bat           ← Đóng gói ra dist\PC_Status_Checker.exe
├── 📋 requirements.txt
└── 📖 README.md
```

---

## ⚙️ Yêu cầu Hệ thống
- **Hệ điều hành:** Windows 10 / Windows 11 (64-bit hoặc 32-bit)
- **Quyền hạn:** Nên mở bằng **Run as Administrator** để đọc đầy đủ các cảm biến phần cứng chuyên sâu.
