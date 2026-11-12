# BUILD_LOG — "Aurora over a glass lake" (coolest-art-01)

Bounty: https://make.fun/bounty/coolest-art-01 — $250, 20 places, closes
Fri 13 Nov 2026 10:00 UTC (17:00 WIB). AI judge compares images pairwise.

## Brief (as read 13 Nov 2026 ~02:07 WIB)

- Program at `main.py` (Python 3.13) in the repo root; writes
  `/output/entry.png`.
- Image: whole PNG or JPEG, at most 1 MiB and 1024×1024 px.
- No network; the program runs twice and both runs must write the same
  bytes (deterministic).
- Deliverables: public GitHub repo under an OSI-approved license (MIT used
  here) + the AI coding-agent transcripts of the sessions that built it,
  uploaded with each submission. Max 10 submissions/day, 20 total; the last
  submission before the deadline is the final entry.
- $250 USDC is locked in the bounty escrow on Solana.

## Approach

- **Stdlib only.** The grading sandbox is Python 3.13, but I could not
  confirm any third-party image library is installed there, so the program
  uses only `math`, `os`, `random`, `struct`, `zlib`. The PNG encoder is
  hand-written (RGB, 8-bit, Up filter per scanline, zlib level 9, correct
  CRCs, no timestamp chunks).
- **Scene choice:** a cosmic aurora landscape — the kind of image that
  reads instantly at thumbnail size and rewards a pairwise "cooler?"
  comparison: strong colour contrast (indigo sky vs green/teal/violet
  aurora vs warm gold planet), a clear focal point (the ringed planet),
  and a reflective lake for symmetry.
- **Composition (1024×1024):** sky 0–640, lake 640–1024; planet at
  (740, 205) r=86; three aurora ribbons at y≈150/295/435; twin mountain
  ridges at the horizon; pine silhouettes at the bottom corners.
- **Determinism:** one fixed seed (`SEED = 20261113`), `random.Random`
  instance only; no `hash()`, no time, no environment-dependent values
  (the `ENTRY_PATH` override only changes where the file lands, never its
  bytes).

## Build steps

1. Read both bounty briefs + `make.fun/skill.md` (13 Nov ~02:07 WIB).
   Confirmed main.py / Python 3.13, `/output/entry.png`, 1 MiB /
   1024×1024 limits, determinism rule.
2. Wrote `main.py` (rasterizer + PNG writer + scene) and ran it.
   - First run failed: `TypeError` — mountain ridge `top` was a float;
     fixed with `int(...)`.
3. Visual check v1: good overall, but (a) aurora bands showed contour
   banding, (b) the planet was too dark/brown, (c) its lake reflection
   was a wide pink blob, (d) the shooting star was barely visible.
4. Iteration v2: softer aurora falloff (`exp(-u²·3)`) + deterministic
   per-pixel dither (±8 alpha) to break contours; brighter planet
   (lighter base, wider light range); thicker ring annulus; narrower,
   dimmer, golden planet reflection; longer/brighter shooting star.
   Visual check v2: accepted — planet reads golden, ring is clear,
   aurora ribbons are smooth, reflection is a narrow golden smear.
   (The aurora keeps a fine stylized texture from the dither; it reads as
   part of the ribbon style.)

## Test results (final, 13 Nov 2026 ~02:10 WIB)

- Runtime: ~2.2 s per run (local Python 3.12.3; target is Python 3.13).
- Determinism: ran twice with `ENTRY_PATH` set, then once with the
  default `/output/entry.png` path — all three outputs byte-identical.
  SHA-256: `967b722cd5ad924f40fb2dd3a928900606980c5e998fbabc210d4bdc60b9caf8`
- PNG validity: header + IHDR parse OK (1024×1024, 8-bit, colour type 2
  RGB); IDAT decompresses to exactly 1024 × (1 + 1024×3) bytes.
- Size: **678,913 bytes** — under the 1,048,576-byte limit.
- Dimensions: 1024×1024 — at the limit, allowed.
- Visual check: viewed the rendered PNG — subject clearly visible,
  not blank, not broken.

## Submission notes (for the parent agent, not done by this build)

- Nothing was submitted to make.fun and no GitHub repo was created.
- To submit: create a public GitHub repo (owner: Rizki's account) with
  `main.py` + `README.md` + `LICENSE` at its root, then submit it with
  the AI-agent transcripts of the sessions that built it (this build's
  transcript lives in the parent agent's conversation).
- The program writes `/output/entry.png` by default; `ENTRY_PATH` only
  exists for local testing and does not affect the output bytes.
