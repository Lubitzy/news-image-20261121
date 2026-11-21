"""Copy the committed original news image to the sandbox output directory."""

import argparse
from pathlib import Path
from shutil import copyfile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("/output"))
    args = parser.parse_args()
    source = Path(__file__).resolve().parent / "assets" / "entry.png"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    copyfile(source, args.output_dir / "entry.png")


if __name__ == "__main__":
    main()
