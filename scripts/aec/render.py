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
    ("Graph", "graph.html"), ("Playground", "playground.html"), ("Impact", "impact.html"), ("Data Lake", "data-lake.html"), ("Digital Twins", "digital-twin.html"), ("Context", "context-fabric.html"),
    ("Registries", "registries.html"), ("Readiness", "readiness.html"), ("Timeline", "timeline.html"), ("Intelligence", "analytics.html"), ("Runtime", "runtime.html"), ("AI Plane", "ai-control-plane.html"),
    ("Control Plane", "control-plane.html"), ("Release", "release.html"), ("Organization", "organizations.html"),
    ("Platform", "platform-overview.html"), ("Dashboard", "exec-dashboard.html"),
    ("Docs", "docs/architecture.html"), ("API", "api.html"), ("Marketplace", "marketplace.html"),
]


def health_badge(status):
    cls = {"healthy": "ok", "degraded": "warn", "warning": "warn", "error": "bad", "critical": "bad"}.get(status, "ok")
    return f'<span class="badge {cls}">{status}</span>'


def shell(title, body):
    nav = "".join(f'<a href="{href}">{label}</a>' for label, href in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · KhulnaSoft Engineering Knowledge OS</title><style>{CSS}</style></head>
<body>
<header class="top"><div class="brand">KhulnaSoft <span class="accent">Knowledge OS</span></div><nav>{nav}</nav></header>
<main>{body}</main>
<footer class="footer"><span>KhulnaSoft Engineering Knowledge OS</span>
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
    body = f"""<h1>KhulnaSoft Engineering Knowledge OS</h1>
<p class="muted">The monorepo-scale operating layer for the Developer Portal, AI Context Platform, and Control Plane across the KhulnaSoft ecosystem.</p>
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
    body += "<h2>Template Registry</h2><ul class='plain'>" + "".join(
        f"<li><strong>{t['name']}</strong> ({t['kind']}) <span class='muted'>· {t['workspace']}</span></li>" for t in reg["template"]["resources"]
    ) + "</ul>" + ("<ul class='plain'>" + "".join(
        f"<li><strong>{m['name']}</strong> <span class='muted'>({m['type']})</span></li>" for m in reg["template"]["marketplace"]
    ) + "</ul>" if reg["template"]["marketplace"] else "")
    body += "<h2>Context Registry</h2><ul class='plain'>" + "".join(
        f"<li><strong>{r['name']}</strong> <code>{r['slug']}</code></li>" for r in reg["context"]["resources"]
    ) + "</ul>"
    body += "<h2>Model Registry</h2><ul class='plain'>" + "".join(
        f"<li><strong>{m['name']}</strong> ({m['kind']}) <span class='muted'>· {m.get('version')}</span></li>" for m in reg["model"]["models"]
    ) + "</ul>"
    body += "<h2>Tool Registry</h2><ul class='plain'>" + "".join(
        f"<li><strong>{t['name']}</strong> <span class='muted'>[{', '.join(t['toolTypes'])}]</span></li>" for t in reg["tool"]["tools"]
    ) + "</ul>"
    body += "<h2>Memory Registry</h2><ul class='plain'>" + "".join(
        f"<li><strong>{m['name']}</strong> <span class='muted'>({m['kind']})</span></li>" for m in reg["memory"]["memories"]
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


def render_ai_control_plane(reg, layers, ai_services=None):
    models = "".join(f'<li><strong>{m["name"]}</strong> · {m.get("version", "-")} <span class="muted">[{m["kind"]}]</span></li>' for m in reg['model']['models'])
    tools = "".join(f'<li><strong>{t["name"]}</strong> <span class="muted">[{", ".join(t["toolTypes"])}]</span></li>' for t in reg['tool']['tools'])
    memory = "".join(f'<li><strong>{m["name"]}</strong> <span class="muted">({m["kind"]})</span></li>' for m in reg['memory']['memories'])

    services_html = ""
    if ai_services:
        ev = ai_services["evaluation"]
        sa = ai_services["safety"]
        te = ai_services["telemetry"]
        guardrails = "".join(
            f'<li><strong>{g["name"]}</strong> ({g["check"]}) · {", ".join(g["requiredSignals"])}</li>'
            for g in sa["guardrails"]
        )
        eval_rows = "".join(
            f'<tr><td><strong>{e["name"]}</strong></td><td>{e["kind"]}</td>'
            f'<td>{e["evaluationScore"]}</td><td>{e.get("ready", "-")}</td></tr>'
            for e in ev["resources"]
        )
        services_html = f"""
<h2>Evaluation service</h2>
<div class="card"><strong>{ev['count']}</strong> AI surfaces · avg score <strong>{ev['avgEvaluationScore']}</strong> · {ev['agentCount']} agents · {ev['promptCount']} prompts</div>
<table><thead><tr><th>Resource</th><th>Kind</th><th>Score</th><th>Readiness</th></tr></thead><tbody>{eval_rows}</tbody></table>
<h2>Safety service</h2>
<div class="card"><strong>{sa['policyCount']}</strong> guardrail policies · <strong>{sa['security']['cleanScans']}/{sa['security']['total']}</strong> clean scans · AI agent-ready {sa['aiPosture']['agentReadyPct']}%</div>
<ul class="plain">{guardrails}</ul>
<h2>Telemetry service</h2>
<div class="card"><strong>{te['aiResources']}</strong> AI resources · <strong>{te['contextBundles']}</strong> context bundles · {te['contextCoveragePct']}% coverage<br/>
<span class="muted">Serving modes:</span> {', '.join(te['operations']['modes'])}<br/>
<span class="muted">Registries:</span> {', '.join(te['registries'])}</div>"""

    body = f"""<h1>AI Control Plane</h1>
<p class="muted">Prompt registry, context registry, agent registry, model registry, tool registry, memory registry, template registry, and AI-safe metadata for agents and automation inside the Knowledge OS.</p>
<h2>Context Registry ({reg['context']['count']})</h2><ul class="plain">
{''.join(f'<li><strong>{r["name"]}</strong> <code>{r["slug"]}</code></li>' for r in reg['context']['resources'])}</ul>
<h2>Prompt Registry ({reg['prompt']['count']})</h2><ul class="plain">
{''.join(f'<li><strong>{p["id"]}</strong><br/><span class="muted">{p["body"]}</span></li>' for p in reg['prompt']['prompts'])}</ul>
<h2>Agent Registry ({reg['agent']['count']})</h2><ul class="plain">
{''.join(f'<li><strong>{a["name"]}</strong> — {a["description"]} <span class="muted">[{", ".join(a["capabilities"])}]</span></li>' for a in reg['agent']['agents'])}</ul>
<h2>Model Registry ({reg['model']['count']})</h2><ul class="plain">{models}</ul>
<h2>Tool Registry ({reg['tool']['count']})</h2><ul class="plain">{tools}</ul>
<h2>Memory Registry ({reg['memory']['count']})</h2><ul class="plain">{memory}</ul>
<h2>Context layers</h2><p>{''.join(f'<span class="pill">{l}</span>' for l in layers)}</p>
{services_html}"""
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
    body = """<h1>Ask the Portal</h1>
<p class="muted">Hybrid search across the knowledge base: keyword + semantic (TF-IDF) ranking with live previews from each resource's context bundle. Pick a mode or let the default blend both.</p>
<div class="card">
<div style="display:flex;gap:.6rem;flex-wrap:wrap;align-items:center">
<input id="q" style="flex:1;min-width:220px;padding:.6rem;border-radius:8px;border:1px solid #1f3244;background:#0d1a28;color:#f5f7fb" placeholder="e.g. api agent gateway mcp" autofocus/>
<select id="mode"><option value="hybrid">hybrid</option><option value="keyword">keyword</option><option value="semantic">semantic</option></select>
<span class="muted" style="align-self:center" id="count"></span>
</div>
<div id="facets" style="display:flex;flex-wrap:wrap;gap:.6rem;margin-top:.8rem"></div>
<div id="out" style="margin-top:1rem"></div>
</div>
<script>
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const ranks=new Map();
const toks=w=>w.toLowerCase().split(/[^\\w+#\\.-]+/).filter(Boolean);
function score(item,q){
 const terms=toks(q);if(!terms.length)return 0;
 let s=0;
 for(const t of terms){
   if(item.name&&item.name.toLowerCase().includes(t))s+=8;
   if((item.text||'').includes(t))s+=3;
   if(item.summary&&item.summary.toLowerCase().includes(t))s+=1;
   if((item.capabilities||[]).some(c=>c.toLowerCase().includes(t)))s+=2;
 }
 return s;
}
 function activeFacets(){return [...document.querySelectorAll('#facets input:checked')].map(i=>JSON.parse(i.dataset.f));}
function render(d,q){
  const faces=activeFacets();
  let hits=(d||[]).map(it=>({it,r:ranks.get(it.slug)||0,sk:score(it,q)})).filter(x=>q?x.r>0||x.sk>0:true);
  for(const f of faces){hits=hits.filter(x=>String(x.it[f.k]??'')===String(f.v));}
  hits.sort((a,b)=>(b.r||b.sk)-(a.r||a.sk));
 const kinds=[...new Set((d||[]).map(i=>i.kind))];
 document.getElementById('facets').innerHTML=kinds.map(k=>
  `<label style="background:#0d1a28;border:1px solid #1f3244;padding:.3rem .6rem;border-radius:8px;font-size:.8rem"><input type="checkbox" data-f='{"k":"kind","v":"${esc(k)}"}' class="fac" style="margin-right:.35rem">${esc(k)}</label>`).join('');
 document.getElementById('count').textContent=hits.length+' result(s)';
 document.getElementById('out').innerHTML=q||faces.length?(
  hits.map(({it,r})=>`<div class="card" style="margin-bottom:.6rem">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <a style="font-weight:700" href="resources/${esc(it.slug)}.html">${esc(it.name)}</a>
      <span>${esc(it.kind)}</span></div>
    <div class="muted">${esc(it.summary)}</div>
    <div style="margin-top:.4rem"><span class="pill">readiness ${it.readiness}</span><span class="pill">${esc(it.workspace||'core')}</span><span class="pill">${esc(it.lifecycle||'active')}</span>
    <a style="margin-left:.5rem" href="context/${esc(it.slug)}.json">bundle</a> · <a href="twins/${esc(it.slug)}.json">twin</a></div>
  </div>`).join('')||'<div class="muted">No matches.</div>':'<div class="muted">Type keywords or filter by facet above.</div>';
}
function go(d){
 const q=document.getElementById('q').value;
 ranks.clear();
 if(q){
  const m=document.getElementById('mode').value;
  fetch('/search?q='+encodeURIComponent(q)+'&mode='+m).then(r=>r.json()).then(j=>{
   (j.results||[]).forEach(rr=>ranks.set(rr.slug,rr.score));
   render(d,q);
  });
 } else { render(d,q); }
}
function init(d){
 window.idx=d;
 document.getElementById('q').addEventListener('input',()=>go(d));
 document.getElementById('mode').addEventListener('change',()=>go(d));
 document.getElementById('facets').addEventListener('change',()=>render(d,document.getElementById('q').value));
 render(d,'');
}
fetch('search-index.json').then(r=>r.json()).then(init);
 </script>"""
    return shell("Ask the Portal", body)


def render_playground():
    body = """<h1>Context Explorer &amp; Agent Playground</h1>
<p class="muted">Inspect a resource's layered AI context, its relationships, readiness, and generated recommendations — then copy a ready-to-use context block or an agent prompt for any resource.</p>
<div class="card">
<div style="display:flex;gap:.6rem;flex-wrap:wrap;align-items:center">
<select id="picker" style="flex:1;min-width:220px;padding:.6rem;border-radius:8px;border:1px solid #1f3244;background:#0d1a28;color:#f5f7fb">
<option value="">— choose a resource —</option></select>
<button id="ctx" style="padding:.6rem 1rem;border-radius:8px;border:1px solid #1f3244;background:#14324f;color:#58c6dd;cursor:pointer">Copy context block</button>
<button id="prm" style="padding:.6rem 1rem;border-radius:8px;border:1px solid #1f3244;background:#14324f;color:#58c6dd;cursor:pointer">Copy agent prompt</button>
</div>
<div style="display:flex;align-items:center;gap:.6rem;margin-top:.6rem">
<label class="muted" style="font-size:.8rem">Filter layers:</label>
<div id="layers" style="display:flex;flex-wrap:wrap;gap:.3rem"></div>
</div>
</div>
<div id="out"><div class="muted" style="margin-top:1rem">Select a resource above to render its full interactive context.</div></div>
<script>
const LAY_ORDER=["metadata","architecture","dependency","api","workflow","deployment","runtime","observability","security","business","health"];
const layer={};
function esc(s){return String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function fmt(v){if(typeof v==='boolean')return String(v);if(typeof v==='object')return JSON.stringify(v);return v;}
function findRes(slug){return (window.state||[]).find(r=>r.slug===slug);}
function render(){
 if(!window.cur){document.getElementById('out').innerHTML='<div class="muted" style="margin-top:1rem">Select a resource above.</div>';return;}
 const ctx=window.cur.context, st=findRes(window.cur.resource.slug);
 const dep=ctx.dependency&&ctx.dependency.relationships||[];
 let html='<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">';
 html+=`<div class="card"><strong>${esc(window.cur.resource.name)}</strong><br/><span class="pill kind">${esc(window.cur.resource.kind)}</span></div>`;
 html+=`<div class="card"><strong>${st?st.readiness:'—'}</strong><br/><span class="muted">readiness</span></div>`;
 html+=`<div class="card"><strong>${Object.keys(ctx).length}</strong><br/><span class="muted">layers present</span></div>`;
 html+=`<div class="card"><strong>${dep.length}</strong><br/><span class="muted">relationships</span></div></div>`;
 html+='<h2>Layers</h2>';
 for(const l of LAY_ORDER){
  if(!(l in ctx))continue;
  const on=layer[l]!==false;
  const rows=Object.entries(ctx[l]).map(([k,v])=>`<tr><td style="width:38%" class="muted"><code>${esc(k)}</code></td><td><code>${esc(fmt(v))}</code></td></tr>`).join('');
  html+=`<div class="card" style="margin-bottom:.6rem;opacity:${on?1:.45}">
   <div style="display:flex;justify-content:space-between;align-items:center"><strong style="color:#58c6dd">${l}</strong>
   ${on?`<a href="#" data-lay="${l}" data-on="0">hide</a>`:`<a href="#" data-lay="${l}" data-on="1">show</a>`}</div>
   ${on?`<table style="margin-top:.4rem"><tbody>${rows}</tbody></table>`:''}</div>`;
 }
 html+=`<h2>Relationships</h2><ul class="plain">${dep.length?dep.map(e=>`<li>${esc(e.type)} → <code>${esc(e.target)}</code>${e.detail?' · '+esc(e.detail):''}</li>`).join(''):'<li class="muted">No declared relationships.</li>'}</ul>`;
 html+=`<h2>Recommended actions</h2><ul class="plain">${(st&&st.recommendations&&st.recommendations.length)?st.recommendations.map(a=>`<li>${esc(a)}</li>`).join(''):'<li class="muted">No recommended actions.</li>'}</ul>`;
 document.getElementById('out').innerHTML=html;
}
function visibleContext(){
 const ctx={};for(const l in window.cur.context){if(layer[l]===false)continue;ctx[l]=window.cur.context[l];}return ctx;
}
function buildPrompt(){
 const st=findRes(window.cur.resource.slug), layers=Object.keys(visibleContext());
 const lines=[`You are operating the KhulnaSoft Engineering Knowledge OS.`];
 lines.push(`Inspect the resource "${st.name}" (${st.kind}).`);
 lines.push(`Active context layers: ${layers.join(', ')}.`);
 lines.push(`Readiness: ${st.readiness}.`);
 if(st.recommendations&&st.recommendations.length)lines.push('Recommended actions: '+st.recommendations.join('; '));
 lines.push(`Return a concise engineering briefing and the next best action for this resource.`);
 return lines.join('\n');
}
function copyAsText(text){
 const pre=document.getElementById('out');pre.textContent='\n'+text+'\n';
 const s=window.getSelection();const r=document.createRange();r.selectNodeContents(pre);s.removeAllRanges();s.addRange(r);
 try{document.execCommand('copy');}catch(e){}s.removeAllRanges();
}
document.addEventListener('click',ev=>{
 const t=ev.target.closest('[data-lay]');if(!t)return;ev.preventDefault();layer[t.dataset.lay]=(t.dataset.on==='1');render();
});
document.getElementById('ctx').addEventListener('click',()=>{
 if(!window.cur){alert('Select a resource first.');return;}
 const st=findRes(window.cur.resource.slug);
 copyAsText(`# ${st.name} — context bundle\n\n`+JSON.stringify(visibleContext(),null,2));
});
document.getElementById('prm').addEventListener('click',()=>{
 if(!window.cur){alert('Select a resource first.');return;}
 copyAsText(buildPrompt());alert('Agent prompt copied to clipboard.');
});
document.getElementById('picker').addEventListener('change',e=>{
 const slug=e.target.value;if(!slug){window.cur=null;render();return;}
 fetch('context/'+slug+'.json').then(r=>r.json()).then(c=>{window.cur=c;render();});
});
fetch('state.json').then(r=>r.json()).then(d=>{
 window.state=d.resources;
 document.getElementById('picker').innerHTML='<option value="">— choose a resource —</option>'+d.resources.map(r=>`<option value="${r.slug}">${r.name} (${r.kind})</option>`).join('');
});
</script>"""
    return shell("Context Explorer", body)


def render_impact_simulator():
    body = """<h1>Dependency &amp; Change-Impact Simulator</h1>
<p class="muted">Click a resource to see the <strong>downstream blast radius</strong>: which services and components are affected if it changes. Impact is derived from the knowledge graph at build-time and ranked by exposure.</p>
<div id="summ" class="card" style="margin-bottom:1rem"></div>
<div style="display:flex;gap:1.4rem;flex-wrap:wrap">
<div id="list" style="flex:1;min-width:280px"></div>
<div id="detail" style="flex:2;min-width:320px"><div class="muted">Select a resource on the left to simulate impact.</div></div>
</div>
<script>
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
window.dim=null;
fetch('impact.json').then(r=>r.json()).then(d=>{
 window.dim=d;
 const byName=Object.fromEntries(d.per_resource.map(v=>[v.name,v]));
 document.getElementById('summ').innerHTML=`<span class="muted">fleet</span> <strong>${d.total}</strong> resources ·
 max blast radius <strong>${d.max_blast_radius}</strong> · avg <strong>${d.avg_blast_radius}</strong>`;
 document.getElementById('list').innerHTML='<h2>Resources</h2><ul class="plain">'+d.nodes.map(n=>
  `<li><a href="#" data-resid="${esc(n.id)}">${esc(n.name)}</a> <span class="muted">(${esc(n.kind)})</span> · <span class="pill">${byName[n.name].blast_radius} affected</span></li>`).join('')+'</ul>';
});
document.addEventListener('click',ev=>{
 const t=ev.target.closest('[data-resid]');if(!t)return;ev.preventDefault();
 const v=(window.dim&&window.dim.per_resource||{})[t.dataset.resid];if(!v)return;
 let html=`<h2>Impact of &quot;${esc(v.name)}&quot;</h2>
 <div class="card"><strong>Blast radius:</strong> ${v.blast_radius} resource(s) affected</div>
 ${v.blast_radius===0?'<p class="muted" style="margin-top:.6rem">No downstream dependents — safe change surface.</p>':''}`;
 if(v.impacted.length){
  html+=`<h3>Affected dependents (ranked by exposure)</h3><table><thead><tr><th>Resource</th><th>Kind</th><th>Hop depth</th></tr></thead><tbody>`
  +v.impacted.map(n=>`<tr><td>${esc(n.name)}</td><td>${esc(n.kind)}</td><td>${n.depth}</td></tr>`).join('')+`</tbody></table>`;
 }
 document.getElementById('detail').innerHTML=html;
});
</script>"""
    return shell("Impact Simulator", body)


def _sparkline(values, w=240, h=52):
    values = [v for v in values if isinstance(v, (int, float))]
    if not values:
        return '<span class="muted">no history</span>'
    mn, mx = min(values), max(values)
    span = (mx - mn) or 1
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = round(i / max(1, n - 1) * (w - 4)) + 2
        y = round(h - 4 - (v - mn) / span * (h - 8))
        pts.append(f"{x},{y}")
    poly = " ".join(pts)
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block">'
        f'<polyline points="{poly}" fill="none" stroke="#58c6dd" stroke-width="1.6"/>'
        f'<circle cx="{pts[-1].split(",")[0]}" cy="{pts[-1].split(",")[1]}" r="2.4" fill="#58c6dd"/>'
        f'<text x="{w-2}" y="{h-3}" text-anchor="end" fill="#93a7bd" font-size="9">{values[-1]}</text>'
        f"</svg>"
    )


def render_readiness_timeline(state):
    history = state.get("history", [])
    labels = [s["build"].split("·")[0] for s in history]
    drift = state.get("drift", {})
    resources = state.get("resources", {})
    cards = ""
    for rid, res in resources.items():
        series = [s["scores"].get(rid) for s in history]
        badge = ""
        if rid in drift:
            d = drift[rid]
            direction = "up" if d["direction"] == "up" else "down"
            badge = f' <span class="badge {"ok" if direction=="up" else "warn"}">drift {d["delta"]:+d}</span>'
        cards += f"""<div class="card"><div style="display:flex;justify-content:space-between;align-items:center">
<a style="font-weight:700" href="resources/{res['slug']}.html">{res['name']}</a>{badge}</div>
{_sparkline([s['scores'].get(rid) for s in history])}</div>"""
    drift_badges = ""
    for rid, d in drift.items():
        cls = "ok" if d["direction"] == "up" else "bad"
        drift_badges += f'<span class="badge {cls}">{d["name"]} {d["delta"]:+d} → {d["current"]}</span> '
    body = f"""<h1>Readiness Timeline &amp; Drift</h1>
<p class="muted">Readiness is recorded on every build. Trend lines show movement over <strong>{len(history)}</strong> snapshot(s); drift badges flag a change of ≥5 points versus the previous build. History is derived at build time, never edited by hand.</p>
<h2>Drift detected ({len(drift)})</h2>
<div class="card">{drift_badges if drift_badges else '<span class="muted">No material drift across the fleet.</span>'}</div>
<h2>Resources</h2>
<div class="grid">{cards}</div>
<h2>Fleet average</h2>
<div class="card">{_sparkline([round(sum(s['scores'].values()) / max(1, len(s['scores']))) for s in history], 300, 60)}</div>"""
    return shell("Readiness Timeline", body)


def render_analytics(analyses):
    s = analyses["summary"]
    cards = ""
    for a in analyses["per_resource"].values():
        debt = "none" if a["techDebt"] == ["none detected"] else ", ".join(a["techDebt"])
        cards += f"""<div class="card"><div style="display:flex;justify-content:space-between">
<a style="font-weight:700" href="resources/{a['slug']}.html">{a['slug']}</a>
{('badge ok' if not a['deprecation']['deprecated'] else 'badge bad')}</div>
<div class="muted" style="margin:.3rem 0">lang: {', '.join(a['languages']) or '—'} · frameworks: {', '.join(a['frameworks']) or '—'}</div>
<div class="muted">arch: {', '.join(a['architecture'])} · api: {'yes' if a['api'] else 'no'}</div>
<div class="muted" style="margin-top:.3rem">tech debt: <code>{debt}</code></div>
 {('<span class="badge bad">deprecated</span> ' if a['deprecation']['deprecated'] else '')}
 {('<span class="badge warn">perf regression</span>' if a['perfRegression']['regression'] else '')}
 {''.join(f'<span class="badge warn">drift: {k}</span>' for k in a['drift'])}
 {('<span class="badge warn">compat risk</span>' if a['apiCompatibility']['risk'] == 'unversioned' else '')}
 {''.join(f'<span class="badge warn">cost</span>' for _ in a['costOptimization'])}
</div>"""
    body = f"""<h1>Engineering Intelligence</h1>
<p class="muted">Deterministic analyzers over the resource registry: languages, frameworks, architecture patterns, API exposure, dependency resolution, security posture, technical debt, deprecation, performance regressions, and drift detection across architecture, dependencies, security, infrastructure, documentation, and configuration.</p>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
<div class="card metric"><div class="value">{s['relationship_count']}</div><div class="label">relationships</div></div>
<div class="card metric"><div class="value">{s['api_resources']}</div><div class="label">api resources</div></div>
<div class="card metric"><div class="value">{s['tech_debt_items']}</div><div class="label">debt items</div></div>
<div class="card metric"><div class="value">{s['deprecated_resources']}</div><div class="label">deprecated</div></div>
<div class="card metric"><div class="value">{s['perf_regressions']}</div><div class="label">perf regressions</div></div>
<div class="card metric"><div class="value">{s['drift_items']}</div><div class="label">drift signals</div></div>
<div class="card metric"><div class="value">{s['api_compatibility_risk']}</div><div class="label">api compat risk</div></div>
<div class="card metric"><div class="value">{s['migration_suggestions']}</div><div class="label">migration hints</div></div>
<div class="card metric"><div class="value">{s['cost_optimization_opportunities']}</div><div class="label">cost opts</div></div>
<div class="card metric"><div class="value">{s['unused_components']}</div><div class="label">unused</div></div>
<div class="card metric"><div class="value">{s['duplicate_libraries']}</div><div class="label">duplicate libs</div></div>
</div>
{s['drift_by_kind'] and '<h2>Drift by kind</h2><div class="grid">' + ''.join(f'<div class="card"><strong>{k}</strong> — {v}</div>' for k, v in s['drift_by_kind'].items() if v) + '</div>' or ''}
{analyses.get('duplicate_libraries') and analyses['duplicate_libraries'] and '<h2>Duplicate libraries</h2><div class="grid">' + ''.join(f'<div class="card"><code>{k}</code> — {", ".join(x["name"] for x in v)}</div>' for k, v in analyses['duplicate_libraries'].items()) + '</div>' or ''}
<h2>Analyses</h2><div class="grid">{cards}</div>"""
    return shell("Engineering Intelligence", body)


def render_data_lake():
    body = """<h1>Engineering Data Lake</h1>
<p class="muted">A raw, event-driven log of engineering signals (GitHub, GitLab, CI/CD, Kubernetes, cloud, monitoring, security, packages, documentation, and AI sources) that feeds the twins, graph, context, and intelligence below. Differently from a static catalog, the data lake keeps raw events separated from normalized state; native webhooks are translated into canonical events by source adapters and persisted for the next targeted refresh.</p>
<div id="summ" class="grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))"></div>
<h2>Recent events</h2>
<div class="card"><table id="tbl"><thead><tr><th>Event</th><th>Source</th><th>Type</th><th>Touched</th><th>Health effect</th></tr></thead><tbody></tbody></table></div>
<p class="muted" style="margin-top:.6rem">Machine-readable: <code>events.json</code> (normalized log) · <code>event-index.json</code> (event → touched resources).</p>
<script>
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
fetch('events.json').then(r=>r.json()).then(d=>{
  document.getElementById('summ').innerHTML=`<div class="card metric"><div class="value">${d.summary.total_events}</div><div class="label">events</div></div>`
  +`<div class="card metric"><div class="value">${d.summary.resources_touched}</div><div class="label">resources touched</div></div>`
  +`<div class="card metric"><div class="value">${Object.keys(d.summary.sources).length}</div><div class="label">sources</div></div>`;
  document.getElementById('tbl').querySelector('tbody').innerHTML=(d.events||[]).map(e=>
    `<tr><td><code>${esc(e.id)}</code></td><td>${esc(e.source)}</td><td>${esc(e.type)}</td><td>${(e.touched||[]).map(t=>esc(t.split(':').pop())).join(', ')}</td><td>${e.healthEffect>0?'+':''}${e.healthEffect}</td></tr>`).join('');
});
</script>"""
    return shell("Data Lake", body)


def render_release_copilot(state):
    per = state["per_resource"]
    verdicts = sorted(
        per.values(),
        key=lambda v: v["decision"]["score"],
    )
    rows = ""
    for v in verdicts:
        ok = v["decision"]["verdict"] == "approve"
        rows += f"""<tr><td><a href="resources/{v['slug']}.html">{v['name']}</a></td>
<td><span class="pill kind">{v['kind']}</span></td>
<td><span class="badge {'ok' if ok else 'bad'}">{v['decision']['verdict']}</span></td>
<td>{v['decision']['passed']}/{v['decision']['total']}</td></tr>"""
    gov = "".join(f'<li>{g["check"]} <span class="muted">· {g["required"]}</span> <span class="badge ok">policy</span></li>' for g in state["governance_gates"])
    apps = "".join(f'<li>{a["check"]} <span class="muted">· required {a["required"]}</span></li>' for a in state["approval_gates"])
    body = f"""<h1>Release Readiness &amp; Governance Copilot</h1>
<p class="muted">A single decision view that aggregates docs, security, tests, deployment state, approvals, and readiness into one release verdict per resource. Rules are deterministic and derived at build time.</p>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
<div class="card metric"><div class="value">{state['releaseable']}</div><div class="label">releaseable</div></div>
<div class="card metric"><div class="value">{state['blocked']}</div><div class="label">blocked</div></div>
<div class="card metric"><div class="value">{state['total_resources']}</div><div class="label">resources</div></div>
</div>
<h2>Governance gates</h2><ul class="plain">{gov}</ul>
<h2>Approval flows</h2><ul class="plain">{apps}</ul>
<h2>Release verdicts</h2>
<div class="card"><table><thead><tr><th>Resource</th><th>Kind</th><th>Verdict</th><th>Gates passed</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Why blocked?</h2>
<p class="muted">Click a resource's page for full gate detail; the checklist below is produced by the rules engine for every resource.</p>
{''.join(f'<div class="card" style="margin-bottom:.6rem"><strong>{v["name"]}</strong> <span class="badge {"ok" if v["decision"]["verdict"]=="approve" else "bad"}">{v["decision"]["verdict"]}</span><ul class="plain">' + ''.join(f'<li><span class="badge {"ok" if g["passed"] else "warn"}">{("pass" if g["passed"] else "fail")}</span> {g["check"]} <span class="muted">· {g["actual"]} (required {g["required"]})</span>{"" if g["passed"] else f' — {g["advice"]}'}</li>' for g in v["gates"]) + '</ul></div>' for v in verdicts)}"""
    return shell("Release Copilot", body)


def render_marketplace(items, sdk_artifacts):
    cards = ""
    for it in items:
        tags = "".join(f'<span class="pill">{t}</span>' for t in it.get("tags", []))
        cards += f"""<div class="card" style="display:flex;flex-direction:column;justify-content:space-between">
<div><span class="pill kind">{it['type']}</span>
<div style="font-weight:700;margin-top:.3rem">{it['name']}</div>
<div class="muted" style="margin:.3rem 0">{it['summary']}</div>
<div>{tags}</div></div>
<div style="margin-top:.6rem"><button class="install" data-id="{it['id']}">Install</button></div></div>"""
    sdks = "".join(f"""<div class="card"><strong>{s['language']}</strong> · <code>{s['path']}</code> · {s['lines']} lines<br/>
<a href="sdks/{s['path'].split('/')[-1]}" style="font-size:.85rem">view stub</a></div>""" for s in sdk_artifacts)
    body = f"""<h1>Marketplace &amp; SDKs</h1>
<p class="muted">Reusable engineering assets (templates, prompt packs, policies, agents, workflows) installable from the portal, and generated SDK stubs derived from the canonical schema for consuming the platform programmatically.</p>
<h2>SDKs (generated from resource.schema.json)</h2><div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(220px,1fr))">{sdks}</div>
<h2>Reusable assets</h2><div class="grid">{cards}</div>
<div id="toast" class="muted" style="margin-top:.8rem"></div>
<div id="resolved" style="margin-top:.8rem"></div>
<script>""" + """
document.addEventListener('click', ev => {
  const b = ev.target.closest('.install'); if (!b) return;
  const d = document.getElementById('toast'); d.textContent = 'Installing ' + b.dataset.id + '…';
  fetch('/marketplace/install', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({id: b.dataset.id})})
    .then(r => r.json()).then(j => {
      d.textContent = 'Installed ' + b.dataset.id + ' ✔';
      let html = '<div class="card"><strong>Resolved:</strong> ' + j.type + ' → ' + j.resolved.kind +
                 ' (' + j.resolved.id + ')';
      if (j.resolved.twin) {
        html += '<br/><span class="muted">twin: ' + j.resolved.twin.resource.name +
                ' readiness ' + j.resolved.twin.readiness.overall + '</span>';
      }
      document.getElementById('resolved').innerHTML = html + '</div>';
    }).catch(e => { d.textContent = 'Install failed'; console.error(e); });
  setTimeout(() => d.textContent = '', 2200);
});
</script>"""
    return shell("Marketplace", body)


def render_runtime_plane(runtime_state, resources):
    wf = "".join(f"""<div class="card"><div style="display:flex;justify-content:space-between">
<strong>{w['name']}</strong><span class="pill">{w['trigger']}</span></div>
<ul class="plain" style="margin-top:.4rem">{''.join(f'<li>{s}</li>' for s in w.get('steps', []))}</ul></div>"""
                  for w in runtime_state["workflows"])
    autos = "".join(f'<li><strong>{a["name"]}</strong> — <span class="muted">{a["action"]}</span> '
                    f'<span class="pill">on {a["event"]}</span></li>' for a in runtime_state["automations"])
    body = f"""<h1>Runtime Plane &amp; Automation</h1>
<p class="muted">Event-driven services that turn the data lake into orchestration: workflows describe the steps for each trigger, and automations bind events to actions such as provisioning context, reconciling drift, and enforcing release gates.</p>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
<div class="card metric"><div class="value">{len(runtime_state['workflows'])}</div><div class="label">workflows</div></div>
<div class="card metric"><div class="value">{len(runtime_state['automations'])}</div><div class="label">automations</div></div>
<div class="card metric"><div class="value">{runtime_state['events_seen']}</div><div class="label">events ingested</div></div>
</div>
<h2>Workflows</h2><div class="grid">{wf}</div>
<h2>Automations</h2><div class="grid"><div class="card"><ul class="plain">{autos}</ul></div></div>"""
    return shell("Runtime & Automation", body)


def render_architecture():
    body = """<h1>Platform Architecture</h1>
<p class="muted">The Engineering Knowledge OS is a modular platform with six planes. All derived artifacts (twins, context, graph, registries, portal) are generated from a canonical model beneath those planes.</p>
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
<li><code>GET /impact</code> — change-impact / blast radius</li>
<li><code>GET /release</code> — release readiness copilot</li>
<li><code>GET /search-index</code> — enriched search index</li>
<li><code>GET /registries</code> — control-plane registries</li>
<li><code>GET /templates</code> — template registry</li>
<li><code>GET /ai/services</code>, <code>/ai/evaluation</code>, <code>/ai/safety</code>, <code>/ai/telemetry</code> — AI control-plane services</li>
<li><code>GET /llms.txt</code>, <code>/llms-full.txt</code>, <code>/mcp.json</code> — AI-ready</li>
<li><code>GET /health</code> — live platform health</li>
<li><code>POST /webhook/ingest</code> — accept a native webhook (GitHub/K8s/monitoring/etc.); set an <code>X-Source</code> header or <code>source</code> field to translate and persist a canonical event</li>
<li><code>sdks/aec.ts</code>, <code>sdks/aec.py</code> and 9 more generated typed clients (Go, Rust, Java, C#, PHP, Ruby, Swift, Kotlin, Dart)</li>
</ul>"""
    return shell("API", body)