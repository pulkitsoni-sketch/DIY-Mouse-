from ocp_vscode import show, Camera
from build123d import *

# ---------- Previous part ----------
sketch_plane = Plane(
    origin=(0, -1.335, 0),
    x_dir=(1, 0, 0),
    z_dir=(0, -1, 0)
)

prev_points = [
    (-23.598, 21.227),
    (-23.348, 18.227),
    (-23.348, 14.805),
    (-22.598, 13.305),
    (-16.848, 13.572),
    (-20.848, 19.727),
]

with BuildPart() as prev_part:
    with BuildSketch(sketch_plane):
        with BuildLine():
            for i in range(len(prev_points)):
                Line(prev_points[i], prev_points[(i + 1) % len(prev_points)])
        make_face()
    extrude(amount=7)

# ---------- Loft profiles ----------
bottom_pts = [
    (-23.348, -8.335, 18.227),
    (-31.848, -8.335, 18.227),
    (-32.848, -6.335, 18.227),
    (-32.348, 1.665, 18.227),
    (-31.348, 3.665, 18.227),
    (-28.848, 3.665, 18.227),
    (-26.848, 1.665, 18.227),
    (-23.348, -1.335, 18.227),
]

mid_pts = [
    (-23.598, -8.335, 20.227),
    (-31.848, -8.335, 20.227),
    (-32.848, -6.335, 20.227),
    (-32.348, 1.665, 20.227),
    (-31.348, 3.665, 20.227),
    (-27.848, 3.665, 20.227),
    (-25.848, 1.665, 20.227),
    (-24.348, -1.335, 20.227),
    (-23.598, -1.335, 20.227),
]

top_pts = [
    (-23.598, -8.335, 22.227),
    (-30.848, -8.335, 22.227),
    (-31.848, -6.335, 22.227),
    (-31.348, 1.665, 22.227),
    (-30.348, 3.665, 22.227),
    (-27.848, 3.665, 22.227),
    (-25.848, 1.665, 22.227),
    (-24.348, -1.335, 22.227),
    (-23.598, -1.335, 22.227),
]

def make_wire(pts):
    edges = []
    for i in range(len(pts)):
        edges.append(Edge.make_line(pts[i], pts[(i + 1) % len(pts)]))
    return Wire(edges)

bottom_wire = make_wire(bottom_pts)
mid_wire    = make_wire(mid_pts)
top_wire    = make_wire(top_pts)

loft1 = Solid.make_loft([bottom_wire, mid_wire], ruled=True)
loft2 = Solid.make_loft([mid_wire, top_wire],   ruled=True)

result = prev_part.part
result = result.fuse(loft1)
result = result.fuse(loft2)

# ---------- Zigzag body ----------
zigzag_plane = Plane(
    origin=(0, -4.435, 0),
    x_dir=(1, 0, 0),
    z_dir=(0, -1, 0)
)

zigzag_pts = [
    (-25.848, 18.227),
    (-26.848, 17.227),
    (-25.848, 16.227),
    (-26.848, 15.227),
    (-25.848, 14.227),
    (-26.848, 13.227),
    (-25.848, 12.227),
    (-26.848, 11.227),
    (-25.848, 10.227),
    (-26.848, 9.227),
    (-25.848, 8.227),
    (-26.848, 8.227),
    (-27.848, 9.227),
    (-26.848, 10.227),
    (-27.848, 11.227),
    (-26.848, 12.227),
    (-27.848, 13.227),
    (-26.848, 14.227),
    (-27.848, 15.227),
    (-26.848, 16.227),
    (-27.848, 17.227),
    (-26.848, 18.227),
]

with BuildPart() as zigzag:
    with BuildSketch(zigzag_plane):
        with BuildLine():
            for i in range(len(zigzag_pts)):
                Line(zigzag_pts[i], zigzag_pts[(i + 1) % len(zigzag_pts)])
        make_face()
    extrude(amount=3.8)

result = result.fuse(zigzag.part)

# ---------- Zigzag loft ----------
r1_wire = Wire([
    Edge.make_line((-25.848, -4.435, 8.227), (-26.848, -4.435, 8.227)),
    Edge.make_line((-26.848, -4.435, 8.227), (-26.848, -8.235, 8.227)),
    Edge.make_line((-26.848, -8.235, 8.227), (-25.848, -8.235, 8.227)),
    Edge.make_line((-25.848, -8.235, 8.227), (-25.848, -4.435, 8.227)),
])

