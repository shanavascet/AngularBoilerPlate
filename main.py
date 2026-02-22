"""
main.py
PR Config Tool — Select a country + environment, preview the config loaded
from an Excel file, and raise a GitHub Pull Request with one click.

Run:
    python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
from pathlib import Path

import settings
from config_reader import ConfigReader
from pr_creator import GitHubPRCreator, build_pr_body

# ── Colour palette ─────────────────────────────────────────────────────────────
BG        = "#F0F4F8"
SIDEBAR   = "#1A2B4A"
ACCENT    = "#2563EB"
ACCENT_H  = "#1D4ED8"
SUCCESS   = "#16A34A"
DANGER    = "#DC2626"
WARN      = "#D97706"
TEXT      = "#1E293B"
MUTED     = "#94A3B8"
WHITE     = "#FFFFFF"
CARD      = "#FFFFFF"
BORDER    = "#CBD5E1"

ENV_COLORS = {
    "dev":     "#22C55E",
    "staging": "#F59E0B",
    "prod":    "#EF4444",
}


class PRConfigApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PR Config Tool")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._reader: ConfigReader | None = None
        self._config: dict | None = None

        self._load_reader(settings.EXCEL_PATH)
        self._build_ui()

    # ── Data ──────────────────────────────────────────────────────────────────

    def _load_reader(self, path: str):
        try:
            self._reader = ConfigReader(path)
        except Exception as e:
            messagebox.showerror("Excel Error", str(e))

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Sidebar ──────────────────────────────────────────────────────────
        sidebar = tk.Frame(self, bg=SIDEBAR, width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo / title
        logo_frame = tk.Frame(sidebar, bg=SIDEBAR)
        logo_frame.pack(fill="x", pady=(30, 10), padx=20)

        tk.Label(
            logo_frame, text="⚙️", font=("Segoe UI", 28), bg=SIDEBAR, fg=WHITE
        ).pack()
        tk.Label(
            logo_frame,
            text="PR Config Tool",
            font=("Segoe UI", 14, "bold"),
            bg=SIDEBAR,
            fg=WHITE,
        ).pack()
        tk.Label(
            logo_frame,
            text="Automated PR generator",
            font=("Segoe UI", 9),
            bg=SIDEBAR,
            fg=MUTED,
        ).pack()

        tk.Frame(sidebar, bg="#2D3F5F", height=1).pack(fill="x", padx=20, pady=20)

        # Excel file picker
        self._excel_path_var = tk.StringVar(value=settings.EXCEL_PATH)
        self._build_sidebar_section(sidebar, "📂 Config File")
        path_frame = tk.Frame(sidebar, bg=SIDEBAR)
        path_frame.pack(fill="x", padx=15, pady=(0, 12))

        path_entry = tk.Entry(
            path_frame,
            textvariable=self._excel_path_var,
            font=("Segoe UI", 8),
            bg="#2D3F5F",
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            bd=4,
        )
        path_entry.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(
            path_frame,
            text="…",
            font=("Segoe UI", 9, "bold"),
            bg=ACCENT,
            fg=WHITE,
            relief="flat",
            bd=0,
            padx=8,
            cursor="hand2",
            command=self._browse_excel,
        )
        browse_btn.pack(side="right", padx=(4, 0))

        # Country selector
        self._build_sidebar_section(sidebar, "🌍 Country")
        self._country_var = tk.StringVar()
        self._country_combo = ttk.Combobox(
            sidebar,
            textvariable=self._country_var,
            state="readonly",
            font=("Segoe UI", 11),
        )
        self._country_combo.pack(fill="x", padx=15, pady=(0, 12))
        self._country_combo.bind("<<ComboboxSelected>>", self._on_country_change)

        # Environment selector
        self._build_sidebar_section(sidebar, "🖥️ Environment")
        self._env_var = tk.StringVar()
        self._env_combo = ttk.Combobox(
            sidebar,
            textvariable=self._env_var,
            state="readonly",
            font=("Segoe UI", 11),
        )
        self._env_combo.pack(fill="x", padx=15, pady=(0, 12))
        self._env_combo.bind("<<ComboboxSelected>>", self._on_env_change)

        tk.Frame(sidebar, bg="#2D3F5F", height=1).pack(fill="x", padx=20, pady=20)

        # GitHub settings
        self._build_sidebar_section(sidebar, "🔑 GitHub Token")
        self._token_var = tk.StringVar(value=settings.GITHUB_TOKEN)
        token_entry = tk.Entry(
            sidebar,
            textvariable=self._token_var,
            font=("Segoe UI", 9),
            bg="#2D3F5F",
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            bd=4,
            show="•",
        )
        token_entry.pack(fill="x", padx=15, pady=(0, 8))

        self._build_sidebar_section(sidebar, "🏠 Owner / Repo")
        self._owner_var = tk.StringVar(value=settings.GITHUB_OWNER)
        self._repo_var  = tk.StringVar(value=settings.GITHUB_REPO)

        tk.Entry(
            sidebar, textvariable=self._owner_var,
            font=("Segoe UI", 9), bg="#2D3F5F", fg=WHITE,
            insertbackground=WHITE, relief="flat", bd=4,
        ).pack(fill="x", padx=15, pady=(0, 4))

        tk.Entry(
            sidebar, textvariable=self._repo_var,
            font=("Segoe UI", 9), bg="#2D3F5F", fg=WHITE,
            insertbackground=WHITE, relief="flat", bd=4,
        ).pack(fill="x", padx=15, pady=(0, 12))

        # ── Main content ──────────────────────────────────────────────────────
        content = tk.Frame(self, bg=BG)
        content.pack(side="right", fill="both", expand=True)

        # Header
        header = tk.Frame(content, bg=CARD, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        self._header_label = tk.Label(
            header,
            text="Select a country and environment to begin",
            font=("Segoe UI", 13, "bold"),
            bg=CARD,
            fg=TEXT,
        )
        self._header_label.pack(side="left", padx=24, pady=0)

        self._env_badge = tk.Label(
            header, text="", font=("Segoe UI", 10, "bold"),
            bg=CARD, fg=WHITE, padx=12, pady=4, relief="flat",
        )
        self._env_badge.pack(side="left", padx=8)

        # Status bar at bottom
        self._status_var = tk.StringVar(value="Ready")
        status_bar = tk.Frame(content, bg=CARD, height=32)
        status_bar.pack(side="bottom", fill="x")
        status_bar.pack_propagate(False)
        tk.Label(
            status_bar, textvariable=self._status_var,
            font=("Segoe UI", 9), bg=CARD, fg=MUTED, anchor="w"
        ).pack(side="left", padx=16, pady=0)

        # Action bar
        action_bar = tk.Frame(content, bg=BG, pady=12)
        action_bar.pack(side="bottom", fill="x", padx=20)

        self._pr_btn = tk.Button(
            action_bar,
            text="🚀  Create Pull Request",
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT,
            fg=WHITE,
            relief="flat",
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
            command=self._create_pr,
            state="disabled",
        )
        self._pr_btn.pack(side="right")
        self._hover(self._pr_btn, ACCENT, ACCENT_H)

        self._refresh_btn = tk.Button(
            action_bar,
            text="🔄  Reload Excel",
            font=("Segoe UI", 10),
            bg=CARD,
            fg=TEXT,
            relief="flat",
            bd=1,
            padx=16,
            pady=10,
            cursor="hand2",
            command=self._reload_excel,
        )
        self._refresh_btn.pack(side="right", padx=(0, 10))

        # Scroll area for config preview
        scroll_frame = tk.Frame(content, bg=BG)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(12, 0))

        # Config preview card
        preview_card = tk.Frame(scroll_frame, bg=CARD, relief="flat", bd=0)
        preview_card.pack(fill="both", expand=True)

        # Two-column layout: config table + PR preview
        left_pane = tk.Frame(preview_card, bg=CARD)
        left_pane.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=16)

        right_pane = tk.Frame(preview_card, bg=CARD, width=340)
        right_pane.pack(side="right", fill="y", padx=(8, 16), pady=16)
        right_pane.pack_propagate(False)

        # ── Config table (left) ──
        tk.Label(
            left_pane, text="Configuration Values",
            font=("Segoe UI", 11, "bold"), bg=CARD, fg=TEXT, anchor="w"
        ).pack(fill="x", pady=(0, 8))

        table_frame = tk.Frame(left_pane, bg=CARD)
        table_frame.pack(fill="both", expand=True)

        cols = ("Key", "Value")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Config.Treeview",
            background=CARD,
            foreground=TEXT,
            rowheight=28,
            fieldbackground=CARD,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Config.Treeview.Heading",
            background=ACCENT,
            foreground=WHITE,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map("Config.Treeview", background=[("selected", "#EFF6FF")])

        self._tree = ttk.Treeview(
            table_frame, columns=cols, show="headings",
            style="Config.Treeview", selectmode="none",
        )
        for c in cols:
            self._tree.heading(c, text=c)
            self._tree.column(c, anchor="w", width=200)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # ── PR preview (right) ──
        tk.Label(
            right_pane, text="PR Preview",
            font=("Segoe UI", 11, "bold"), bg=CARD, fg=TEXT, anchor="w"
        ).pack(fill="x", pady=(0, 8))

        self._pr_preview = scrolledtext.ScrolledText(
            right_pane,
            font=("Courier New", 9),
            bg="#F8FAFC",
            fg=TEXT,
            relief="flat",
            bd=1,
            wrap="word",
            state="disabled",
        )
        self._pr_preview.pack(fill="both", expand=True)

        # Populate countries
        self._populate_countries()

    def _build_sidebar_section(self, parent, label: str):
        tk.Label(
            parent, text=label,
            font=("Segoe UI", 9, "bold"),
            bg=SIDEBAR, fg=MUTED, anchor="w",
        ).pack(fill="x", padx=15, pady=(8, 2))

    @staticmethod
    def _hover(btn: tk.Button, normal: str, hover: str):
        btn.bind("<Enter>", lambda _: btn.config(bg=hover))
        btn.bind("<Leave>", lambda _: btn.config(bg=normal))

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _populate_countries(self):
        if not self._reader:
            return
        countries = self._reader.get_countries()
        self._country_combo["values"] = countries
        self._country_var.set("")
        self._env_combo["values"] = []
        self._env_var.set("")

    def _browse_excel(self):
        path = filedialog.askopenfilename(
            title="Select Excel Config File",
            filetypes=[("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")],
        )
        if path:
            self._excel_path_var.set(path)
            self._load_reader(path)
            self._populate_countries()
            self._clear_preview()

    def _reload_excel(self):
        if self._reader:
            try:
                self._reader.reload()
                self._populate_countries()
                self._clear_preview()
                self._set_status("✅ Excel reloaded successfully")
            except Exception as e:
                messagebox.showerror("Reload Error", str(e))

    def _on_country_change(self, _event=None):
        country = self._country_var.get()
        envs = self._reader.get_environments(country) if self._reader else []
        self._env_combo["values"] = envs
        self._env_var.set("")
        self._clear_preview()
        self._pr_btn.config(state="disabled")

    def _on_env_change(self, _event=None):
        country = self._country_var.get()
        env     = self._env_var.get()
        if not (country and env and self._reader):
            return

        self._config = self._reader.get_config(country, env)
        if not self._config:
            messagebox.showwarning("Not Found", f"No config for {country} / {env}")
            return

        self._refresh_table()
        self._refresh_pr_preview()
        self._update_header(country, env)
        self._pr_btn.config(state="normal")
        self._set_status(f"Loaded config: {country} / {env}")

    def _refresh_table(self):
        for row in self._tree.get_children():
            self._tree.delete(row)
        if not self._config:
            return
        skip = {"Country", "Environment", "BRANCH_NAME"}
        for i, (k, v) in enumerate(self._config.items()):
            if k in skip:
                continue
            tag = "even" if i % 2 == 0 else "odd"
            self._tree.insert("", "end", values=(k, v if v is not None else "—"), tags=(tag,))
        self._tree.tag_configure("even", background="#F8FAFC")
        self._tree.tag_configure("odd",  background=CARD)

    def _refresh_pr_preview(self):
        if not self._config:
            return
        country = self._config.get("Country", "")
        env     = self._config.get("Environment", "")
        title   = settings.PR_TITLE_TEMPLATE.format(country=country, environment=env)
        body    = build_pr_body(self._config)

        self._pr_preview.config(state="normal")
        self._pr_preview.delete("1.0", "end")
        self._pr_preview.insert("end", f"TITLE:\n{title}\n\n{'─'*40}\n\nBODY:\n{body}")
        self._pr_preview.config(state="disabled")

    def _update_header(self, country: str, env: str):
        self._header_label.config(text=f"{country}  ›  {env.upper()}")
        color = ENV_COLORS.get(env.lower(), ACCENT)
        self._env_badge.config(
            text=env.upper(), bg=color, fg=WHITE
        )

    def _clear_preview(self):
        for row in self._tree.get_children():
            self._tree.delete(row)
        self._pr_preview.config(state="normal")
        self._pr_preview.delete("1.0", "end")
        self._pr_preview.config(state="disabled")
        self._header_label.config(text="Select a country and environment to begin")
        self._env_badge.config(text="", bg=CARD)
        self._config = None

    def _set_status(self, msg: str):
        self._status_var.set(msg)

    # ── PR Creation ───────────────────────────────────────────────────────────

    def _create_pr(self):
        if not self._config:
            return

        token = self._token_var.get().strip()
        owner = self._owner_var.get().strip()
        repo  = self._repo_var.get().strip()

        if not token or token.startswith("ghp_YOUR"):
            messagebox.showerror("Missing Token", "Please enter a valid GitHub Personal Access Token.")
            return
        if not owner or not repo:
            messagebox.showerror("Missing Repo", "Please enter the GitHub owner and repository name.")
            return

        country = self._config.get("Country", "")
        env     = self._config.get("Environment", "")
        branch  = self._config.get("BRANCH_NAME") or f"feature/{country.lower()}-{env.lower()}-config"
        title   = settings.PR_TITLE_TEMPLATE.format(country=country, environment=env)
        body    = build_pr_body(self._config)

        self._pr_btn.config(state="disabled", text="⏳  Creating PR…")
        self._set_status("Creating Pull Request on GitHub…")

        def worker():
            creator = GitHubPRCreator(token, owner, repo)
            result  = creator.create_pr(
                title=title,
                body=body,
                head_branch=branch,
                base_branch="main",
                labels=settings.DEFAULT_LABELS,
            )
            self.after(0, lambda: self._on_pr_done(result))

        threading.Thread(target=worker, daemon=True).start()

    def _on_pr_done(self, result):
        self._pr_btn.config(state="normal", text="🚀  Create Pull Request")
        if result.success:
            self._set_status(f"✅  PR #{result.pr_number} created successfully!")
            answer = messagebox.askyesno(
                "Pull Request Created",
                f"✅ PR #{result.pr_number} was created successfully!\n\n"
                f"URL: {result.pr_url}\n\nOpen in browser?",
            )
            if answer:
                import webbrowser
                webbrowser.open(result.pr_url)
        else:
            self._set_status(f"❌  PR creation failed: {result.error}")
            messagebox.showerror("PR Creation Failed", result.error)


if __name__ == "__main__":
    app = PRConfigApp()
    app.mainloop()
