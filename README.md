# PR Config Tool

A desktop GUI application that reads environment configuration from an Excel file and automatically creates GitHub Pull Requests for the selected country/environment combination.

---

## ✨ Features

- **Country & Environment selector** — dropdowns auto-populated from your Excel file
- **Live config preview** — see all key/value pairs before submitting
- **PR body preview** — markdown table generated from config values
- **One-click PR creation** — branches are created automatically if they don't exist
- **Branch name** — driven by the `BRANCH_NAME` column in your Excel file
- **Color-coded environments** — green for dev, amber for staging, red for prod
- **Hot-reload** — reload the Excel file without restarting the app

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note**: `tkinter` ships with the Python standard library. If it's missing (some Linux distros strip it), install it via your package manager:
> ```bash
> # Ubuntu/Debian
> sudo apt install python3-tk
> # Fedora
> sudo dnf install python3-tkinter
> ```

### 2. Configure settings

Open `settings.py` and fill in:

```python
GITHUB_TOKEN = "ghp_your_personal_access_token"
GITHUB_OWNER = "your-org-or-username"
GITHUB_REPO  = "your-repository"
EXCEL_PATH   = "sample_config.xlsx"  # or path to your own file
```

> **Generating a GitHub Token**: Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens. Grant **Read/Write** access to **Contents** and **Pull Requests**.

### 3. Prepare your Excel file

Use `sample_config.xlsx` as a template. Required columns:

| Column | Description |
|--------|-------------|
| `Country` | Country code (e.g. US, UK, EU) |
| `Environment` | Environment name (dev, staging, prod) |
| `BRANCH_NAME` | Git branch to create the PR from |
| *(any others)* | Config keys that appear in the PR body |

### 4. Run the app

```bash
python main.py
```

---

## 📁 Project Structure

```
pr-config-tool/
├── main.py              # Tkinter UI application
├── config_reader.py     # Excel reader (openpyxl)
├── pr_creator.py        # GitHub REST API client
├── settings.py          # User configuration
├── requirements.txt     # Python dependencies
├── sample_config.xlsx   # Example Excel config file
└── README.md            # This file
```

---

## 🔧 How It Works

1. On startup, the app reads `EXCEL_PATH` and populates the **Country** dropdown.
2. Selecting a country filters the **Environment** dropdown.
3. Selecting an environment loads the matching row from Excel into the config table and builds a PR markdown preview.
4. Clicking **Create Pull Request**:
   - Finds (or creates) the feature branch specified in `BRANCH_NAME`
   - Commits a generated config file to that branch
   - Opens a PR against the repository's default branch
   - Shows the PR link and offers to open it in your browser

---

## 🎨 Environment Color Codes

| Environment | Color |
|-------------|-------|
| dev | 🟢 Green |
| staging | 🟡 Amber |
| prod | 🔴 Red |

---

## 🛡️ Security

- Never commit your GitHub token to version control.
- Consider storing the token in an environment variable and reading it with `os.environ.get("GITHUB_TOKEN")` instead of hardcoding it in `settings.py`.
