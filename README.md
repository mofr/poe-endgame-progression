# PoE Endgame Poster

A poster of the Path of Exile endgame: the pinnacle boss crown on top, league/system
progression below, rendered over official-style art with Fontin typography.

The content and progression live in `spec.yaml`. The HTML layout lives in `template.html`.
`generate.py` combines them into `dist/` — `index.html` plus the `icons/`, `art/`, and
`fonts/` folders it references, so `dist/` is fully self-contained and offline-viewable.

## Build

```bash
python -m pip install -r requirements.txt
python generate.py
```

The first build downloads badge icons from poewiki.net into the `assets/icons/` cache
(with backoff for the wiki's rate limiting); subsequent builds are fully offline.

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
- add rewards to `badges`;
- move a branch in the crown by reordering entries in `bossCrown`
  (keep the `span` values summing to `layout.crown_columns`);
- edit league mechanics in `mechanics`.

Then rerun:

```bash
python generate.py
```

## Badges (reward icons)

Badges render as game item icons with the label as a hover tooltip:

```yaml
badges:
  - label: Voidstone
    icon: https://www.poewiki.net/wiki/Special:FilePath/Grasping_Voidstone_inventory_icon.png
```

Any poewiki item works via `https://www.poewiki.net/wiki/Special:FilePath/<Item_Name>_inventory_icon.png`.
The generator downloads each icon once into `assets/icons/` and ships it to `dist/icons/`.
A badge given as a plain string renders as a text pill instead.

## Art backdrops

Branches and mechanics can carry a backdrop from `assets/art/`:

```yaml
art: eater-of-worlds.png        # file in assets/art/
artPos: calc(50% + 7px) -45px   # offset  — CSS background-position
artSize: 110%                   # scale   — CSS background-size (default: cover)
artDim: 1.2                     # overlay — 0 raw art .. 1 default darkening .. higher darker
artBlend: multiply              # blend vs the tinted base (for white-background art)
```

Mechanics additionally support `headerArt:` — a league logo image that replaces the
header pill. Only art files referenced by the spec are copied into `dist/art/`.

## Fonts

Fontin and Fontin SmallCaps (the classic PoE typefaces) are bundled in `assets/fonts/`
and shipped to `dist/fonts/`.
