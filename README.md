# PoE Endgame Poster

The content and progression live in `spec.yaml`. The HTML layout lives in `template.html`.
`generate.py` combines them into a self-contained `dist/index.html`.

## Build

```bash
python -m pip install -r requirements.txt
python generate.py
```

## Preview locally

```bash
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`.

## Intended viewing size

The working poster width is **2048 CSS pixels**. The layout deliberately does not reflow on narrow screens;
the browser will scroll horizontally instead of crushing the boss crown.

Recommended viewing:

- 2560px-wide monitor: browser zoom 100%.
- 1920px-wide monitor: browser zoom around 80–85%.
- 1440px-wide monitor: browser zoom around 67–70%.
- For content review, keep the browser at 100% and scroll horizontally/vertically.
- For a whole-poster overview, zoom out. Do not judge text size at overview zoom.

## Updating for a league

Edit only `spec.yaml` for most changes:

- reorder or rename stages;
- add/remove bosses;
- change `final: true`;
- add a reward to `badges` (later rendered as an icon);
- move a branch in the crown by reordering entries in `bossCrown`;
- edit league mechanics in `mechanics`.

Then rerun:

```bash
python generate.py
```

## Future icons

The intended model is to replace text badges with icon IDs, for example:

```yaml
badges:
  - icon: voidstone
    label: Voidstone
```

Icon files can live in `assets/icons/`. The template can then map IDs such as `voidstone`, `catalyst`,
`oil`, and `timeless-jewel` to local SVG/PNG assets.
