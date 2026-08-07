"""Experience-plane static portal renderer.

Every page is generated from canonical model state so the portal reflects the
registry/twins rather than hand-authored content.
"""
from __future__ import annotations

CSS = """*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
background:#07111f;color:#f5f7fb;line-height:1.5}
a{color:#58c6dd}a:hover{text-decoration:underline}
header.top{border-bottom:1px solid #1f3040;padding:.85rem 1.4rem;display:flex;align-items:center;gap:1rem;
position:sticky;top:0;background:rgba(7,17,31,.95)}
header.top .brand{font-weight:700;letter-spacing:.2px}
header.top .accent{color:#58c6dd}
header.top nav{margin-left:auto;display:flex;flex-wrap:wrap;gap:.2rem}
header.top nav a{color:#93a7bd;text-decoration:none;padding:.3rem .55rem;border-radius:8px;font-size:.82rem}
header.top nav a:hover{color:#f5f7fb;background:#1f2f40}
main{max-width:1140px;margin:0 auto;padding:1.6rem}
h1{letter-spacing:-.03em;font-size:1.8rem}
h2{color:#58c6dd;font-size:1.15rem;margin:1.5rem 0 .6rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1rem}
.card{background:#10202f;border:1px solid #1f3244;border-radius:12px;padding:1rem 1.1rem}
.card.metric{text-align:center}
.metric .value{font-size:1.9rem;font-weight:800;color:#58c6dd}
.metric .label{color:#93a7bd;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em}
.pill{display:inline-block;background:#14324f;color:#58c6dd;padding:.18rem .6rem;border-radius:999px;font-size:.75rem;margin:.15rem .25rem .15rem 0}
.pill.kind{background:#14314a;color:#c5d5e8}
.muted{color:#93a7bd}
code{background:#0d1a28;padding:.1rem .35rem;border-radius:5px;font-size:.85rem}
ul.plain{list-style:none;padding:0;margin:0}
ul.plain li{padding:.42rem 0;border-bottom:1px solid #1f3244}
ul.plain li:last-child{border-bottom:none}
table{width:100%;border-collapse:collapse}
th{text-align:left;color:#93a7bd;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;padding:.4rem}
td{padding:.45rem;border-top:1px solid #1f3244}
.footer{border-top:1px solid #1f3244;margin-top:2rem;padding:1rem 1.4rem;color:#93a7bd;font-size:.8rem;display:flex;flex-wrap:wrap;gap:1rem}
.badge{display:inline-block;padding:.12rem .5rem;border-radius:999px;font-size:.7rem;font-weight:600}
.badge.ok{background:rgba(74,222,128,.16);color:#4ade80}
.badge.warn{background:rgba(251,191,36,.16);color:#fbbf24}
.badge.bad{background:rgba(248,113,113,.16);color:#f87171}
"""

NAV = [
    ("Index", "index.html"), ("Resources", "catalog.html"), ("Search", "search.html"),
    ("Graph", "graph.html"), ("Digital Twins", "digital-twin.html"), ("Context", "context-fabric.html"),
    ("Registries", "registries.html"), ("Readiness", "readiness.html"), ("AI Plane", "ai-control-plane.html"),
    ("Control Plane", "control-plane.html"), ("Organization", "organizations.html"),
    ("Platform", "platform-overview.html"), ("Dashboard", "exec-dashboard.html"),
    ("Docs", "docs/architecture.html"), ("API", "api.html"),
]


def health_badge(status):
    cls = {"healthy": "ok", "degraded": "warn", "warning": "warn", "error": "bad", "critical": "bad"}.get(status, "ok")
    return f'<span class="badge {cls}">{status}</span>'


