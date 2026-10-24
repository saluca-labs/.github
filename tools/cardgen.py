#!/usr/bin/env python
"""Render Saluca Labs repo graphics from HTML/CSS with Playwright.

Palette is sampled from the three cyberpunk portraits: deep indigo ground,
neon cyan (#22e8ff) and magenta (#ff3fe0), with the chrome of the Saluca
shield as the title metal. Portraits are assigned per repo family:

  pr0fx    - Saluca Labs / research / physical science
  tiresias - security, detection, verification
  asphodel - memory, persistence, context

Usage:
  python cardgen.py --repos org_repos.json --out out
Outputs:
  social/<repo>.png        1280x640  GitHub social preview
  readme/<repo>.png        1200x300  README header banner
  org/profile-banner.png   1280x400  org profile README header
  org/social-preview.png   1280x640  org social preview
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import pathlib
import re

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "out"
SHIELD = ROOT / "org-avatar.png"
PORTRAITS: dict[str, pathlib.Path] = {
    "pr0fx": ROOT / "pr0fx.jpg",
    "tiresias": ROOT / "tiresias.jpg",
    "asphodel": ROOT / "asphodel.jpg",
}

# --- palette, sampled from the portraits ------------------------------------
VOID = "#050713"
INDIGO = "#0d0a24"
PANEL = "#120d2e"
CYAN = "#22e8ff"
CYAN_HOT = "#7bfaff"
MAGENTA = "#ff3fe0"
MAGENTA_HOT = "#ff8bf0"
VIOLET = "#8b5cf6"
CHROME = "#c9cdd1"
SILVER = "#e9ecef"
WHITE = "#ffffff"


def dash(text: str) -> str:
    """House style: no em-dashes or en-dashes in anything we publish."""
    text = text.replace("—", " - ").replace("–", "-")
    return re.sub(r"\s+", " ", text).strip()


def data_uri(path: pathlib.Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


BASE_CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ background:{VOID}; }}
body {{
  font-family:"Segoe UI",system-ui,sans-serif;
  color:{CHROME};
  overflow:hidden;
  position:relative;
}}
.stage {{ position:relative; overflow:hidden; background:{VOID}; }}
.layer {{ position:absolute; inset:0; pointer-events:none; }}

/* neon horizon + perspective grid */
.glow {{
  background:
    radial-gradient(52% 60% at 78% 42%, rgba(255,63,224,.16), transparent 62%),
    radial-gradient(55% 65% at 12% 78%, rgba(34,232,255,.14), transparent 64%),
    radial-gradient(80% 70% at 45% 115%, rgba(139,92,246,.17), transparent 60%);
}}
.grid {{
  position:absolute; left:-30%; right:-30%; bottom:-46%; height:92%;
  background-image:
    repeating-linear-gradient(90deg, rgba(34,232,255,.20) 0 1px, transparent 1px 88px),
    repeating-linear-gradient(0deg, rgba(255,63,224,.18) 0 1px, transparent 1px 88px);
  transform:perspective(520px) rotateX(73deg);
  transform-origin:50% 100%;
  mask-image:linear-gradient(to top, rgba(0,0,0,.6), transparent 76%);
  -webkit-mask-image:linear-gradient(to top, rgba(0,0,0,.6), transparent 76%);
}}
.scan {{
  background:repeating-linear-gradient(0deg, rgba(255,255,255,.025) 0 1px, transparent 1px 3px);
  mix-blend-mode:screen;
}}
.vignette {{
  background:radial-gradient(115% 92% at 38% 40%, transparent 30%, rgba(2,3,9,.86) 100%);
}}
.grain {{
  opacity:.14; mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2'/><feColorMatrix type='saturate' values='0'/></filter><rect width='160' height='160' filter='url(%23n)' opacity='.5'/></svg>");
}}

/* HUD frame: cyan top-left, magenta bottom-right */
.frame {{ position:absolute; inset:24px; border:1px solid rgba(34,232,255,.13); }}
.corner {{ position:absolute; width:22px; height:22px; border-style:solid; border-width:0; }}
.c1 {{ top:-1px; left:-1px; border-top-width:2px; border-left-width:2px; border-color:{CYAN}; }}
.c2 {{ top:-1px; right:-1px; border-top-width:2px; border-right-width:2px; border-color:{CYAN}; }}
.c3 {{ bottom:-1px; left:-1px; border-bottom-width:2px; border-left-width:2px; border-color:{MAGENTA}; }}
.c4 {{ bottom:-1px; right:-1px; border-bottom-width:2px; border-right-width:2px; border-color:{MAGENTA}; }}

.mono {{ font-family:Consolas,"Courier New",monospace; }}
.eyebrow {{
  font-family:Consolas,monospace; font-size:13px; letter-spacing:.36em;
  text-transform:uppercase; color:{CYAN}; white-space:nowrap;
}}
.eyebrow b {{ color:{CHROME}; font-weight:400; }}
.rule {{ height:2px; background:linear-gradient(90deg,{CYAN} 0%,{MAGENTA} 55%,transparent 100%); }}
.rule.thin {{ height:1px; }}

.chrome-text {{
  background:linear-gradient(178deg,{WHITE} 0%,{SILVER} 24%,{CHROME} 46%,#6f7b88 58%,{CHROME} 74%,{SILVER} 100%);
  -webkit-background-clip:text; background-clip:text; color:transparent;
}}

/* portrait panel */
.portrait {{ position:absolute; top:0; bottom:0; right:0; overflow:hidden; }}
.portrait img {{ width:100%; height:100%; object-fit:cover; object-position:50% 28%; display:block; }}
.portrait .wash {{
  position:absolute; inset:0;
  background:
    linear-gradient(to right, {VOID} 0%, rgba(5,7,19,.94) 14%, rgba(5,7,19,.35) 48%, rgba(5,7,19,0) 72%),
    linear-gradient(to top, rgba(5,7,19,.82) 0%, rgba(5,7,19,0) 34%),
    linear-gradient(120deg, rgba(255,63,224,.10), rgba(34,232,255,.08));
  mix-blend-mode:normal;
}}
.portrait .edge {{
  position:absolute; top:0; bottom:0; left:0; width:2px;
  background:linear-gradient(to bottom,{CYAN},{VIOLET} 52%,{MAGENTA});
  box-shadow:0 0 18px rgba(255,63,224,.5);
}}
.portrait .tag {{
  position:absolute; right:26px; bottom:22px; font-size:11px; letter-spacing:.3em;
  color:{CYAN_HOT}; text-transform:uppercase; opacity:.75;
}}

/* title glitch: cyan and magenta offset copies behind the chrome face */
.titlewrap {{ position:relative; }}
.title {{ font-family:Bahnschrift,"Segoe UI",sans-serif; font-weight:600; letter-spacing:.012em;
  line-height:1.02; text-transform:uppercase; white-space:nowrap; }}
.titlewrap .ghost {{ position:absolute; inset:0; }}
.titlewrap .g1 {{ color:{CYAN}; transform:translate(-3px,1px); opacity:.30; }}
.titlewrap .g2 {{ color:{MAGENTA}; transform:translate(3px,-1px); opacity:.30; }}

.desc {{ color:#b9c2cf; line-height:1.45; }}
.meta {{ color:#8b96a6; }}
.shield-badge {{
  position:absolute; width:70px; height:70px; right:34px; top:30px; z-index:3;
  filter:drop-shadow(0 0 10px rgba(34,232,255,.35));
}}
.shield-badge img {{ width:100%; height:100%; display:block; opacity:.9; }}
"""