r2_wire = Wire([
    Edge.make_line((-26.348, -0.435, 7.227), (-27.348, -0.435, 7.227)),
    Edge.make_line((-27.348, -0.435, 7.227), (-27.348, -8.235, 7.227)),
    Edge.make_line((-27.348, -8.235, 7.227), (-26.348, -8.235, 7.227)),
    Edge.make_line((-26.348, -8.235, 7.227), (-26.348, -0.435, 7.227)),
])

zigzag_loft = Solid.make_loft([r1_wire, r2_wire], ruled=True)
result = result.fuse(zigzag_loft)

# ---------- New profile at Y=-0.435 ----------
new_plane = Plane(
    origin=(0, -0.435, 0),
    x_dir=(1, 0, 0),
    z_dir=(0, -1, 0)
)

profile_pts = [
    (-27.348, 7.227),
    (-26.348, 6.227),
    (-26.348, 4.227),
    (-25.848, 3.227),
    (-24.848, 3.227),
    (-23.848, 3.624),
    (-22.848, 3.624),
    (-22.848, 4.624),
    (-23.848, 4.624),
    (-25.348, 4.227),
    (-25.348, 6.227),
    (-24.348, 6.227),
    (-23.848, 7.227),
    (-22.848, 6.227),
    (-21.848, 6.227),
    (-21.848, 12.227),
    (-24.848, 12.227),
    (-24.848, 8.227),
    (-25.348, 7.227),
    (-26.348, 7.227),
]

with BuildPart() as new_profile:
    with BuildSketch(new_plane):
        with BuildLine():
            for i in range(len(profile_pts)):
                Line(profile_pts[i], profile_pts[(i + 1) % len(profile_pts)])
        make_face()
    extrude(amount=7.8)

result = result.fuse(new_profile.part)

# ---------- Extrude face from X=-21.848 to X=-9.048 ----------
src_wire = Wire([
    Edge.make_line((-21.848, -0.435, 6.227), (-21.848, -0.435, 12.227)),
    Edge.make_line((-21.848, -0.435, 12.227), (-21.848, -8.235, 12.227)),
    Edge.make_line((-21.848, -8.235, 12.227), (-21.848, -8.235, 6.227)),
    Edge.make_line((-21.848, -8.235, 6.227), (-21.848, -0.435, 6.227)),
])

tgt_wire = Wire([
    Edge.make_line((-9.048, -0.635, 6.227), (-9.048, -0.635, 12.227)),
    Edge.make_line((-9.048, -0.635, 12.227), (-9.048, -8.435, 12.227)),
    Edge.make_line((-9.048, -8.435, 12.227), (-9.048, -8.435, 6.227)),
    Edge.make_line((-9.048, -8.435, 6.227), (-9.048, -0.635, 6.227)),
])

face_extrude = Solid.make_loft([src_wire, tgt_wire], ruled=True)
result = result.fuse(face_extrude)

# ---------- Bottom plate profile at Z=6.227 (CUTTING extrude) ----------
bottom_plate_plane = Plane(
    origin=(0, 0, 6.227),
    x_dir=(1, 0, 0),
    z_dir=(0, 0, 1)
)

bottom_plate_pts = [
    (-21.848, -0.3),
    (-22.848, -1.435),
    (-22.848, -7.235),
    (-9.848, -7.235),
    (-10.048, -1.435),
    (-11.048, -0.935),
    (-11.048, -0.835),
    (-10.048, -0.5),
]

with BuildPart() as bottom_plate:
    with BuildSketch(bottom_plate_plane):
        with BuildLine():
            for i in range(len(bottom_plate_pts)):
                Line(bottom_plate_pts[i], bottom_plate_pts[(i + 1) % len(bottom_plate_pts)])
        make_face()
    extrude(amount=6)

result = result - bottom_plate.part

# ---------- Mirror about XZ plane at Y = -8.435 - 10.075/2 ----------
# Bottom-most Y in the part = -8.435 (from tgt_wire / loft bottom faces)
# Mirror plane offset = 10.075/2 = 5.0375 mm in -Y direction
# Mirror plane Y = -8.435 - 5.0375 = -13.4725

mirror_y = -8.435 - 10.075 / 2  # = -13.4725

mirror_plane = Plane(
    origin=(0, mirror_y, 0),
    x_dir=(1, 0, 0),
    z_dir=(0, 1, 0)   # normal is Y-axis → XZ plane
)

mirrored = result.mirror(mirror_plane)

# ---------- SHOW ----------
show(result, reset_camera=Camera.RESET)
