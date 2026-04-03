from ocp_vscode import show, Camera
from build123d import *
import math

# ---------- PARAMETERS ----------
center = (13.111, 18.604, 17.278)
radius1 = 7.417 / 2
radius2 = 5.114 / 2 

yz_plane = Plane(
    origin=center,
    x_dir=(0, 1, 0),
    z_dir=(1, 0, 0)
)

# ---------- BUILD EVERYTHING ----------
with BuildPart() as part:

    # Base hollow cylinder
    with BuildSketch(yz_plane):
        Circle(radius1)
        Circle(radius2, mode=Mode.SUBTRACT)
    
    extrude(amount=-9.538)

    # Step with taper
    bottom_face = part.faces().sort_by(Axis.X)[0]
    extrude(bottom_face, amount=1.464, taper=-3.595)

# --- Build loft outside the context ---
bottom_face_2 = part.faces().sort_by(Axis.X)[0]
bf2_center = bottom_face_2.center()
target_center = bf2_center + Vector(-5, 0, 0)

target_plane = Plane(
    origin=target_center,
    x_dir=(0, 1, 0),
    z_dir=(1, 0, 0)
)

bf2_wires = bottom_face_2.wires().sort_by(SortBy.LENGTH)
outer_wire = Wire([Edge.make_circle(11.3 / 2, target_plane)])

outer_loft = Solid.make_loft([bf2_wires[-1], outer_wire])
result = part.part.fuse(outer_loft)

# --- Extruded annular ring ---
circle_center = (3.573, 18.604, 17.278)
ring_end_x = 3.573 - 6.923

circle_plane = Plane(
    origin=circle_center,
    x_dir=(0, 1, 0),
    z_dir=(1, 0, 0)
)

with BuildPart() as ring:
    with BuildSketch(circle_plane):
        Circle(24.516 / 2)
        Circle(20.835 / 2, mode=Mode.SUBTRACT)
    extrude(amount=-6.923)

result = result.fuse(ring.part)

# --- Revolve profile connecting loft bottom to ring bottom ---
rev_axis = Axis((0, 18.604, 17.278), (1, 0, 0))

loft_bottom_x = -3.351
loft_outer_r = 11.3 / 2
ring_outer_r = 24.516 / 2
ring_inner_r = 20.835 / 2

profile_plane = Plane(
    origin=(0, 18.604, 17.278),
    x_dir=(1, 0, 0),
    z_dir=(0, 0, 1)
)

with BuildSketch(profile_plane) as profile:
    Polygon(
        (loft_bottom_x, loft_outer_r),
        (circle_center[0], ring_outer_r),
        (ring_end_x, ring_outer_r),
        (ring_end_x, ring_inner_r),
        (circle_center[0], ring_inner_r),
        (loft_bottom_x, ring_inner_r),
        align=None
    )

revolved = revolve(profile.sketch, axis=rev_axis)
result = result.fuse(revolved)

# --- Extrude bottom face to X = -3.351 ---
bottom_x = target_center.X
extrude_amount = -3.351 - bottom_x

loft_bottom_plane = Plane(
    origin=target_center,
    x_dir=(0, 1, 0),
    z_dir=(1, 0, 0)
)

with BuildPart() as extension:
    with BuildSketch(loft_bottom_plane):
        Circle(11.3 / 2)
    extrude(amount=extrude_amount)

result = result.fuse(extension.part)

# --- Small cylinder with chamfer ---
bottom_center = (-3.351, 18.604, 17.278)
bottom_plane = Plane(
    origin=bottom_center,
    x_dir=(0, 1, 0),
    z_dir=(1, 0, 0)
)

with BuildPart() as small_cyl:
    with BuildSketch(bottom_plane):
        Circle(4.028 / 2)
    extrude(amount=-4.856)
    
    bottom_edge = small_cyl.edges().sort_by(Axis.X)[0]
    chamfer(bottom_edge, length=1)

result = result.fuse(small_cyl.part)