def page_social(repo: str, desc: str, idx: int, blurb: str,
                portrait: str, shield: str) -> str:
    desc = dash(desc)
    size = max(40, min(72, int(600 / (0.56 * max(len(repo), 1)))))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
.stage {{ width:1280px; height:640px; }}
.portrait {{ width:520px; }}
.content {{ position:absolute; left:0; top:0; bottom:0; width:790px; padding:60px 56px 84px 72px;
  display:flex; flex-direction:column; justify-content:center; }}
.titlewrap {{ margin:20px 0 18px; }}
.title {{ font-size:{size}px; }}
.desc {{ font-size:20px; max-width:620px; }}
.meta {{ margin-top:24px; font-size:13px; letter-spacing:.18em; text-transform:uppercase; }}
.footer {{ position:absolute; left:72px; bottom:40px; width:610px; display:flex; align-items:center; gap:16px; }}
.footer .url {{ font-size:12px; letter-spacing:.13em; color:#93a0b4; }}
.footer .idx {{ font-size:12px; letter-spacing:.3em; color:{MAGENTA_HOT}; margin-left:14px; }}
</style></head><body><div class="stage">
  <div class="layer glow"></div><div class="layer grid"></div>
  <div class="layer scan"></div><div class="layer vignette"></div><div class="layer grain"></div>
  <div class="portrait"><img src="{portrait}" alt=""><div class="wash"></div><div class="edge"></div></div>
  <div class="frame"><i class="corner c1"></i><i class="corner c2"></i><i class="corner c3"></i><i class="corner c4"></i></div>
  <div class="content">
    <div class="eyebrow"><b>SALUCA LABS</b> // RESEARCH DIVISION</div>
    <div class="titlewrap"><div class="title chrome-text">{html.escape(repo)}</div>
      <div class="title ghost g1">{html.escape(repo)}</div>
      <div class="title ghost g2">{html.escape(repo)}</div></div>
    <div class="rule" style="width:430px"></div>
    <div class="desc" style="margin-top:22px">{html.escape(desc)}</div>
    <div class="meta mono">{html.escape(blurb)}</div>
  </div>
  <div class="footer mono"><span class="url">github.com/saluca-labs/{html.escape(repo)}</span><span class="idx">SL-R // {idx:02d}</span></div>
</div></body></html>"""


def page_readme_banner(repo: str, desc: str, portrait: str) -> str:
    desc = dash(desc)
    size = max(30, min(54, int(760 / (0.58 * max(len(repo), 1)))))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
.stage {{ width:1200px; height:300px; }}
.portrait {{ width:340px; }}
.portrait .wash {{ background:linear-gradient(to right,{VOID} 0%,rgba(5,7,19,.92) 18%,rgba(5,7,19,.25) 60%,rgba(5,7,19,0) 85%); }}
.content {{ position:absolute; left:0; top:0; bottom:0; width:880px; padding:34px 40px 34px 52px;
  display:flex; flex-direction:column; justify-content:center; }}
.title {{ font-size:{size}px; margin-top:10px; }}
.desc {{ font-size:16px; margin-top:12px; max-width:720px; color:#aab4c2; }}
.eyebrow {{ font-size:11px; letter-spacing:.32em; }}
.footer {{ position:absolute; right:22px; top:20px; font-size:11px; letter-spacing:.3em; color:{CYAN}; z-index:4; }}
</style></head><body><div class="stage">
  <div class="layer glow"></div><div class="layer grid"></div>
  <div class="layer scan"></div><div class="layer vignette"></div><div class="layer grain"></div>
  <div class="portrait"><img src="{portrait}" alt=""><div class="wash"></div><div class="edge"></div></div>
  <div class="frame"><i class="corner c1"></i><i class="corner c2"></i><i class="corner c3"></i><i class="corner c4"></i></div>
  <div class="footer mono">SL-R</div>
  <div class="content">
    <div class="eyebrow mono"><b style="color:{CHROME}">SALUCA LABS</b> // RESEARCH</div>
    <div class="title chrome-text">{html.escape(repo)}</div>
    <div class="rule thin" style="width:330px;margin-top:10px"></div>
    <div class="desc">{html.escape(desc)}</div>
  </div>
</div></body></html>"""


def page_org_banner(portrait: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
.stage {{ width:1280px; height:400px; }}
.portrait {{ width:400px; }}
.content {{ position:absolute; left:0; top:0; bottom:0; width:900px; padding:48px 50px 48px 64px;
  display:flex; flex-direction:column; justify-content:center; }}
.word {{ font-size:84px; letter-spacing:.06em; }}
.tag {{ font-size:19px; color:#b6c0ce; margin-top:14px; }}
.chip {{ display:inline-block; margin-top:20px; padding:7px 12px; border:1px solid rgba(34,232,255,.5);
  color:{CYAN}; font-size:11px; letter-spacing:.3em; text-transform:uppercase; }}
.footer {{ position:absolute; left:64px; bottom:30px; width:700px; display:flex; }}
.footer .url {{ font-size:11px; letter-spacing:.2em; color:#93a0b4; }}
.footer .idx {{ margin-left:auto; font-size:11px; letter-spacing:.3em; color:{MAGENTA_HOT}; }}
</style></head><body><div class="stage">
  <div class="layer glow"></div><div class="layer grid"></div>
  <div class="layer scan"></div><div class="layer vignette"></div><div class="layer grain"></div>
  <div class="portrait"><img src="{portrait}" alt="Cyberpunk portrait of the Saluca Labs founder"><div class="wash"></div><div class="edge"></div></div>
  <div class="frame"><i class="corner c1"></i><i class="corner c2"></i><i class="corner c3"></i><i class="corner c4"></i></div>
  <div class="content">
    <div class="eyebrow"><b>SALUCA LLC</b> // RESEARCH BRANCH</div>
    <div class="word title chrome-text" style="margin-top:16px">SALUCA LABS</div>
    <div class="rule" style="width:500px;margin-top:16px"></div>
    <div class="tag">Open code, open records, open review.</div>
    <div><span class="chip mono">RESEARCH DIVISION</span></div>
  </div>
  <div class="footer mono"><span class="url">github.com/saluca-labs</span><span class="idx">SL // ORG</span></div>
</div></body></html>"""


def page_org_social(pr0fx: str, tiresias: str, asphodel: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
.stage {{ width:1280px; height:640px; }}
.triptych {{ position:absolute; right:0; top:0; bottom:0; width:560px; display:flex; }}
.slot {{ position:relative; flex:1 1 0; overflow:hidden; }}
.slot img {{ width:100%; height:100%; object-fit:cover; object-position:50% 28%; display:block; filter:saturate(1.05); }}
.slot::after {{ content:""; position:absolute; inset:0;
  background:linear-gradient(to right,{VOID} 0%,rgba(5,7,19,.72) 12%,rgba(5,7,19,.10) 46%,rgba(5,7,19,.30) 100%); }}
.slot + .slot {{ border-left:1px solid rgba(34,232,255,.32); }}
.triptych .edge {{ position:absolute; top:0; bottom:0; left:0; width:2px;
  background:linear-gradient(to bottom,{CYAN},{VIOLET} 50%,{MAGENTA}); box-shadow:0 0 20px rgba(255,63,224,.45); }}
.content {{ position:absolute; left:0; top:0; bottom:0; width:790px; padding:60px 46px 90px 72px;
  display:flex; flex-direction:column; justify-content:center; }}
.word {{ font-size:92px; letter-spacing:.05em; }}
.tag {{ font-size:22px; color:#b9c2cf; margin-top:16px; max-width:600px; }}
.chips {{ display:flex; gap:9px; margin-top:26px; flex-wrap:wrap; }}
.chip {{ padding:6px 11px; border:1px solid rgba(34,232,255,.42); color:{CYAN}; font-size:10px;
  letter-spacing:.22em; text-transform:uppercase; }}
.footer {{ position:absolute; left:72px; bottom:38px; width:640px; display:flex; }}
.footer .url {{ font-size:11px; letter-spacing:.2em; color:#93a0b4; }}
.footer .idx {{ margin-left:auto; font-size:11px; letter-spacing:.3em; color:{MAGENTA_HOT}; }}
</style></head><body><div class="stage">
  <div class="layer glow"></div><div class="layer grid"></div>
  <div class="layer scan"></div><div class="layer vignette"></div><div class="layer grain"></div>
  <div class="triptych"><div class="edge"></div>
    <div class="slot"><img src="{pr0fx}" alt=""></div>
    <div class="slot"><img src="{tiresias}" alt=""></div>
    <div class="slot"><img src="{asphodel}" alt=""></div></div>
  <div class="frame"><i class="corner c1"></i><i class="corner c2"></i><i class="corner c3"></i><i class="corner c4"></i></div>
  <div class="content">
    <div class="eyebrow"><b>SALUCA LLC</b> // RESEARCH BRANCH</div>
    <div class="word title chrome-text" style="margin-top:18px">SALUCA LABS</div>
    <div class="rule" style="width:520px;margin-top:18px"></div>
    <div class="tag">Open code, open records, open review. Research that can be checked.</div>
    <div class="chips mono"><span class="chip">AI SYSTEMS</span><span class="chip">SECURITY</span><span class="chip">PHYSICS</span><span class="chip">OPEN REVIEW</span></div>
  </div>
  <div class="footer mono"><span class="url">github.com/saluca-labs</span><span class="idx">SL // ORG</span></div>
</div></body></html>"""


# portrait family per repo. Unmapped repos raise rather than take a default.
PORTRAIT_OF = {
    "borrowed-trust-detections": "tiresias",
    "cct": "pr0fx",
    "chain-verify": "tiresias",
    "context-load-novelty": "asphodel",
    "detection-content": "tiresias",
    "elysium": "asphodel",
    "ephaptic-shi-testbed": "pr0fx",
    "gfe-unitary-fork": "pr0fx",
    "glass-brain-bench": "asphodel",
    "hephaestus": "pr0fx",
    "llm-determinism-probe": "pr0fx",
    "navier-stokes": "pr0fx",
    "open-review": "pr0fx",
    "roadmap": "pr0fx",
    "soulguard": "asphodel",
    "tartarus-mcp": "asphodel",
    "tiresias-core": "tiresias",
    "velamen": "tiresias",
}

BLURBS = {
    "borrowed-trust-detections": "DETECTION CONTENT / DEFENSIVE ONLY",
    "cct": "INFERENCE-TIME PROBE / STDLIB ONLY",
    "chain-verify": "HASH CHAIN / INDEPENDENT VERIFIER",
    "context-load-novelty": "LLM STUDY / HARNESS + DATA",
    "detection-content": "THREAT CAMPAIGNS / ONE PACK EACH",
    "elysium": "PERSISTENCE LAYER / TARTARUS",
    "ephaptic-shi-testbed": "COMPANION CODE / PREPRINT",
    "gfe-unitary-fork": "REPRODUCIBILITY / PHYSICS",
    "glass-brain-bench": "BENCHMARK STANDARD / SYNTHETIC MEMORY",
    "hephaestus": "ROBOTICS SUBSTRATE / SOURCE-AVAILABLE",
    "llm-determinism-probe": "MINIMAL REPRO / CPU ONLY",
    "navier-stokes": "DNS + JHTDB / ANALYSIS",
    "open-review": "PEER REVIEW / PUBLISHED BOTH WAYS",
    "roadmap": "ROADMAP / PUBLIC CHANGE RECORD",
    "soulguard": "AGENT TRUST LAYER / APACHE-2.0",
    "tartarus-mcp": "MODEL CONTEXT PROTOCOL / TOOLS",
    "tiresias-core": "SHARED PRIMITIVES / PROXY + OBSERVABILITY",
    "velamen": "STEGANOGRAPHY / TOKEN DISTRIBUTIONS",
}


def main() -> None:
    global OUT, SHIELD
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repos", default=str(ROOT / "org_repos.json"))
    ap.add_argument("--shield", default=str(ROOT / "org-avatar.png"))
    ap.add_argument("--out", default=str(ROOT / "out"))
    args = ap.parse_args()

    OUT = pathlib.Path(args.out)
    SHIELD = pathlib.Path(args.shield)
    for name, p in PORTRAITS.items():
        if not p.exists():
            raise SystemExit(f"missing portrait {name}: {p}")
    if not SHIELD.exists():
        raise SystemExit(f"missing shield: {SHIELD}")

    repos = json.loads(pathlib.Path(args.repos).read_text(encoding="utf-8"))
    public = sorted([r for r in repos if r["visibility"] == "PUBLIC"],
                    key=lambda r: r["name"])
    for sub in ("social", "readme", "org"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    uri = {k: data_uri(p, "image/jpeg") for k, p in PORTRAITS.items()}
    shield_uri = data_uri(SHIELD, "image/png")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 640})

        for idx, repo in enumerate(public, start=1):
            name = repo["name"]
            if name not in PORTRAIT_OF:
                raise SystemExit(f"no portrait mapping for {name}: refusing to default")
            if name not in BLURBS:
                raise SystemExit(f"no blurb mapping for {name}: refusing to default")
            desc = repo.get("description") or ""

            page.set_viewport_size({"width": 1280, "height": 640})
            page.set_content(page_social(name, desc, idx, BLURBS[name],
                                         uri[PORTRAIT_OF[name]], shield_uri))
            page.wait_for_timeout(120)
            page.screenshot(path=str(OUT / "social" / f"{name}.png"))

            page.set_viewport_size({"width": 1200, "height": 300})
            page.set_content(page_readme_banner(name, desc, uri[PORTRAIT_OF[name]]))
            page.wait_for_timeout(80)
            page.screenshot(path=str(OUT / "readme" / f"{name}.png"))

        page.set_viewport_size({"width": 1280, "height": 400})
        page.set_content(page_org_banner(uri["pr0fx"]))
        page.wait_for_timeout(120)
        page.screenshot(path=str(OUT / "org" / "profile-banner.png"))

        page.set_viewport_size({"width": 1280, "height": 640})
        page.set_content(page_org_social(uri["pr0fx"], uri["tiresias"], uri["asphodel"]))
        page.wait_for_timeout(120)
        page.screenshot(path=str(OUT / "org" / "social-preview.png"))

        browser.close()
    print(f"wrote graphics for {len(public)} repos into {OUT}")


if __name__ == "__main__":
    main()
