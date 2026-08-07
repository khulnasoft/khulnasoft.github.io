"""SDK generator: emits minimal client stubs from the canonical resource schema.

Generates a small typed client in each target language exposing the agent-friendly
API surface (resources, twins, context, recommendations, graph, impact, events,
analytics, release) so the platform is consumable via SDKs as well as HTTP/MCP.
"""
from __future__ import annotations

import json
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

# Actions exposed by the agent-facing MCP/SDK surfaces (Phase 9.4/10.4).
# These are write operations, so they POST to the runtime plane.
ACTIONS = [
    ("install_asset", "asset_id", "/marketplace/install"),
    ("consume_artifact", "asset_id", "/marketplace"),
    ("route_event", "payload", "/webhook/ingest"),
]

BRAND = "KhulnaSoft Engineering Knowledge OS"


def gen_python() -> str:
    lines = [
        f'"""{BRAND} SDK (generated). Do not hand-edit."""',
        "",
        "from typing import Any",
        "",
        "",
        "class Client:",
        f'    """Minimal typed client for the {BRAND}."""',
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
    # Agent-facing marketplace install/consume actions (Phase 9.4/10.4).
    lines.append("    def install_asset(self, asset_id: str) -> dict:")
    lines.append('        """Install a reusable marketplace asset (template, prompt pack, policy, agent)."""')
    lines.append('        return self.request("POST", "/marketplace/install", {"id": asset_id})')
    lines.append("")
    lines.append("    def consume_artifact(self, asset_id: str) -> dict:")
    lines.append('        """Fetch the artifact resolved from an installed marketplace asset."""')
    lines.append('        return self.request("GET", "/marketplace?asset=" + asset_id)')
    lines.append("")
    lines += [
        "    def request(self, method, path, body=None):",
        '        """HTTP helper (swap with an httpx/requests transport)."""',
        '        return {"path": path, "method": method, "body": body}',
    ]
    return "\n".join(lines) + "\n"


def gen_typescript() -> str:
    lines = [
        f"// {BRAND} SDK (generated). Do not hand-edit.",
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
    # Agent-facing marketplace install/consume actions (Phase 9.4/10.4).
    lines.append("""  /** Install a reusable marketplace asset (template, prompt pack, policy, agent). */""")
    lines.append("  installAsset = (assetId: string) =>")
    lines.append("    fetch(this.base + '/marketplace/install', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id: assetId})}).then(r => r.json());")
    lines.append("  /** Fetch the artifact resolved from an installed marketplace asset. */")
    lines.append("  consumeArtifact = (assetId: string) =>")
    lines.append("    fetch(this.base + '/marketplace?asset=' + assetId).then(r => r.json());")
    lines.append("}")
    return "\n".join(lines) + "\n"


def gen_go() -> str:
    lines = [
        f"// Package khulnasoft is a minimal client for the {BRAND}.",
        "// Generated. Do not hand-edit.",
        "package khulnasoft",
        "",
        "import (",
        '\t"fmt"',
        '\t"net/http"',
        '\t"strings"',
        ")",
        "",
        "const BaseURL = \"https://khulnasoft.github.io/api\"",
        "",
        "type Client struct { HTTP *http.Client }",
        "",
    ]
    for func, param, path in ENDPOINTS:
        if param:
            lines.append(f"// {func} returns the resource identified by slug.")
            lines.append(f"func (c *Client) {func.capitalize()}(slug string) (*http.Response, error) {{")
            lines.append(f"\treturn c.HTTP.Get(fmt.Sprintf(\"%s{path.replace('{slug}', '%s')}\", BaseURL, slug))")
        else:
            lines.append(f"// {func} returns the API payload.")
            lines.append(f"func (c *Client) {func.capitalize()}() (*http.Response, error) {{")
            lines.append(f'\treturn c.HTTP.Get(BaseURL + "{path}")')
        lines.append("}")
        lines.append("")
    # Agent-facing marketplace install/consume actions (Phase 9.4/10.4).
    lines.append("// InstallAsset installs a reusable marketplace asset.")
    lines.append("func (c *Client) InstallAsset(assetID string) (*http.Response, error) {")
    lines.append('\treq, _ := http.NewRequest("POST", BaseURL+"/marketplace/install", strings.NewReader(`{"id":"`+assetID+`"}`))')
    lines.append('\treq.Header.Set("Content-Type", "application/json")')
    lines.append("\treturn c.HTTP.Do(req)")
    lines.append("}")
    lines.append("")
    lines.append("// ConsumeArtifact fetches the artifact resolved from an installed asset.")
    lines.append('func (c *Client) ConsumeArtifact(assetID string) (*http.Response, error) {')
    lines.append('\treturn c.HTTP.Get(BaseURL + "/marketplace?asset=" + assetID)')
    lines.append("}")
    lines.append("")
    return "\n".join(lines) + "\n"


def gen_rust() -> str:
    lines = [
        f"//! {BRAND} SDK (generated). Do not hand-edit.",
        "",
        "const BASE: &str = \"https://khulnasoft.github.io/api\";",
        "",
        "pub struct Client;",
        "",
    ]
    for func, param, path in ENDPOINTS:
        if param:
            # Replace the {slug} token with a positional {} so BASE and slug
            # are passed as args, preserving any surrounding path segments.
            fmt = "{}/" + path.lstrip("/").replace("{slug}", "{}")
            lines.append(f"pub fn {func}(slug: &str) -> String {{")
            lines.append(f'    format!("{fmt}", BASE, slug)')
        else:
            lines.append(f"pub fn {func}() -> String {{")
            lines.append(f'    format!("{{}}{path}", BASE)')
        lines.append("}")
        lines.append("")
    return "\n".join(lines) + "\n"


def gen_java() -> str:
    lines = [
        f"// {BRAND} SDK (generated). Do not hand-edit.",
        "package io.khulnasoft;",
        "",
        "public final class AecClient {",
        "    private static final String BASE = \"https://khulnasoft.github.io/api\";",
        "",
    ]
    for func, param, path in ENDPOINTS:
        if param:
            lines.append(f"    public static String {func}(String slug) {{")
            lines.append(f'        return BASE + "{path}".replace("{{slug}}", slug);')
        else:
            lines.append(f"    public static String {func}() {{")
            lines.append(f'        return BASE + "{path}";')
        lines.append("    }")
        lines.append("")
    # Agent-facing marketplace install/consume actions (Phase 9.4/10.4).
    lines.append("    // Install a reusable marketplace asset (template, prompt pack, policy, agent).")
    lines.append("    public static String installAsset(String assetId) {")
    lines.append('        return BASE + "/marketplace/install";')
    lines.append("    }")
    lines.append("")
    lines.append("    // Fetch the artifact resolved from an installed marketplace asset.")
    lines.append("    public static String consumeArtifact(String assetId) {")
    lines.append('        return BASE + "/marketplace?asset=" + assetId;')
    lines.append("    }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def gen_csharp() -> str:
    lines = [
        f"// {BRAND} SDK (generated). Do not hand-edit.",
        "namespace KhulnaSoft;",
        "",
        "public static class AecClient",
        "{",
        '    private const string Base = "https://khulnasoft.github.io/api";',
        "",
    ]
    for func, param, path in ENDPOINTS:
        if param:
            lines.append(f"    public static string {func.capitalize()}(string slug) {{")
            lines.append(f'        return Base + "{path}".Replace("{{slug}}", slug);')
        else:
            lines.append(f"    public static string {func.capitalize()}() {{")
            lines.append(f'        return Base + "{path}";')
        lines.append("    }")
        lines.append("")
    lines.append("}")
    return "\n".join(lines) + "\n"


def gen_php() -> str:
    lines = [
        f"<?php",
        f"// {BRAND} SDK (generated). Do not hand-edit.",
        "",
        "final class AecClient",
        "{",
        "    private const BASE = 'https://khulnasoft.github.io/api';",
        "",
    ]
    for func, param, path in ENDPOINTS:
        if param:
            lines.append(f"    public static function {func}(string $slug): string")
            lines.append("    {")
            lines.append(f"        return self::BASE . str_replace('{{slug}}', $slug, '{path}');")
            lines.append("    }")
        else:
            lines.append(f"    public static function {func}(): string")
            lines.append("    {")
            lines.append(f"        return self::BASE . '{path}';")
            lines.append("    }")
        lines.append("")
    lines.append("}")
    return "\n".join(lines) + "\n"


def gen_ruby() -> str:
    lines = [
        f"# {BRAND} SDK (generated). Do not hand-edit.",
        "",
        "module KhulnaSoft",
        "  BASE = 'https://khulnasoft.github.io/api'.freeze",
        "",
        "  module_function",
        "",
    ]
    for func, param, path in ENDPOINTS:
        if param:
            lines.append(f"  def {func}(slug)")
            lines.append(f"    BASE + '{path}'.gsub('{{slug}}', slug)")
            lines.append("  end")
        else:
            lines.append(f"  def {func}")
            lines.append(f"    BASE + '{path}'")
            lines.append("  end")
        lines.append("")
    lines.append("end")
    return "\n".join(lines) + "\n"


def gen_swift() -> str:
    lines = [
        f"// {BRAND} SDK (generated). Do not hand-edit.",
        "",
        "public enum AecClient {",
        '    public static let base = "https://khulnasoft.github.io/api"',
        "",
    ]
    for func, param, path in ENDPOINTS:
        if param:
            lines.append(f"    public static func {func}(slug: String) -> String {{")
            lines.append(f'        base + "{path}".replacingOccurrences(of: "{{slug}}", with: slug)')
            lines.append("    }")
        else:
            lines.append(f"    public static func {func}() -> String {{")
            lines.append(f'        base + "{path}"')
            lines.append("    }")
        lines.append("")
    lines.append("}")
    return "\n".join(lines) + "\n"


def gen_kotlin() -> str:
    lines = [
        f"// {BRAND} SDK (generated). Do not hand-edit.",
        "",
        "package io.khulnasoft",
        "",
        "object AecClient {",
        "    const val BASE = \"https://khulnasoft.github.io/api\"",
        "",
    ]
    for func, param, path in ENDPOINTS:
        if param:
            lines.append(f"    fun {func}(slug: String): String =")
            lines.append(f'        BASE + "{path}".replace("{{slug}}", slug)')
        else:
            lines.append(f"    fun {func}(): String = BASE + \"{path}\"")
        lines.append("")
    lines.append("}")
    return "\n".join(lines) + "\n"


def gen_dart() -> str:
    lines = [
        f"// {BRAND} SDK (generated). Do not hand-edit.",
        "",
        "class AecClient {",
        '  static const String base = "https://khulnasoft.github.io/api";',
        "",
    ]
    for func, param, path in ENDPOINTS:
        if param:
            lines.append(f"  static String {func}(String slug) {{")
            lines.append(f'    return base + "{path}".replaceAll("{{slug}}", slug);')
            lines.append("  }")
        else:
            lines.append(f"  static String {func}() => base + \"{path}\";")
        lines.append("")
    lines.append("}")
    return "\n".join(lines) + "\n"


GENERATORS = {
    "python": ("aec.py", gen_python),
    "typescript": ("aec.ts", gen_typescript),
    "go": ("aec.go", gen_go),
    "rust": ("aec.rs", gen_rust),
    "java": ("AecClient.java", gen_java),
    "csharp": ("AecClient.cs", gen_csharp),
    "php": ("aec.php", gen_php),
    "ruby": ("aec.rb", gen_ruby),
    "swift": ("AecClient.swift", gen_swift),
    "kotlin": ("AecClient.kt", gen_kotlin),
    "dart": ("aec.dart", gen_dart),
}


def generate_sdks() -> list[dict]:
    """Emit all client stubs and return metadata describing them."""
    SDK_DIR.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for language, (filename, gen) in GENERATORS.items():
        content = gen()
        (SDK_DIR / filename).write_text(content, encoding="utf-8")
        artifacts.append({
            "language": language,
            "path": f"sdks/{filename}",
            "lines": content.count("\n"),
        })
    return artifacts
