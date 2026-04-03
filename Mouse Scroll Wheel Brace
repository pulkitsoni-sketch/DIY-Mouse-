from ocp_vscode import show, Camera
from build123d import *
import math

# ---------- Main body ----------
sketch_plane = Plane(
    origin=(7.561, 0, 0),
    x_dir=(0, 1, 0),
    z_dir=(1, 0, 0)
)

points = [
    (8.735, 6.254),
    (8.735, 12.754),
    (12.083, 12.754),
    (12.667, 14),
    (13.667, 18.754),
    (14.667, 18.754),
    (14.667, 14),
    (16.656, 12.004),
    (20.573, 12.004),
    (22.571, 14),
    (22.571, 18.754),
    (23.571, 18.754),
    (24.571, 14),
    (24.435, 12.754),
    (24.435, 6.254),
]

with BuildPart() as brace:
    with BuildSketch(sketch_plane):
        with BuildLine():
            for i in range(len(points)):
                Line(points[i], points[(i + 1) % len(points)])
        make_face()
    extrude(amount=1)

# ---------- Middle rectangles for loft targets ----------
r1_p1 = (14.261, 9.235, 12.754)
r1_p2 = (14.387, 10.235, 12.754)
r1_p3 = (14.387, 10.235, 6.254)
r1_p4 = (14.261, 9.235, 6.254)

rect1_wire = Wire([
    Edge.make_line(r1_p1, r1_p2),
    Edge.make_line(r1_p2, r1_p3),
    Edge.make_line(r1_p3, r1_p4),
    Edge.make_line(r1_p4, r1_p1),
])

r2_p1 = (14.261, 23.935, 12.754)
r2_p2 = (14.387, 22.935, 12.754)
r2_p3 = (14.387, 22.935, 6.254)
r2_p4 = (14.261, 23.935, 6.254)

rect2_wire = Wire([
    Edge.make_line(r2_p1, r2_p2),
    Edge.make_line(r2_p2, r2_p3),
    Edge.make_line(r2_p3, r2_p4),
    Edge.make_line(r2_p4, r2_p1),
])

# Back face rectangle wires for lofting (at X=8.561)
bl_p1 = (8.561, 8.735, 12.754)
bl_p2 = (8.561, 9.735, 12.754)
bl_p3 = (8.561, 9.735, 6.254)
bl_p4 = (8.561, 8.735, 6.254)

back_lower_wire = Wire([
    Edge.make_line(bl_p1, bl_p2),
    Edge.make_line(bl_p2, bl_p3),
    Edge.make_line(bl_p3, bl_p4),
    Edge.make_line(bl_p4, bl_p1),
])

bu_p1 = (8.561, 24.435, 12.754)
bu_p2 = (8.561, 23.435, 12.754)
bu_p3 = (8.561, 23.435, 6.254)
bu_p4 = (8.561, 24.435, 6.254)

back_upper_wire = Wire([
    Edge.make_line(bu_p1, bu_p2),
    Edge.make_line(bu_p2, bu_p3),
    Edge.make_line(bu_p3, bu_p4),
    Edge.make_line(bu_p4, bu_p1),
])

# Lofts
lower_loft = Solid.make_loft([back_lower_wire, rect1_wire], ruled=True)
upper_loft = Solid.make_loft([back_upper_wire, rect2_wire], ruled=True)

result = brace.part
result = result.fuse(lower_loft)
result = result.fuse(upper_loft)

# ---------- Bottom tab (Z=6.254 to Z=12.754) ----------
tab_points_bottom = [
    (14.261, 9.235),
    (15.261, 9.235),
    (15.261, 11.235),
    (14.761, 11.735),
    (14.261, 11.235),
    (14.387, 10.235),
]

with BuildPart() as tab_bottom:
    with BuildSketch(Plane(
        origin=(0, 0, 6.254),
        x_dir=(1, 0, 0),
        z_dir=(0, 0, 1)
    )):
        with BuildLine():
            for i in range(len(tab_points_bottom)):
                Line(tab_points_bottom[i], tab_points_bottom[(i + 1) % len(tab_points_bottom)])
        make_face()
    extrude(amount=12.754 - 6.254)

result = result.fuse(tab_bottom.part)

# ---------- Top tab (mirrored, facing toward center i.e. -Y) ----------
# Bottom tab starts at (14.261, 9.235) and features go in +Y
# Top tab starts at (14.261, 23.935) and features go in -Y
tab_points_top = [
    (14.261, 23.935),
    (15.261, 23.935),
    (15.261, 21.935),
    (14.761, 21.435),
    (14.261, 21.935),
    (14.387, 22.935),
]

with BuildPart() as tab_top:
    with BuildSketch(Plane(
        origin=(0, 0, 6.254),
        x_dir=(1, 0, 0),
        z_dir=(0, 0, 1)
    )):
        with BuildLine():
            for i in range(len(tab_points_top)):
                Line(tab_points_top[i], tab_points_top[(i + 1) % len(tab_points_top)])
        make_face()
    extrude(amount=12.754 - 6.254)

result = result.fuse(tab_top.part)

# ---------- SHOW ----------
show(result, reset_camera=Camera.RESET)
