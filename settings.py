"""
settings.py
Edit this file to configure your GitHub repository and token.
"""

# ─── GitHub Settings ──────────────────────────────────────────────────────────
# Your GitHub Personal Access Token (needs repo scope).
# Get one at: https://github.com/settings/tokens
GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"

# The owner (user or org) and repository name.
GITHUB_OWNER = "your-org"
GITHUB_REPO  = "your-repo"

# ─── Excel Settings ───────────────────────────────────────────────────────────
# Path to your Excel configuration file (absolute or relative to main.py).
EXCEL_PATH = "sample_config.xlsx"

# ─── PR Settings ──────────────────────────────────────────────────────────────
# Default labels to apply to every created PR (must already exist in the repo).
DEFAULT_LABELS = ["config", "automated"]

# PR title template. Available placeholders: {country}, {environment}.
PR_TITLE_TEMPLATE = "config({country}): Update {environment} configuration"
