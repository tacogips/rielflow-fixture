#!/usr/bin/env python3
import fnmatch
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

TEXT_EXTENSIONS = {
    ".bash",
    ".json",
    ".md",
    ".sh",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
    ".zsh",
}

URL_PATTERN = re.compile(r"https?://[A-Za-z0-9._~:/?#@!$&'()*+,;=%-]+")
SHELL_EGRESS_PATTERN = re.compile(
    r"\b(curl|wget|nc|netcat)\b[^\n\r]{0,240}", re.IGNORECASE
)


def load_allowlist(path: Path) -> list[str]:
    entries: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        entries.append(line.lower())
    return entries


def host_allowed(host: str, allowlist: list[str]) -> bool:
    normalized = host.lower().rstrip(".")
    for pattern in allowlist:
        if pattern.startswith("*."):
            suffix = pattern[1:]
            if normalized.endswith(suffix) and normalized != suffix[1:]:
                return True
        elif fnmatch.fnmatchcase(normalized, pattern):
            return True
    return False


def iter_text_files(root: Path):
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if ".git" in file_path.parts or "node_modules" in file_path.parts:
            continue
        if file_path.suffix.lower() in TEXT_EXTENSIONS:
            yield file_path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "/package")
    default_allowlist = Path("/opt/rielflow-sandbox/allowlist.txt")
    local_allowlist = Path(__file__).resolve().parents[1] / "allowlist.txt"
    allowlist_file = Path(
        os.environ.get(
            "RIELFLOW_VENDOR_ALLOWLIST",
            str(default_allowlist if default_allowlist.exists() else local_allowlist),
        )
    )
    allowlist = load_allowlist(allowlist_file)
    findings: list[str] = []

    for file_path in iter_text_files(root):
        relative = file_path.relative_to(root)
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match in URL_PATTERN.finditer(content):
            parsed = urlparse(match.group(0))
            host = parsed.hostname
            if host and not host_allowed(host, allowlist):
                findings.append(f"{relative}: disallowed URL host {host}")
        for match in SHELL_EGRESS_PATTERN.finditer(content):
            command = match.group(0)
            for url_match in URL_PATTERN.finditer(command):
                parsed = urlparse(url_match.group(0))
                host = parsed.hostname
                if host and not host_allowed(host, allowlist):
                    findings.append(f"{relative}: disallowed shell egress host {host}")

    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        return 2
    print("rielflow sandbox check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
