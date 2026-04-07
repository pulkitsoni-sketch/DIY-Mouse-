import os
from pathlib import Path
from build123d import import_stl, export_stl, Compound, Location

# Attempt to import the viewer components
try:
    from ocp_vscode import show_object, set_defaults, Camera
    HAS_VIEWER = True
except ImportError:
    HAS_VIEWER = False
    print("ocp_vscode not found. Script will only export the STL.")

# Directory configuration
DIR = Path("./output") 
DIR.mkdir(exist_ok=True)

# Define the parts and their corresponding STL filenames
PARTS_MAP = {
    "thumb_a": "thumb_a.stl",
    "thumb_b": "thumb_b.stl",
    "wheel": "mouse_scroll_wheel.stl",
    "wheel_brace": "mouse_scroll_wheel_brace.stl",
    "top": "mouse_top.stl",
    "bottom": "mouse_bottom.stl",
}

# --- UPDATED: Removed "bottom" from suppression list ---
SUPPRESS_PARTS = ["top"]

# --- UPDATED: Added color for the bottom shell ---
COLOURS = {
    "thumb_a": (230, 75, 75),    # Red
    "thumb_b": (230, 130, 50),   # Orange
    "wheel": (50, 200, 75),      # Green
    "wheel_brace": (200, 200, 50), # Yellow
    "bottom": (100, 100, 100),   # Grey
}

def main():
    faces = []
    parts_to_show = {}

    print(f"Assembling parts from: {DIR.absolute()}")

    for name, filename in PARTS_MAP.items():
        if name in SUPPRESS_PARTS:
            print(f"[-] Suppressing: {name}")
            continue

        path = DIR / filename
        if path.exists():
            shape = import_stl(str(path))
            # If your bottom shell needs to be the origin, 
            # ensure other parts are moved relative to it here.
            shape.move(Location()) 
            
            faces.append(shape)
            parts_to_show[name] = shape
            print(f"[✓] Loaded: {name}")
        else:
            print(f"[!] Skip: {filename} not found.")

    if faces:
        # 1. Export the physical STL file
        assembly = Compound(faces)
        # Renamed to 'full' for clarity
        export_path = DIR / "mouse_assembly_full.stl"
        export_stl(assembly, str(export_path))
        print(f"\nAssembly exported to {export_path}")

        # 2. Show in OCP Viewer
        if HAS_VIEWER:
            set_defaults(reset_camera=Camera.RESET)
            for name, shape in parts_to_show.items():
                color = COLOURS.get(name, (200, 200, 200))
                show_object(shape, name=name, options={"color": color, "alpha": 1.0})
            print("Displaying assembly in ocp_vscode viewer.")
    else:
        print("No parts were found to assemble.")

if __name__ == "__main__":
    main()
