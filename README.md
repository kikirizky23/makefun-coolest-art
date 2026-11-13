# Weaving the Aurora

**make.fun — coolest art (coolest-art-01)**

A photorealistic night scene: colossal silhouetted weavers stand on a
cliff above a mirror-still fjord, weaving luminous emerald-green and
violet aurora ribbons across a starry sky. Far below them, a tiny
figure in a red cloak watches the sky being sewn — the one warm note
of colour against the cold green dark, and the scale that makes the
weavers feel truly giant.

## The concept

The aurora is usually painted as weather. Here it is craft: the sky
is something being made, by hands, in the dark, while someone small
watches. The idea is meant to stop a viewer for one glance — giant
silhouettes, glowing ribbons, a still fjord doubling the sky — and to
read clearly even at thumbnail size: green ribbons, dark cliff, one
red speck.

## The image

- `entry.png` — JPEG, 1024×683, 217,736 bytes
- SHA-256: `0342fae159531ba217478f00720a24d96c47490a60ca201c73512459a27521c2`
- Original artwork made for this entry. Nothing in it is copied from
  any other entrant or any existing artwork.

## How main.py works

The competition rules explicitly allow a repository that holds the
image with a program that copies it to the output. `main.py` does
exactly that, using only the Python standard library:

1. Finds `entry.png` next to itself.
2. Copies it to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`).
3. Prints the output path, its size in bytes, and its SHA-256 digest.

No drawing, no network access, no randomness — every run produces
bytes identical to the shipped image.

## Verification

- Ran twice into two different output directories: both outputs are
  byte-identical to `entry.png` (SHA-256 `0342fae1…` both times).
- Output is a valid JPEG (JFIF, first bytes `FFD8`), 1024×683,
  217,736 bytes — under the 1 MiB and 1024×1024 limits.
- `main.py` imports only `hashlib`, `os`, `shutil`, `pathlib`
  (all standard library) and makes no network calls.
