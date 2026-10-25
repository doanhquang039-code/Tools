# 🖥️ PC Status & License Checker

> **Kiểm tra bản quyền Windows · Phát hiện phần mềm lậu · Thông số hệ thống**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightblue)](https://microsoft.com)
[![License](https://img.shields.io/badge/License-MIT-green)]()

---

## 🚀 Cách dùng nhanh

### ⚡ Cách 1 — Chạy ngay không cần cài Python (Khuyên dùng)
> Máy bất kỳ (Windows 10/11) chỉ cần tải repo về là chạy được ngay:
```
1. Tải về từ GitHub (Code → Download ZIP hoặc git clone)
2. Mở thư mục dist → Double-click chạy PC_Status_Checker.exe
   (hoặc chỉ cần click run.bat ngoài thư mục gốc, tool sẽ tự động khởi chạy)
```

### 🐍 Cách 2 — Chạy từ mã nguồn Python
```
1. Cài đặt Python 3.8+ (tích chọn "Add python to PATH" khi cài)
2. Double-click run.bat
```
> `run.bat` sẽ tự kiểm tra và cài đặt thư viện (`psutil`, `wmi`) nếu máy còn thiếu, sau đó khởi động app.

### 🛠️ Cách 3 — Tự đóng gói (Build lại .exe)
```
1. Chạy build.bat
2. Đợi vài chục giây, file mới sẽ nằm trong thư mục dist\PC_Status_Checker.exe
```

---

## ✨ Tính năng

| Chức năng | Mô tả |
|-----------|-------|
| 🪟 **Bản quyền Windows** | Kiểm tra activation status, license type, phát hiện KMS crack |
| 🔍 **Phát hiện phần mềm lậu** | Quét tên & đường dẫn cài đặt, phát hiện activator/keygen/crack |
| 🧩 **Phần mềm đã cài** | Danh sách đầy đủ, tìm kiếm, sort theo tên/publisher/ngày |
| 📊 **Thông số hệ thống** | CPU · RAM · GPU · Mainboard · BIOS · Disk |
| ⚙️ **Processes** | Top 250 process đang chạy, flag process crack |
| 📋 **Xuất báo cáo** | Export `.txt` đầy đủ để gửi qua Zalo/Email |

---

## 🔍 Phát hiện những gì?

**Windows lậu:**
- KMS Activation (KMSpico, KMSAuto, HWID, Re-Loader, v.v.)
- Notification Mode / Unlicensed
- KMS Server bất thường

**Phần mềm lậu/crack:**
- Tên chứa từ khóa: `kmspico`, `keygen`, `crack`, `activator`, `patch`...
- Cài đặt từ đường dẫn đáng ngờ
- Không có publisher + tên đáng ngờ
- Crack process đang chạy real-time

---

## 📁 Cấu trúc

```
📂 Tools Check Status PC/
├── 📄 pc_checker.py      ← Source code chính (~600 dòng)
├── ▶️  run.bat            ← Chạy thẳng (cần Python)
├── 📦 build.bat           ← Đóng gói → dist\PC_Status_Checker.exe
├── 📋 requirements.txt
└── 📖 README.md
```

---

## ⚙️ Yêu cầu hệ thống

- **OS:** Windows 10 / 11
- **Python:** 3.8+ (chỉ cần khi chạy bằng source code)
- **Quyền:** Nên chạy với **Administrator** để kiểm tra bản quyền đầy đủ

---

## ⚠️ Lưu ý

- Tool này dùng để **kiểm tra, audit** — không phải antivirus
- Một số phần mềm crack tinh vi có thể không bị phát hiện
- KMS của **doanh nghiệp/trường học** (Volume License) có thể bị cảnh báo nhầm — bình thường
- Kết quả chính xác nhất khi chạy với quyền **Administrator**

---

Made with ❤️ — Python + tkinter
