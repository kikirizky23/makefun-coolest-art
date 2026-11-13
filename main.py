"""Weaving the Aurora -- make.fun coolest art entry (copy-style).

The artwork is an original photorealistic scene made for this entry:
colossal silhouetted weavers standing on a cliff, weaving luminous
emerald-green and violet aurora ribbons across a starry night sky
above a mirror-still fjord, watched by a tiny red-cloaked figure.

The image ships beside this program as entry.png; this program copies
it to the competition output directory. No drawing, no network, no
randomness -- the output is byte-identical to the shipped image.
"""

import hashlib
import os
import shutil
from pathlib import Path

SOURCE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"


def main() -> None:
    source = Path(__file__).resolve().parent / SOURCE_NAME
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))
    out_dir.mkdir(parents=True, exist_ok=True)
    destination = out_dir / SOURCE_NAME
    shutil.copyfile(source, destination)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    size = destination.stat().st_size
    print(f"wrote {destination} ({size} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
