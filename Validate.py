import argparse
import os
import struct
import sys
from pathlib import Path
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# RAW STL UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _is_binary(path: str) -> bool:
    with open(path, "rb") as f:
        hdr = f.read(80)
    return not (hdr[:5] == b"solid" and hdr[5:6] in (b" ", b"\n", b"\r"))

def _triangles(path: str) -> np.ndarray:
    tris: list = []
    if _is_binary(path):
        with open(path, "rb") as f:
            f.read(80)
            n = struct.unpack("<I", f.read(4))[0]
            for _ in range(n):
                d = struct.unpack("<12fH", f.read(50))
                tris.append([d[3:6], d[6:9], d[9:12]])
    else:
        verts: list = []
        with open(path, "r", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if s.startswith("vertex"):
                    p = s.split()
                    verts.append([float(p[1]), float(p[2]), float(p[3])])
        for i in range(0, len(verts) - 2, 3):
            tris.append([verts[i], verts[i + 1], verts[i + 2]])
    return np.array(tris, dtype=np.float64)

def _volume(path: str) -> float:
    total = 0.0
    for tri in _triangles(path):
        v1, v2, v3 = tri
        total += float(np.dot(v1, np.cross(v2, v3))) / 6.0
    return abs(total)

def _surface_area(path: str) -> float:
    total = 0.0
    for tri in _triangles(path):
        v1, v2, v3 = tri
        total += float(np.linalg.norm(np.cross(v2 - v1, v3 - v1))) / 2.0
    return total

# ─────────────────────────────────────────────────────────────────────────────
# MAIN VALIDATION LOGIC
# ─────────────────────────────────────────────────────────────────────────────

PARTS = [
    ("Bottom shell",   "mouse_shell_progress_pico_2_bottom.stl",      "mouse_bottom.stl"),
    ("Top shell",      "mouse_shell_progress_pico_2_top.stl",         "mouse_top.stl"),
    ("Thumb button A", "mouse_shell_progress_pico_2_thumb_a.stl",     "Thumb_a.stl"),
    ("Thumb button B", "mouse_shell_progress_pico_2_thumb_b.stl",     "Thumb_b.stl"),
    ("Scroll wheel",   "mouse_shell_progress_pico_2_wheel.stl",       "mouse_scroll_wheel.stl"),
    ("Wheel brace",    "mouse_shell_progress_pico_2_wheel_brace.stl", "mouse_scroll_wheel_brace.stl"),
]

def analyse_pair(label: str, orig: str, rebuilt: str):
    if not os.path.exists(orig) or not os.path.exists(rebuilt):
        print(f"{label:<16} | MISSING FILES")
        return

    # Calculate Volume Error
    orig_vol = _volume(orig)
    rebuilt_vol = _volume(rebuilt)
    vol_err = (abs(orig_vol - rebuilt_vol) / orig_vol * 100) if orig_vol > 0 else 0.0

    # Calculate Surface Area Error
    orig_sa = _surface_area(orig)
    rebuilt_sa = _surface_area(rebuilt)
    sa_err = (abs(orig_sa - rebuilt_sa) / orig_sa * 100) if orig_sa > 0 else 0.0

    print(f"{label:<16} | Volume Error: {vol_err:>7.4f}%  |  Surface Area Error: {sa_err:>7.4f}%")

def main(working_dir: Path) -> None:
    print(f"\n--- Validation Report ---")
    for label, orig_fname, built_fname in PARTS:
        orig    = str(working_dir / orig_fname)
        rebuilt = str(working_dir / built_fname)
        analyse_pair(label, orig, rebuilt)
    print("-------------------------\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate rebuilt mouse-shell STLs against originals.")
    parser.add_argument("--dir",  type=Path, default=Path(__file__).parent,
        help="Folder containing ALL STLs (originals + generated). Default: current directory")
    args = parser.parse_args()

    if not args.dir.is_dir():
        sys.exit(f"[ERROR] Directory not found: {args.dir}")

    main(args.dir)
