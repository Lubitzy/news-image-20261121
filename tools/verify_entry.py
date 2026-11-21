"""Verify this entry using only the Python standard library.

Both isolated child runs deny socket operations, disable site packages, and
write into different empty directories. The PNG checks target the renderer's
8-bit RGB, non-interlaced output rather than claiming a universal PNG decoder.
"""

import argparse
import ast
import binascii
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
NETWORK_GUARD = r"""
import runpy
import sys

def deny_network(event, arguments):
    if event.startswith('socket.') or event == 'urllib.Request':
        raise RuntimeError('Network access is forbidden during verification')

sys.addaudithook(deny_network)
entry, output = sys.argv[1:]
sys.argv = [entry, '--output-dir', output]
runpy.run_path(entry, run_name='__main__')
"""


def png_info(data: bytes) -> dict:
    if len(data) > 1_048_576 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG within the byte cap")
    offset = 8
    chunks = []
    compressed = bytearray()
    header = None
    ended = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("Truncated PNG chunk")
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        stop = offset + 12 + length
        if stop > len(data):
            raise ValueError("Chunk exceeds file length")
        payload = data[offset + 8:offset + 8 + length]
        checksum = struct.unpack_from(">I", data, offset + 8 + length)[0]
        if binascii.crc32(kind + payload) & 0xFFFFFFFF != checksum:
            raise ValueError("PNG checksum mismatch")
        if not chunks and kind != b"IHDR":
            raise ValueError("IHDR must be first")
        chunks.append(kind.decode("ascii"))
        if kind == b"IHDR":
            if header is not None or length != 13:
                raise ValueError("Invalid IHDR")
            header = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            if length != 0 or stop != len(data):
                raise ValueError("Invalid IEND or trailing bytes")
            ended = True
        offset = stop
    if not header or not ended or not compressed:
        raise ValueError("Incomplete PNG")
    width, height, depth, color, compression, filtering, interlace = header
    if not (0 < width <= 1024 and 0 < height <= 1024):
        raise ValueError("Dimensions exceed the limits")
    if (depth, color, compression, filtering, interlace) != (8, 2, 0, 0, 0):
        raise ValueError("Expected non-interlaced 8-bit RGB")
    stride = 1 + width * 3
    expected = stride * height
    decoder = zlib.decompressobj()
    raw = decoder.decompress(bytes(compressed), expected + 1)
    if len(raw) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError("Invalid or unexpected image-data stream")
    if any(raw[row * stride] > 4 for row in range(height)):
        raise ValueError("Invalid scanline filter")
    return {"format": "PNG", "width": width, "height": height, "bytes": len(data),
            "bit_depth": depth, "color_type": "RGB", "all_chunk_crcs_valid": True,
            "image_stream_complete": True, "scanline_filters_valid": True,
            "chunk_count": len(chunks)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, default=ROOT / ".verification")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    args.work_dir.mkdir(parents=True, exist_ok=True)
    entrypoint = ROOT / "main.py"
    tree = ast.parse(entrypoint.read_text(encoding="utf-8"), feature_version=(3, 13))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    if not imports <= sys.stdlib_module_names:
        raise ValueError("Entrypoint imports a non-standard-library module")
    outputs = []
    with tempfile.TemporaryDirectory(prefix="news-image-check-", dir=args.work_dir) as scratch:
        for index in range(2):
            output_dir = Path(scratch) / f"run-{index + 1}"
            completed = subprocess.run(
                [sys.executable, "-I", "-S", "-c", NETWORK_GUARD,
                 str(entrypoint), str(output_dir)],
                capture_output=True, text=True, timeout=10, check=True,
            )
            if completed.stdout or completed.stderr:
                raise ValueError("Unexpected entrypoint output")
            outputs.append((output_dir / "entry.png").read_bytes())
    asset = (ROOT / "assets" / "entry.png").read_bytes()
    if outputs[0] != outputs[1] or outputs[0] != asset:
        raise ValueError("Runs or committed source asset differ")
    report = {
        "status": "pass",
        "python_version": sys.version.split()[0],
        "entrypoint_stdlib_imports": sorted(imports),
        "isolation_flags": ["-I", "-S"],
        "socket_operations_denied": True,
        "independent_runs": 2,
        "runs_byte_identical": True,
        "output_matches_source_asset": True,
        "sha256": hashlib.sha256(asset).hexdigest(),
        "png": png_info(asset),
    }
    serialized = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
