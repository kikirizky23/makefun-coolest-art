# Make the coolest art — "Aurora over a glass lake"

Entry for the make.fun bounty **"Make the coolest art"**
(https://make.fun/bounty/coolest-art-01) — $250 prize pool, 20 places,
closes Friday 13 Nov 2026 10:00 UTC (17:00 WIB).

## What it draws

A vivid cosmic landscape: a ringed golden planet glowing above a
star-filled indigo sky, three luminous aurora ribbons (green, teal,
violet), a shooting star, twin snow-capped mountain ridges, and a
mirror-still lake that reflects the aurora, the stars and the planet,
with pine silhouettes on the near shore.

## How to run

```sh
python3 main.py            # writes /output/entry.png
ENTRY_PATH=./entry.png python3 main.py   # write somewhere else (testing)
```

- **Language/runtime:** Python 3.13, **stdlib only** — the PNG encoder is
  hand-written (zlib + a small RGB rasterizer), so the program runs in any
  bare Python 3.13 sandbox with no third-party packages and no network.
- **Output:** `/output/entry.png`, 1024×1024 px, RGB PNG.
- **Determinism:** fixed seed (`SEED = 20261113`), no network, no wall
  clock, no timestamps in the PNG. Two runs produce byte-identical output
  (verified: same SHA-256 on repeated runs, see BUILD_LOG.md).

## Files

- `main.py` — the entry program (repo root, as the brief requires)
- `entry.png` — the generated output (678,913 bytes, under the 1 MiB limit)
- `LICENSE` — MIT

## License

MIT — see `LICENSE`.