# --- New revolve: line + arc + closing line ---
profile_plane2 = Plane(
    origin=(0, 18.604, 17.278),
    x_dir=(1, 0, 0),
    z_dir=(0, 0, 1)
)

with BuildSketch(profile_plane2) as profile2:
    with BuildLine():
        Line((-8.206, 0), (-11.179, 0))
        Line((-11.179, 0), (-11.179, 0.944))
        RadiusArc((-11.179, 0.944), (-8.206, 0.944), 11.989)
        Line((-8.206, 0.944), (-8.206, 0))
    make_face()

rev_axis2 = Axis((0, 18.604, 17.278), (1, 0, 0))
revolved2 = revolve(profile2.sketch, axis=rev_axis2)
result = result.fuse(revolved2)

# --- Tapered rectangular (pyramid frustum) cuts on the ring ---
ring_cy = 18.604
ring_cz = 17.278
ring_r_outer = 24.516 / 2
ring_mid_x = 3.573 - 6.923 / 2

num_cuts = 16
cut_depth = 0.616

# Top rectangle (at outer surface): 6.924 x 4.783
top_length = 6.924
top_width = 4.783

# Bottom rectangle (at inner cut surface): 2.406 x 1.438
bot_length = 2.406
bot_width = 1.438

for i in range(num_cuts):
    angle = i * (360.0 / num_cuts)
    angle_rad = math.radians(angle)
    
    dy = math.cos(angle_rad)
    dz = math.sin(angle_rad)
    
    outer_y = ring_cy + ring_r_outer * dy
    outer_z = ring_cz + ring_r_outer * dz
    
    inner_r = ring_r_outer - cut_depth
    inner_y = ring_cy + inner_r * dy
    inner_z = ring_cz + inner_r * dz
    
    cut_normal = Vector(0, dy, dz)
    
    # Top plane (outer surface)
    top_plane = Plane(
        origin=(ring_mid_x, outer_y, outer_z),
        x_dir=(1, 0, 0),
        z_dir=cut_normal
    )
    
    # Bottom plane (inner cut surface)
    bot_plane = Plane(
        origin=(ring_mid_x, inner_y, inner_z),
        x_dir=(1, 0, 0),
        z_dir=cut_normal
    )
    
    # Create top rectangle wire
    hl_t = top_length / 2
    hw_t = top_width / 2
    top_wire = Wire([
        Edge.make_line(
            top_plane.from_local_coords((hl_t, hw_t)),
            top_plane.from_local_coords((-hl_t, hw_t))
        ),
        Edge.make_line(
            top_plane.from_local_coords((-hl_t, hw_t)),
            top_plane.from_local_coords((-hl_t, -hw_t))
        ),
        Edge.make_line(
            top_plane.from_local_coords((-hl_t, -hw_t)),
            top_plane.from_local_coords((hl_t, -hw_t))
        ),
        Edge.make_line(
            top_plane.from_local_coords((hl_t, -hw_t)),
            top_plane.from_local_coords((hl_t, hw_t))
        ),
    ])
    
    # Create bottom rectangle wire
    hl_b = bot_length / 2
    hw_b = bot_width / 2
    bot_wire = Wire([
        Edge.make_line(
            bot_plane.from_local_coords((hl_b, hw_b)),
            bot_plane.from_local_coords((-hl_b, hw_b))
        ),
        Edge.make_line(
            bot_plane.from_local_coords((-hl_b, hw_b)),
            bot_plane.from_local_coords((-hl_b, -hw_b))
        ),
        Edge.make_line(
            bot_plane.from_local_coords((-hl_b, -hw_b)),
            bot_plane.from_local_coords((hl_b, -hw_b))
        ),
        Edge.make_line(
            bot_plane.from_local_coords((hl_b, -hw_b)),
            bot_plane.from_local_coords((hl_b, hw_b))
        ),
    ])
    
    # Loft between the two rectangles
    cut_solid = Solid.make_loft([top_wire, bot_wire], ruled=True)
    result = result.cut(cut_solid)

# ---------- SHOW ----------
show(result, reset_camera=Camera.RESET)
