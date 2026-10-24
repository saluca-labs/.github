![Saluca Labs](assets/banner.png)

# saluca-labs/.github

Org-level files for [Saluca Labs](https://github.com/saluca-labs): the profile README that renders
on the org page, the shared artwork, and the generator that produced it.

This repo holds no product code. It is the shopfront.

## What is here

| Path | What it is |
|---|---|
| [`profile/README.md`](profile/README.md) | The org page profile. GitHub renders this file at `github.com/saluca-labs`. |
| `assets/banner.png` | Header banner, 1280 x 400. |
| `assets/social-preview.png` | Org social preview, 1280 x 640, a triptych of the three portraits. |
| `assets/readme/<repo>.jpg` | Per-repo README header, 1200 x 300, one for each of the 18 public repos. |
| `assets/portraits/` | The three portraits and the Saluca shield that the art is built from. |
| `tools/cardgen.py` | The generator. Renders HTML/CSS with Playwright at exact pixel size. |
| `tools/org_repos.json` | The repo metadata the generator ran against, so a rerun is reproducible. |

## Using a header in a repo README

Add one line as the first line of a repo's README, with `<repo>` replaced by that repo's name:

```markdown
![<repo>](https://github.com/saluca-labs/.github/raw/HEAD/assets/readme/<repo>.jpg)
```

`HEAD` resolves to whichever branch is the default, so the link keeps working if the default branch
is renamed.

That keeps every banner in one place, so a change here reaches all 18 repos without a commit in
any of them.

## Regenerating the art

```bash
python -m pip install playwright pillow
python -m playwright install chromium
python tools/cardgen.py --repos tools/org_repos.json --out ../out
```

`cardgen.py` takes the repo list as JSON, reads the portraits from `assets/portraits/`, and writes
`social/<repo>.png` and `readme/<repo>.png` into `--out`. It raises rather than guessing: a repo
with no portrait mapping or no blurb stops the run, so a new repo has to be assigned a portrait
deliberately rather than inheriting one.

## Design

The palette is sampled from the three cyberpunk portraits: deep indigo ground, neon cyan
`#22e8ff`, neon magenta `#ff3fe0`, violet `#8b5cf6`, and the chrome of the Saluca shield as the
title metal. Portraits are assigned per repo family: pr0fx for research and physics, Tiresias for
security, detection and verification, Asphodel for memory, persistence and context.

Text on a card is never text that the repo does not already carry: each card repeats the repo name
and its GitHub description, with em-dashes and en-dashes normalised to a hyphen to house style.

## Social previews

GitHub has no API for the social preview image. Each repo carries its own, uploaded by hand at
repo Settings > Social preview. `assets/readme/` is the in-repo copy; the 1280 x 640 upload sources
are kept outside this repo because they are not read from it.

## License

No license is granted for the artwork. The generator script in `tools/` is available to read.

_Last updated: 2026-10-23_
