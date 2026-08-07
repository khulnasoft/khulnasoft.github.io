"""SDK generator: emits minimal client stubs from the canonical resource schema.

Generates a small typed client in each target language exposing the agent-friendly
API surface (resources, twins, context, recommendations, graph, impact, events,
analytics, release) so the platform is consumable via SDKs as well as HTTP/MCP.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SDK_DIR = ROOT / "site" / "sdks"

ENDPOINTS = [
    ("resources", None, "/resources"),
    ("resource", "slug", "/resources/{slug}"),
    ("twin", "slug", "/resources/{slug}/twin"),
    ("context", "slug", "/resources/{slug}/context"),
    ("recommendations", "slug", "/resources/{slug}/recommendations"),
    ("graph", None, "/graph"),
    ("impact", None, "/impact"),
    ("events", None, "/events"),
    ("analytics", None, "/analytics"),
    ("release", None, "/release"),
]


def gen_python() -> str:
    lines = [
        '"""KhulnaSoft AEC SDK (generated). Do not hand-edit."""',
        "",
        "from typing import Any",
        "",
        "",
        "class Client:",
        '    """Minimal typed client for the KhulnaSoft AI-Native Engineering Cloud."""',
        "",
    ]
    for func, param, path in ENDPOINTS:
        args = f"{param}: str" if param else ""
        lines.append(f"    def {func}(self, {args}) -> dict:" if param
                     else f"    def {func}(self) -> dict:")
        if param:
            lines.append(f"        path = {path!r}.replace( '{{slug}}', {param} )")
        else:
            lines.append(f"        path = {path!r}")
        lines.append('        return self.request("GET", path)')
        lines.append("")
    lines += [
        "    def request(self, method, path):",
        '        """HTTP helper (swap with an httpx/requests transport)."""',
        '        return {"path": path, "method": method}',
    ]
    return "\n".join(lines) + "\n"


def gen_typescript() -> str:
    import json
    lines = [
        "// KhulnaSoft AEC SDK (generated). Do not hand-edit.",
        "export class AecClient {",
        "  base = \"https://khulnasoft.github.io/api\";",
        "",
    ]
    for func, param, path in ENDPOINTS:
        if param:
            ts_path = path.replace("{slug}", "${" + param + "}")
            sig = f"({param}: string)"
        else:
            ts_path = path
            sig = "()"
        if "{" in ts_path or param:
            expr = f"this.base + `{ts_path}`"
        else:
            expr = f"this.base + {json.dumps(ts_path)}"
        lines.append(f"  {func}{sig} = fetch({expr}).then(r => r.json());")
    lines.append("}")
    return "\n".join(lines) + "\n"


def generate_sdks() -> list[dict]:
    """Emit all client stubs and return metadata describing them."""
    SDK_DIR.mkdir(parents=True, exist_ok=True)
    artifacts = [
        {"language": "python", "path": "sdks/aec.py", "content": gen_python()},
        {"language": "typescript", "path": "sdks/aec.ts", "content": gen_typescript()},
    ]
    for art in artifacts:
        (SDK_DIR / art["path"].split("/")[-1]).write_text(art["content"], encoding="utf-8")
    return [
        {"language": a["language"], "file": a["path"], "lines": a["content"].count("\n")}
        for a in artifacts
    ]