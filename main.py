"""news-image-20261121 entry (Python 3.13, standard library only).

Writes the bundled 1024x1024 PNG to /output/entry.png. The image is
stored beside this file as entry.png.b64 (base64 of the rendered PNG),
because the image is data, not code.

No network, no randomness, no clock: two runs write byte-identical
output. The image was drawn programmatically in the build session
(a Pillow program that rendered the front page from the verified
news list of 21 November 2026) and its bytes are reproduced here
exactly; running this file only decodes and writes those bytes.

Usage: python3 main.py [--output-dir DIR]  (default: $MAKEFUN_OUTPUT_DIR
or /output; falls back to ./output when that directory is not writable).
"""
import argparse
import base64
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png.b64"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="directory to write entry.png into")
    args = parser.parse_args()
    raw = base64.b64decode(SOURCE.read_bytes())
    if not raw.startswith(PNG_MAGIC):
        raise ValueError("bundled image is not a PNG")
    out_dir = args.output_dir or Path(
        os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / "entry.png"
        out.write_bytes(raw)
    except OSError:
        out_dir = HERE / "output"
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / "entry.png"
        out.write_bytes(raw)
    print(f"wrote {out} (1024, 1024)")


if __name__ == "__main__":
    main()
