# 🚀 Antigravity Manager

> **Modern Antigravity Multi-Account Manager designed for macOS**

Antigravity Manager is a powerful utility tool designed to solve the pain point that Antigravity client does not natively support multi-account switching. By taking over the application's configuration state, it allows users to seamlessly switch between infinite accounts with one click, while providing automatic backup, process guarding, and a visual management interface.

---

## ✨ Core Features

### 🛡️ Account Security & Management
*   **Infinite Account Snapshots**: Create any number of account backups, fully saving login credentials, user configurations, and local state.
*   **Smart Recognition**: Automatically read the current logged-in account's email and ID from the database, no manual input required.
*   **Automatic Backup Mechanism**:
    *   **Startup Backup**: Automatically backup current state every time the manager starts to prevent accidental overwrites.
    *   **Switch Backup**: Automatically save the latest state of the current account before switching.
*   **Detailed Metadata**: Record creation time, last used time, email, and unique ID for each archive.

### ⚡️ Seamless Experience
*   **One-Click Switch**: Complete the "Close App -> Replace Data -> Restart App" process with just one click.
*   **Process Guard**:
    *   **Graceful Exit**: Prioritize using AppleScript to notify the app to exit normally, protecting data integrity.
    *   **Force Fallback**: If the app freezes, it will automatically upgrade to a forced termination strategy to ensure successful switching.
*   **Cross-Platform Support**: Perfectly adapted for macOS (Intel/Apple Silicon).

### 🎨 Modern Interface
*   **Flet Driven**: High-performance GUI based on Flutter, responsive.
*   **Native Integration**: Automatically adapts to system dark/light mode, providing a native window experience.
*   **User Friendly**: Clear list view, intuitive operation buttons, and friendly confirmation dialogs.

---

## 🛠️ Quick Start

### Requirements
*   **OS**: macOS 10.15+
*   **Python**: 3.10 or higher
*   **Antigravity**: Must be installed and run at least once

### 1. Install Dependencies
Run the following command in the project root directory to install required libraries:

```bash
pip install -r requirements.txt
```

### 2. Run Application

#### 🖥️ GUI Mode - Recommended
Launch the graphical interface for full interactive features:

```bash
python gui/main.py
```

#### ⌨️ CLI Mode
Suitable for script integration or geek users.

**Interactive Menu**:
```bash
python main.py
```

**Common Commands**:
```bash
# List all archives
python main.py list

# Backup current account (auto name)
python main.py add

# Backup with specific name
python main.py add -n "Work Account"

# Switch account (use ID or list index)
python main.py switch -i 1

# Delete backup
python main.py delete -i 1
```

---

## 📦 Packaging & Deployment

This project has built-in automated build scripts to generate standalone executables that do not require a Python environment.

### 🍎 macOS Packaging
Build `.app` application and `.dmg` installer.

```bash
# 1. Grant execution permission
chmod +x build_macos.sh

# 2. Run build
./build_macos.sh
```
*   **Output Path**: `gui/build/macos/`
*   **Includes**: `Antigravity Manager.app`, `Antigravity Manager.dmg`
*   **Architecture**: Universal Binary (Supports Intel & M1/M2/M3)

---

## 🧩 Technical Architecture

### Directory Structure
```
antigravity_manager/
├── assets/                 # Static resources (icons etc.)
├── gui/                    # Core codebase
│   ├── main.py             # GUI entry point
│   ├── account_manager.py  # Account logic (CRUD)
│   ├── process_manager.py  # Process control (Cross-platform process management)
│   ├── db_manager.py       # Data persistence (File operations)
│   ├── views/              # UI View Components
│   └── utils.py            # Common utilities
├── main.py                 # CLI entry point
├── build_macos.sh          # macOS build script
└── requirements.txt        # Python dependencies
```

### Data Storage
*   **Config File**: `~/.antigravity-agent/accounts.json` (Stores account list index)
*   **Backup Data**: `~/.antigravity-agent/backups/*.json` (Actual account data snapshots)
*   **Log File**: `~/.antigravity-agent/app.log`

---

## ❓ FAQ

**Q: Antigravity does not auto-start after switching account?**
A: Please ensure Antigravity is installed in the standard path (`/Applications`). If using a custom path, the program will attempt to start via URI protocol (`antigravity://`).

**Q: Where are backup files stored?**
A: All data is stored in the `.antigravity-agent` folder in the user's home directory. You can back up this folder manually at any time.

---

## 📄 License

This project is licensed under the MIT License. Issues and Pull Requests are welcome.

Copyright (c) 2025 Ctrler. All rights reserved.
