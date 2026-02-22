"""
pr_creator.py
Creates GitHub Pull Requests using the GitHub REST API (no third-party SDK needed).
"""

import json
import urllib.request
import urllib.error
from dataclasses import dataclass


@dataclass
class PRResult:
    success: bool
    pr_url: str = ""
    pr_number: int = 0
    error: str = ""


class GitHubPRCreator:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo

    def _request(self, method: str, endpoint: str, body: dict = None) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        data = json.dumps(body).encode() if body else None

        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
                "User-Agent": "PR-Config-Tool/1.0",
            },
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def get_default_branch(self) -> str:
        data = self._request("GET", f"/repos/{self.owner}/{self.repo}")
        return data.get("default_branch", "main")

    def branch_exists(self, branch: str) -> bool:
        try:
            self._request("GET", f"/repos/{self.owner}/{self.repo}/branches/{branch}")
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            raise

    def create_branch(self, new_branch: str, base_branch: str):
        ref_data = self._request(
            "GET", f"/repos/{self.owner}/{self.repo}/git/ref/heads/{base_branch}"
        )
        sha = ref_data["object"]["sha"]
        self._request(
            "POST",
            f"/repos/{self.owner}/{self.repo}/git/refs",
            {"ref": f"refs/heads/{new_branch}", "sha": sha},
        )

    def update_or_create_file(
        self,
        branch: str,
        file_path: str,
        content: str,
        commit_message: str,
    ):
        import base64

        encoded = base64.b64encode(content.encode()).decode()
        endpoint = f"/repos/{self.owner}/{self.repo}/contents/{file_path}"

        # Get existing SHA if file exists
        sha = None
        try:
            existing = self._request("GET", f"{endpoint}?ref={branch}")
            sha = existing.get("sha")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise

        payload = {
            "message": commit_message,
            "content": encoded,
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha

        self._request("PUT", endpoint, payload)

    def create_pr(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
        labels: list[str] = None,
    ) -> PRResult:
        try:
            # Ensure base branch exists
            default_branch = self.get_default_branch()
            actual_base = base_branch if self.branch_exists(base_branch) else default_branch

            # Create feature branch if it doesn't exist
            if not self.branch_exists(head_branch):
                self.create_branch(head_branch, actual_base)

            # Write config file to the branch
            config_content = f"# Auto-generated config\n# Title: {title}\n\n{body}"
            self.update_or_create_file(
                branch=head_branch,
                file_path=f"configs/{head_branch.replace('/', '_')}.md",
                content=config_content,
                commit_message=f"chore: add config for {title}",
            )

            # Open the PR
            payload = {
                "title": title,
                "body": body,
                "head": head_branch,
                "base": actual_base,
                "draft": False,
            }
            pr_data = self._request(
                "POST",
                f"/repos/{self.owner}/{self.repo}/pulls",
                payload,
            )

            # Apply labels if any
            if labels:
                self._request(
                    "POST",
                    f"/repos/{self.owner}/{self.repo}/issues/{pr_data['number']}/labels",
                    {"labels": labels},
                )

            return PRResult(
                success=True,
                pr_url=pr_data["html_url"],
                pr_number=pr_data["number"],
            )

        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            try:
                msg = json.loads(error_body).get("message", error_body)
            except Exception:
                msg = error_body
            return PRResult(success=False, error=f"GitHub API error {e.code}: {msg}")
        except Exception as e:
            return PRResult(success=False, error=str(e))


def build_pr_body(config: dict) -> str:
    """Formats the Excel config row into a nice PR description."""
    skip = {"Country", "Environment", "BRANCH_NAME"}
    rows = "\n".join(
        f"| `{k}` | `{v}` |"
        for k, v in config.items()
        if k not in skip and v is not None
    )
    country = config.get("Country", "")
    environment = config.get("Environment", "")

    return f"""## 🌍 Configuration Update — {country} / {environment.upper()}

This PR was auto-generated by the **PR Config Tool**.

### 📋 Configuration Values

| Key | Value |
|-----|-------|
{rows}

---
> **Country**: `{country}` | **Environment**: `{environment}` | **Auto-generated**: ✅
"""