def shell(title, body):
    nav = "".join(f'<a href="{href}">{label}</a>' for label, href in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · KhulnaSoft AEC</title><style>{CSS}</style></head>
<body>
<header class="top"><div class="brand">KhulnaSoft <span class="accent">AEC</span></div><nav>{nav}</nav></header>
<main>{body}</main>
<footer class="footer"><span>KhulnaSoft AI-Native Engineering Cloud</span>
<a href="llms.txt">llms.txt</a><a href="llms-full.txt">llms-full.txt</a><a href="mcp.json">MCP</a>
<a href="manifests.json">manifests</a><a href="graph-data.json">graph</a><a href="search-index.json">search</a></footer>
</body></html>"""


def render_index(resources, metrics):
    cards = ""
    for r in resources:
        cards += f"""<div class="card"><div style="display:flex;justify-content:space-between;align-items:center">
<a href="resources/{r['slug']}.html" style="font-weight:700;font-size:1.05rem">{r['name']}</a>{health_badge(r['health']['status'])}</div>
<div class="muted" style="margin:.25rem 0"><span class="pill kind">{r['kind']}</span><span class="pill">{r.get('workspace','core')}</span></div>
<div class="muted">{r['summary']}</div>
<div style="margin-top:.6rem"><a href="context/{r['slug']}.json">bundle</a> · <a href="twins/{r['slug']}.json">twin</a></div></div>"""
    body = f"""<h1>KhulnaSoft AI-Native Engineering Cloud</h1>
<p class="muted">A continuously updated control plane for engineering assets, AI-ready context, and agent-friendly APIs.</p>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
"""+("".join(f'<div class="card metric"><div class="value">{metrics[k]}</div><div class="label">{k.replace("_"," ")}</div></div>' for k, v in metrics.items()))+f"""</div>
<h2>Resources</h2><div class="grid">{cards}</div>"""
    return shell("Platform", body)


def render_resource(r, readiness, recommendations, graph):
    caps = "".join(f'<span class="pill">{c}</span>' for c in r.get("capabilities", [])) or "<span class='muted'>none</span>"
    rels = "".join(
        f'<li>{rel.get("type","related")} → <code>{rel.get("target")}</code>{(" · "+rel["detail"]) if rel.get("detail") else ""}</li>'
        for rel in r.get("relationships", [])
    ) or "<li class='muted'>No declared relationships.</li>"
    recs = "".join(f"<li>{a}</li>" for a in recommendations) or "<li class='muted'>No recommended actions.</li>"
    syn = "<span class='muted'>No layered context.</span>"
    meters = "".join(
        f"""<div style="display:flex;align-items:center;gap:.6rem;margin:.25rem 0">
<span style="width:110px" class="muted">{dim.replace('_',' ')}</span>
<div style="flex:1;background:#0d1a28;border-radius:6px;height:8px">
<div style="width:{val}%;background:#58c6dd;height:8px;border-radius:6px"></div></div><span>{val}</span></div>"""
        for dim, val in sorted(readiness.get("scores", {}).items())
    )
    body = f"""<p class="muted"><a href="catalog.html">← Catalog</a></p>
<h1>{r['name']} {health_badge(r['health']['status'])}</h1>
<p class="muted">{r['summary']}</p>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">
<div class="card"><strong>{r['kind']}</strong><br/><span class="muted">kind</span></div>
<div class="card"><strong>{r.get('owner')}</strong><br/><span class="muted">owner · {r.get('team')}</span></div>
<div class="card"><strong>{r.get('workspace')}</strong><br/><span class="muted">workspace</span></div>
<div class="card"><strong>{r['health']['score']}/100</strong><br/><span class="muted">health</span></div>
<div class="card"><strong>{readiness.get('overall')} · {readiness.get('level')}</strong><br/><span class="muted">readiness</span></div>
</div>
<h2>Capabilities</h2><div>{caps}</div>
<h2>Relationships</h2><ul class="plain">{rels}</ul>
<h2>Context (selective)</h2>
<p class="muted">{syn}</p>
<p><a href="context/{r['slug']}.json">full context bundle</a> · <a href="twins/{r['slug']}.json">digital twin</a></p>
<h2>Readiness</h2><div class="card">{meters}</div>
<h2>Recommended actions</h2><ul class="plain">{recs}</ul>
<h2>Digital twin</h2>
<div class="card"><span class="muted">status</span> <code>{r.get('status')}</code> ·
<span class="muted">lifecycle</span> <code>{r.get('lifecycle')}</code> ·
<span class="muted">visibility</span> <code>{r.get('visibility')}</code>
<a href="twins/{r['slug']}.json" style="margin-left:.5rem">open twin</a></div>"""
    return shell(f"{r['name']} · Resource", body)


def render_catalog(resources):
    rows = ""
    for r in resources:
        rows += f"""<tr><td><a href="resources/{r['slug']}.html">{r['name']}</a></td>
<td><span class="pill kind">{r['kind']}</span></td><td>{r.get('workspace')}</td><td>{r.get('owner')}</td>
<td>{health_badge(r['health']['status'])}</td><td>{r['health']['score']}</td>
<td>{' '.join(r.get('capabilities', [])[:3])}</td></tr>"""
    body = f"""<h1>Resource Catalog</h1>
<p class="muted">Every ecosystem asset as a first-class resource, with filtering-friendly facets.</p>
<div class="card"><table><thead><tr><th>Name</th><th>Kind</th><th>Workspace</th><th>Owner</th><th>Health</th><th>Score</th><th>Capabilities</th></tr></thead>
<tbody>{rows}</tbody></table></div>"""
    return shell("Catalog", body)


def render_graph(graph):
    body = """<h1>Relationship Graph</h1>
<p class="muted">Derived from resource relationships — nodes and edges are generated, never hand-edited. Machine-readable copy: <code>graph-data.json</code>.</p>
<div class="card"><pre style="white-space:pre" id="g"></pre></div>
<script>
fetch('graph-data.json').then(r=>r.json()).then(g=>{
const byId=Object.fromEntries(g.nodes.map(n=>[n.id,n.label]));
const nodes=g.nodes.map(n=>`${n.label} (${n.kind})`);
const edges=g.edges.map(e=>`${byId[e.from]||e.from} → ${byId[e.to]||e.to} [${e.type}]`);
document.getElementById('g').textContent='NODES\n'+nodes.join('\n')+'\n\nEDGES\n'+edges.join('\n');
});
</script>"""
    return shell("Relationship Graph", body)


def render_digital_twins(resources, twins):
    cards = ""
    for r in resources:
        t = twins[r["id"]]
        cards += f"""<div class="card"><div style="display:flex;justify-content:space-between">
<a style="font-weight:700" href="resources/{r['slug']}.html">{r['name']}</a>{health_badge(t['health']['status'])}</div>
<div class="muted" style="margin:.25rem 0"><span class="pill kind">{t['resource']['kind']}</span>{t['resource']['workspace']}</div>
<div class="muted">{t['resource']['summary']}</div>
<div class="muted" style="margin:.45rem 0">health <code>{t['health']['score']}</code> · readiness <code>{t['readiness'].get('overall')}</code> · lifecycle <code>{t['resource']['lifecycle']}</code></div>
<a href="twins/{r['slug']}.json">open twin</a></div>"""
    body = f"""<h1>Engineering Digital Twins</h1>
<p class="muted">Each twin is the canonical, continuously updated representation of a resource: metadata, source state, readiness, dependencies, and AI context in one place.</p>
<div class="grid">{cards}</div>"""
    return shell("Digital Twins", body)


def render_context_fabric(resources, layers):
    pill = "".join(f'<span class="pill">{l}</span>' for l in layers)
    cards = ""
    for r in resources:
        cards += f"""<div class="card"><a style="font-weight:700" href="resources/{r['slug']}.html">{r['name']}</a>
<div class="muted" style="margin:.3rem 0">{r['summary']}</div>
<a href="context/{r['slug']}.json">full bundle</a></div>"""
    body = f"""<h1>Context Fabric</h1>
<p class="muted">AI-ready context composed by layer: {pill}. Context supports selective retrieval so agents fetch only the layers they need. Published as <code>llms.txt</code>, <code>llms-full.txt</code>, and MCP metadata.</p>
<div class="grid">{cards}</div>"""
    return shell("Context Fabric", body)


def render_registries(reg):
    body = "<h1>Control-plane Registries</h1>"
    body += "<h2>Capability Registry</h2><ul class='plain'>" + "".join(
        f"<li><code>{cap}</code> — {v['count']} resource(s)</li>" for cap, v in list(reg["capability"]["capabilities"].items())[:25]
    ) + "</ul>"
    body += "<h2>Platform Registry (by kind)</h2><ul class='plain'>" + "".join(
        f"<li><strong>{k}</strong> — {v['count']} object(s)</li>" for k, v in reg["platform"]["kinds"].items()
    ) + "</ul>"
    body += "<h2>Kind Taxonomy</h2><ul class='plain'>" + "".join(
        f"<li><strong>{k}</strong> — {v}</li>" for k, v in reg["kind"]["coverage"].items()
    ) + "</ul>"
    body += "<h2>Service Registry</h2><ul class='plain'>" + "".join(
        f"<li><strong>{s['name']}</strong> ({s['kind']}) <span class='muted'>· {s['workspace']}</span></li>" for s in reg["service"]["services"]
    ) + "</ul>"
    body += "<h2>Context Registry</h2><ul class='plain'>" + "".join(
        f"<li><strong>{r['name']}</strong> <code>{r['slug']}</code></li>" for r in reg["context"]["resources"]
    ) + "</ul>"
    return shell("Registries", body)


def render_readiness(insights, resources):
    dist = "".join(f'<span class="pill">{lvl}: {cnt}</span>' for lvl, cnt in insights["distribution"].items())
    cards = ""
    for r in resources:
        per = insights["per_resource"].get(r["id"], {})
        cards += f"""<div class="card"><div style="display:flex;justify-content:space-between">
<a style="font-weight:700" href="resources/{r['slug']}.html">{r['name']}</a><strong>{per.get('overall', '-')}</strong></div>
<div class="muted">level: {per.get('level', '?')}</div>
<div style="background:#0d1a28;border-radius:6px;height:8px;margin-top:.4rem">
<div style="width:{per.get('overall', 0)}%;background:#58c6dd;height:8px;border-radius:6px"></div></div></div>"""
    body = f"""<h1>Fleet Readiness</h1>
<p class="muted">Readiness is derived per resource from manifest signals and health. {dist}</p>
<div class="grid">{cards}</div>"""
    return shell("Readiness", body)


def render_ai_control_plane(reg, layers):
    body = f"""<h1>AI Control Plane</h1>
<p class="muted">Prompt registry, context registry, agent registry, and AI-safe metadata for agents and automation.</p>
<h2>Context Registry ({reg['context']['count']})</h2><ul class="plain">
{''.join(f'<li><strong>{r["name"]}</strong> <code>{r["slug"]}</code></li>' for r in reg['context']['resources'])}</ul>
<h2>Prompt Registry ({reg['prompt']['count']})</h2><ul class="plain">
{''.join(f'<li><strong>{p["id"]}</strong><br/><span class="muted">{p["body"]}</span></li>' for p in reg['prompt']['prompts'])}</ul>
<h2>Agent Registry ({reg['agent']['count']})</h2><ul class="plain">
{''.join(f'<li><strong>{a["name"]}</strong> — {a["description"]} <span class="muted">[{", ".join(a["capabilities"])}]</span></li>' for a in reg['agent']['agents'])}</ul>
<h2>Context layers</h2><p>{''.join(f'<span class="pill">{l}</span>' for l in layers)}</p>"""
    return shell("AI Control Plane", body)


def render_control_plane(org):
    gov = org["governance"]
    roles = "".join(f'<span class="pill">{r}</span>' for r in gov["rbacRoles"])
    policies = "".join(
        f'<li><strong>{p["name"]}</strong> ({p["check"]}) — {", ".join(p["requiredSignals"])}</li>' for p in gov["policies"]
    )
    approvals = "".join(
        f'<li><strong>{a["name"]}</strong> — required {a["required"]}, enforced {a["enforced"]}</li>' for a in gov["approvals"]
    )
    body = f"""<h1>Control Plane</h1>
<p class="muted">Orchestration and governance: organizations, workspaces, projects, policies, registries, workflows, events, and approvals.</p>
<h2>Identity &amp; RBAC</h2><div class="card"><strong>Protocols:</strong> {', '.join(gov['identity']['protocols'])}<br/>{roles}</div>
<h2>Policies</h2><ul class="plain">{policies}</ul>
<h2>Approval flows</h2><ul class="plain">{approvals}</ul>
<h2>Audit &amp; change management</h2>
<div class="card"><code>{gov['auditTrail']}</code><br/><br/><span class="muted">Flow:</span> {gov['changeManagement']['flow']}</div>"""
    return shell("Control Plane", body)


def render_platform(org):
    planes = "".join(
        f'<div class="card"><strong>{v["name"]}</strong><div class="muted">{v["summary"]}</div></div>'
        for k, v in org["planes"].items()
    )
    body = f"""<h1>Platform Overview</h1>
<p class="muted">Modular plane architecture across experience, knowledge, control, intelligence, runtime, and infrastructure.</p>
<div class="grid">{planes}</div>
<h2>Governance posture</h2>
<div class="card">Policies {len(org['governance']['policies'])} · Approvals {len(org['governance']['approvals'])} · RBAC roles {len(org['governance']['rbacRoles'])}</div>"""
    return shell("Platform Overview", body)


def render_organization(org):
    body = f"""<h1>Organization</h1>
<p class="muted">{org['summary']}</p>
<h2>Workspaces</h2><p>{''.join(f'<span class="pill">{w}</span>' for w in org['workspaces'])}</p>
<h2>Planes</h2>
{''.join(f'<div class="card"><strong>{v["name"]}</strong><div class="muted">{v["summary"]}</div></div>' for k, v in org['planes'].items())}
<h2>Governance</h2>
<div class="card"><strong>Identity:</strong> {', '.join(org['governance']['identity']['protocols'])}<br/>
<strong>RBAC:</strong> {', '.join(org['governance']['rbacRoles'])}<br/>
<strong>Policies:</strong> {len(org['governance']['policies'])} · <strong>Approvals:</strong> {len(org['governance']['approvals'])}</div>"""
    return shell("Organization", body)


def render_dashboard(metrics):
    body = '<h1>Executive Dashboard</h1><div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(170px,1fr))">' + "".join(
        f'<div class="card metric"><div class="value">{v}</div><div class="label">{k.replace("_"," ")}</div></div>'
        for k, v in metrics.items()
    ) + "</div>"
    return shell("Executive Dashboard", body)


def render_search():
    body = """<h1>Engineering Search</h1>
<p class="muted">Keyword + capability + ownership search across the knowledge base.</p>
<div class="card"><input id="q" style="width:100%;padding:.6rem;border-radius:8px;border:1px solid #1f3244;background:#0d1a28;color:#f5f7fb" placeholder="search resources, kinds, owners, capabilities" autofocus/>
<div id="out" style="margin-top:1rem"></div></div>
<script>
const idx=[];
fetch('search-index.json').then(r=>r.json()).then(d=>{window.idx=d;});
document.getElementById('q').addEventListener('input',e=>{
 const q=(e.target.value||'').toLowerCase();
 const hits=(window.idx||[]).filter(i=>(i.text||'').includes(q));
 document.getElementById('out').innerHTML=q?hits.map(h=>
   `<div class="card"><a style="font-weight:700" href="resources/${h.slug}.html">${h.name}</a> <span class="pill kind">${h.kind}</span><div class="muted">${h.summary}</div></div>`
 ).join('')||'<div class="muted">No matches.</div>':'';
});
</script>"""
    return shell("Search", body)


def render_architecture():
    body = """<h1>Platform Architecture</h1>
<p class="muted">The AEC is a modular platform with six planes. All derived artifacts (twins, context, graph, registries, portal) are generated from a canonical model beneath those planes.</p>
<h2>Canonical model</h2>
<div class="card"><code>organization → workspace → project → resource</code><br/><br/>
<span class="muted">Manifest:</span> <code>khulnasoft.yaml</code> is the authoritative contract; twins and portals are a derived layer.</div>
<h2>Planes</h2>
<ul class="plain">
<li><strong>Experience</strong> — portal, catalog views, dashboards</li>
<li><strong>Knowledge</strong> — graph, vectors, search, context fabric</li>
<li><strong>Control</strong> — org, governance, registries, workflows</li>
<li><strong>Intelligence</strong> — analyzers, readiness, recommendations</li>
<li><strong>Runtime</strong> — events, workers, deployment automation</li>
<li><strong>Infrastructure</strong> — GitHub/Kubernetes/cloud integrations</li>
</ul>"""
    return shell("Architecture", body)


def render_api():
    body = """<h1>API</h1>
<p class="muted">The platform is consumable via web, CLI, SDK, API, MCP, and webhooks. Endpoints serve the canonical model directly.</p>
<ul class="plain">
<li><code>GET /resources</code> — full resource registry</li>
<li><code>GET /resources/&lt;slug&gt;</code> — resource</li>
<li><code>GET /resources/&lt;slug&gt;/twin</code> — digital twin</li>
<li><code>GET /resources/&lt;slug&gt;/context</code> — layered, selective context</li>
<li><code>GET /resources/&lt;slug&gt;/recommendations</code> — insights</li>
<li><code>GET /graph</code> — knowledge graph</li>
<li><code>GET /registries</code> — control-plane registries</li>
<li><code>GET /llms.txt</code>, <code>/llms-full.txt</code>, <code>/mcp.json</code> — AI-ready</li>
<li><code>GET /health</code> — live platform health</li>
</ul>"""
    return shell("API", body)