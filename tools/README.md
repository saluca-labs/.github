# cardgen

Renders the Saluca Labs card art: HTML and CSS screenshotted by Playwright at exact pixel size, so
the output is a real 1280 x 640 or 1200 x 300 image rather than a scaled one.

## Install

```bash
python -m pip install playwright pillow
python -m playwright install chromium
```

## Run

```bash
python cardgen.py --repos org_repos.json --out ../out
```

| Flag | Default | Meaning |
|---|---|---|
| `--repos` | `org_repos.json` | A `gh repo list saluca-labs --json name,description,visibility` dump. Only `PUBLIC` repos are rendered. |
| `--shield` | `org-avatar.png` | The Saluca shield, used as the small badge. |
| `--out` | `out` | Output root. Gets `social/`, `readme/` and `org/`. |

Inputs the script reads from its own directory: `pr0fx.jpg`, `tiresias.jpg`, `asphodel.jpg`.

## Output

| File | Size | Use |
|---|---|---|
| `social/<repo>.png` | 1280 x 640 | Repo Settings > Social preview |
| `readme/<repo>.png` | 1200 x 300 | Header at the top of a repo README |
| `org/profile-banner.png` | 1280 x 400 | Org profile header |
| `org/social-preview.png` | 1280 x 640 | Org Settings > Profile > Social preview |

## Behaviour worth knowing

- **It refuses to guess.** A repo missing from `PORTRAIT_OF` or `BLURBS` raises. Adding a public
  repo means deciding its portrait family and its one-line blurb, on purpose.
- **It normalises punctuation.** `dash()` turns em-dashes and en-dashes into a plain hyphen before
  rendering, because house style has no em-dashes anywhere, including inside an image.
- **It fits the title.** The title size is computed from the repo name's length and clamped, so a
  long name like `borrowed-trust-detections` shrinks instead of clipping the panel.
- **It resets the viewport per render.** Each card sets the viewport to its own size before
  screenshotting; skipping this crops the wider cards to the previous card's height.
