#For showing the sketch in OCP CAD Viewer
from ocp_vscode import show
from build123d import *

# Building 1st cylinder 
center = (13.111, 18.604, 17.278)
radius1 = 7.417 / 2
radius2 = 5.114 / 2 

yz_plane = Plane(
    origin=center,
    x_dir=(0, 1, 0),   # along global Y
    z_dir=(1, 0, 0)    # normal along X
)

with BuildPart() as part:
    with BuildSketch(yz_plane):
        Circle(radius1, mode=Mode.ADD)
        Circle(radius2, mode=Mode.SUBTRACT)
    
    extrude(amount=-9.538)   # 👈 negative = -X direction
    bottom_face = part.faces().sort_by(Axis.X)[0] # sort_by(Axis.X)[0] = most closest to -ve X directon face 
    extrude(bottom_face,amount=1.464, taper=-3.595)  # 👈 positive = -X direction
show (part)

with BuildPart() as part2:
    with BuildSketch(yz_plane.offset(-11.002)) as sketch2:
        Circle(11.3/2)
    with BuildSketch(yz_plane.offset(-15.002)) as sketch3:
        Circle(7.601/2)
    loft([sketch2, sketch3])
show(part2)