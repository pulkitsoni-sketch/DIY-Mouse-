from ocp_vscode import show, Camera
from build123d import *
from OCP.BRepFill import BRepFill_Filling
from OCP.BRepOffset import BRepOffset_MakeOffset, BRepOffset_Skin
from OCP.GeomAbs import GeomAbs_C0, GeomAbs_Arc
from OCP.gp import gp_Vec, gp_Trsf, gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_Transform,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeEdge,
)
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
from OCP.GC import GC_MakeCircle
from OCP.TopAbs import TopAbs_SOLID
import math

THICKNESS = 1.0
REFERENCE_DIR = gp_Vec(0, 0, 1)

# ═══════════════════════════════════════════════════════════════════════════════
# MIRROR TRANSFORM
# ═══════════════════════════════════════════════════════════════════════════════
mirror_trsf = gp_Trsf()
mirror_trsf.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)))

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def make_solid_from_splines(pts_list, label="surface"):
    print(f"  Building {label}...")
    valid_pts_list = [pts for pts in pts_list if len(pts) > 1]
    edges = [Edge.make_spline([Vector(*p) for p in pts]) for pts in valid_pts_list]
    
    filler = BRepFill_Filling()
    filler.SetResolParam(3, 15, 2, False) 
    
    for edge in edges:
        filler.Add(edge.wrapped, GeomAbs_C0)
    filler.Build()
    
    if not filler.IsDone():
        try:
            face = Face.make_surface(Wire(edges))
        except:
            raise RuntimeError(f"Surface creation failed for {label}")
    else:
        face = Face(filler.Face())

    centre = face.center()
    normal = face.normal_at(centre)
    if gp_Vec(normal.X, normal.Y, normal.Z).Dot(REFERENCE_DIR) < 0:
        face = Face(face.wrapped.Reversed())
        
    offset = BRepOffset_MakeOffset()
    offset.Initialize(face.wrapped, THICKNESS, 1e-3, BRepOffset_Skin, False, False, GeomAbs_Arc, True)
    offset.MakeOffsetShape()
    
    if not offset.IsDone():
        raise RuntimeError(f"BRepOffset failed for {label}.")
    return Solid(offset.Shape())

def fuse_solids(solids):
    result = solids[0].wrapped
    for s in solids[1:]:
        f = BRepAlgoAPI_Fuse(result, s.wrapped)
        f.Build()
        if not f.IsDone():
            raise RuntimeError("Fuse failed.")
        result = f.Shape()
    return result

def make_closed_wire(pts):
    wire_builder = BRepBuilderAPI_MakeWire()
    for i in range(len(pts)):
        edge = Edge.make_line(pts[i], pts[(i + 1) % len(pts)])
        wire_builder.Add(edge.wrapped)
    wire_builder.Build()
    if not wire_builder.IsDone():
        raise RuntimeError("Wire construction failed.")
    return Wire(wire_builder.Wire())

def capped_loft(wire_list, label="loft"):
    print(f"  Building {label}...")
    gen = BRepOffsetAPI_ThruSections(True)
    for w in wire_list:
        gen.AddWire(w.wrapped)
    gen.Build()
    if not gen.IsDone():
        raise RuntimeError(f"ThruSections failed for {label}.")
    shape = gen.Shape()
    if shape.ShapeType() != TopAbs_SOLID:
        raise RuntimeError(f"{label}: ThruSections produced shape type {shape.ShapeType()}, not solid.")
    print(f"  {label} done.")
    return Solid(shape)

def mirror_solid(solid, trsf, label="mirror"):
    mb = BRepBuilderAPI_Transform(solid.wrapped, trsf, True)
    mb.Build()
    return Solid(mb.Shape())

def extrude_face_solid(face, vec, label="extrude"):
    prism = BRepPrimAPI_MakePrism(face, vec)
    prism.Build()
    if not prism.IsDone():
        raise RuntimeError(f"BRepPrimAPI_MakePrism failed for {label}.")
    return Solid(prism.Shape())

# ═══════════════════════════════════════════════════════════════════════════════
# SURFACE DATA
# ═══════════════════════════════════════════════════════════════════════════════

# Surface 4 Spline 1 (Cleaned)
s4_s1 = [(6.0,-2.5,33.24),(10.104,-11.199,32.887),(12.682,-18.191,32.251),(15.338,-25.503,30.994),(17.361,-32.184,29.072),(18.32,-38.344,26.317),(18.665,-42.295,23.648),(18.51,-47.772,18.461),(18.139,-49.862,15.23),(17.686,-50.911,13.4)]

s1_pts = [[(25.411,35.37,17.066),(24.731,35.641,17.066),(24.042,35.914,17.066),(23.336,36.193,17.066),(22.604,36.479,17.066),(21.839,36.776,17.066),(21.03,37.086,17.066),(20.17,37.412,17.066),(19.251,37.757,17.066),(18.268,38.12,17.066),(17.236,38.495,17.066),(16.175,38.872,17.066),(15.104,39.241,17.066),(14.043,39.593,17.067),(13.012,39.918,17.067),(12.029,40.207,17.068),(11.114,40.45,17.069),(10.283,40.64,17.071),(9.528,40.781,17.073),(8.839,40.882,17.075),(8.206,40.947,17.077),(7.616,40.985,17.079),(7.059,41.001,17.082),(6.524,41.004,17.085),(6.0,41.0,17.087)], [(6.0,41.0,17.087),(6.0,36.568,19.271),(6.0,35.259,19.909),(6.0,33.763,20.628),(6.0,32.095,21.415),(6.0,30.271,22.255),(6.0,28.306,23.135),(6.0,26.217,24.043),(6.0,24.018,24.963),(6.0,21.725,25.886),(6.0,19.35,26.809),(6.0,16.905,27.731),(6.0,14.401,28.654),(6.0,11.85,29.576),(6.0,9.264,30.498),(6.0,6.649,31.42),(6.0,4.034,32.343)], [(6.0,4.034,32.343),(6.647,4.021,32.228),(7.305,4.008,32.111),(7.986,3.995,31.99),(8.701,3.981,31.865),(9.462,3.966,31.732),(10.279,3.95,31.59),(11.165,3.933,31.437),(12.13,3.915,31.272),(13.181,3.895,31.094),(14.301,3.874,30.904),(15.467,3.852,30.708),(16.658,3.83,30.508),(17.852,3.808,30.308),(19.026,3.786,30.111),(20.159,3.765,29.922),(21.228,3.745,29.743),(22.217,3.727,29.578),(23.131,3.71,29.425),(23.98,3.694,29.283),(24.776,3.68,29.15),(25.529,3.666,29.025),(26.25,3.652,28.904),(26.949,3.639,28.787),(27.638,3.626,28.672)], [(27.638,3.626,28.672),(27.566,6.032,27.939),(27.492,8.424,27.207),(27.414,10.785,26.477),(27.33,13.103,25.749),(27.239,15.361,25.025),(27.139,17.545,24.306),(27.026,19.641,23.593),(26.901,21.633,22.886),(26.761,23.508,22.189),(26.611,25.259,21.507),(26.455,26.878,20.851),(26.298,28.359,20.229),(26.145,29.696,19.65),(26.001,30.881,19.123),(25.869,31.91,18.657),(25.755,32.774,18.261),(25.663,33.472,17.94),(25.59,34.02,17.687),(25.534,34.441,17.494),(25.493,34.755,17.349),(25.463,34.983,17.244),(25.441,35.148,17.168),(25.425,35.27,17.112),(25.411,35.37,17.066)]]
s2_pts = [s1_pts[2], [(27.638,3.626,28.672),(27.411,3.462,28.708),(27.183,3.298,28.743),(26.956,3.134,28.779),(26.729,2.97,28.814),(26.501,2.806,28.85),(26.274,2.642,28.885),(26.047,2.477,28.921),(25.819,2.313,28.956)], [(25.819,2.313,28.956),(25.198,2.32,29.077),(24.567,2.326,29.199),(23.917,2.333,29.324),(23.237,2.34,29.456),(22.519,2.347,29.595),(21.753,2.355,29.743),(20.929,2.364,29.903),(20.037,2.373,30.075),(19.072,2.383,30.262),(18.05,2.393,30.46),(16.989,2.404,30.665),(15.908,2.415,30.874),(14.828,2.426,31.083),(13.767,2.437,31.289),(12.745,2.448,31.486),(11.78,2.458,31.673),(10.888,2.467,31.846),(10.064,2.475,32.005),(9.298,2.483,32.153),(8.581,2.49,32.292),(7.902,2.497,32.424),(7.252,2.504,32.549),(6.621,2.511,32.671),(6.0,2.517,32.791)], [(6.0,2.517,32.791),(6.0,2.707,32.735),(6.0,2.896,32.679),(6.0,3.086,32.623),(6.0,3.276,32.567),(6.0,3.465,32.511),(6.0,3.655,32.455),(6.0,3.844,32.399),(6.0,4.034,32.343)]]
s3_pts = [s2_pts[2], [(25.819,2.313,28.956),(25.842,2.149,28.992),(25.864,1.985,29.027),(25.887,1.821,29.063),(25.91,1.657,29.098),(25.932,1.492,29.134),(25.955,1.328,29.169),(25.977,1.164,29.205),(26.0,1.0,29.24)], [(26.0,1.0,29.24),(23.5,0.563,29.74),(21.0,0.125,30.24),(18.5,-0.313,30.74),(16.0,-0.75,31.24),(13.5,-1.187,31.74),(11.0,-1.625,32.24),(8.5,-2.062,32.74),(6.0,-2.5,33.24)], [(6.0,-2.5,33.24),(6.0,-1.873,33.184),(6.0,-1.246,33.128),(6.0,-0.619,33.072),(6.0,0.009,33.016),(6.0,0.636,32.96),(6.0,1.263,32.904),(6.0,1.89,32.848),(6.0,2.517,32.791)]]

s4_pts = [s4_s1, [(17.686,-50.911,13.4),(18.513,-50.177,13.4),(20.087,-48.59,13.4),(21.568,-46.924,13.4),(22.941,-45.219,13.4),(24.194,-43.513,13.4),(25.313,-41.847,13.4),(26.284,-40.26,13.4),(27.101,-38.781,13.4),(27.776,-37.406,13.4),(28.331,-36.12,13.4),(28.786,-34.907,13.4)], [(28.786,-34.907,13.4),(28.63,-33.842,15.07),(28.427,-32.677,16.834),(28.151,-31.423,18.602),(27.778,-30.089,20.281),(26.946,-27.718,22.726),(25.967,-25.208,24.796),(24.856,-22.395,26.597),(23.676,-19.035,28.132),(23.08,-16.674,28.808),(22.66,-14.143,29.282),(22.456,-11.574,29.574),(22.503,-9.097,29.708),(23.007,-6.67,29.695),(23.954,-4.172,29.572),(25.049,-1.612,29.4),(26.0,1.0,29.24)], s3_pts[2]]
s5_pts = [[(17.686,-50.911,13.4),(16.858,-51.645,13.4),(15.137,-52.956,13.4),(13.362,-54.078,13.4),(11.54,-55.014,13.4),(9.677,-55.775,13.4),(7.782,-56.373,13.4),(6.563,-56.656,13.4)], [(6.563,-56.656,13.4),(7.01,-54.858,16.277),(7.696,-50.555,20.465),(8.04,-43.278,26.219),(8.153,-34.783,30.636),(7.858,-28.093,32.395),(6.942,-18.562,33.532),(5.896,-12.261,33.822),(4.5,-7.0,33.74)], [(4.5,-7.0,33.74),(4.688,-6.438,33.678),(4.875,-5.875,33.615),(5.063,-5.313,33.553),(5.25,-4.75,33.49),(5.625,-3.625,33.365),(5.813,-3.063,33.303),(6.0,-2.5,33.24)], s4_s1]

# Surface 9 Splits (Not Mirrored)
s9a_pts = [[(27.03, -11.55, 26.888), (27.645, -9.046, 26.674), (28.083, -6.607, 26.628), (28.43, -4.129, 26.738), (28.723, -1.598, 26.898), (29.0, 1.0, 27.0)], [(29.0, 1.0, 27.0), (28.625, 1.0, 27.28), (28.25, 1.0, 27.56), (27.875, 1.0, 27.84), (27.125, 1.0, 28.4), (26.75, 1.0, 28.68), (26.375, 1.0, 28.96), (26.0, 1.0, 29.24)], [(26.0, 1.0, 29.24), (25.049, -1.612, 29.4), (23.954, -4.172, 29.572), (23.007, -6.67, 29.695), (22.503, -9.097, 29.708), (22.456, -11.574, 29.574), (22.66, -14.143, 29.282)], [(22.66, -14.143, 29.282), (25.762, -12.691, 27.863), (27.03, -11.55, 26.888)]]
s9b_pts = [[(28.0, -13.5, 25.0), (28.128, -12.494, 25.038), (28.51, -9.857, 24.931), (28.822, -7.184, 24.88), (29.079, -4.487, 24.88), (29.299, -1.761, 24.86), (29.5, 1.0, 24.75)], [(29.5, 1.0, 24.75), (29.25, 1.0, 25.875), (29.0, 1.0, 27.0)], [(29.0, 1.0, 27.0), (28.723, -1.598, 26.898), (28.43, -4.129, 26.738), (28.083, -6.607, 26.628), (27.645, -9.046, 26.674), (27.03, -11.55, 26.888)], [(27.03, -11.55, 26.888), (27.442, -12.575, 26.077), (28.0, -13.5, 25.0)]]
s9c_pts = [[(29.776, -10.5, 22.0), (30.06, -7.497, 21.555), (30.132, -4.693, 21.51), (30.193, -1.855, 21.447), (30.25, 1.0, 21.375)], [(30.25, 1.0, 21.375), (30.0, 1.0, 22.5), (29.75, 1.0, 23.625), (29.5, 1.0, 24.75)], [(29.5, 1.0, 24.75), (29.299, -1.761, 24.86), (29.079, -4.487, 24.88), (28.822, -7.184, 24.88), (28.51, -9.857, 24.931), (28.128, -12.494, 25.038), (28.0, -13.5, 25.0)], [(28.0, -13.5, 25.0), (28.576, -12.692, 24.192), (28.746, -12.429, 23.929), (28.889, -12.162, 23.662), (29.408, -11.255, 22.755), (29.776, -10.5, 22.0)]]
s9d_pts = [[(31.445, -10.5, 17.894), (31.349, -7.498, 17.96), (31.242, -4.712, 17.988), (31.124, -1.87, 17.999), (31.0, 1.0, 18.0)], [(31.0, 1.0, 18.0), (30.5, 1.0, 20.25), (30.25, 1.0, 21.375)], [(30.25, 1.0, 21.375), (30.193, -1.855, 21.447), (30.132, -4.693, 21.51), (30.06, -7.497, 21.555), (29.776, -10.5, 22.0)], [(29.776, -10.5, 22.0), (29.908, -10.5, 21.687), (30.014, -10.5, 21.456), (30.458, -10.5, 20.364), (30.951, -10.5, 19.134), (31.445, -10.5, 17.894)]]
s9e_pts = [[(29.371, -16.5, 22.0), (29.068, -15.771, 22.729), (29.02, -15.679, 22.821), (28.934, -15.483, 23.017), (28.607, -14.809, 23.691), (28.5, -14.542, 23.958), (28.186, -13.947, 24.553), (28.0, -13.5, 25.0)], [(28.0, -13.5, 25.0), (27.442, -12.575, 26.077), (27.03, -11.55, 26.888)], [(27.03, -11.55, 26.888), (25.762, -12.691, 27.863), (22.66, -14.143, 29.282)], [(22.66, -14.143, 29.282), (23.08, -16.674, 28.808), (23.676, -19.035, 28.132), (24.856, -22.395, 26.597), (25.425, -23.853, 25.73)], [(25.425, -23.853, 25.73), (26.269, -22.728, 25.119), (27.703, -20.45, 23.904), (28.871, -18.055, 22.646), (29.371, -16.5, 22.0)]]
s9f_pts = [[(30.0, -30.5, 13.4), (30.249, -29.433, 13.974), (30.492, -28.337, 14.538), (30.724, -27.185, 15.085), (30.937, -25.948, 15.604), (31.128, -24.598, 16.088), (31.289, -23.105, 16.527), (31.415, -21.444, 16.911), (31.5, -19.583, 17.233), (31.54, -17.506, 17.486), (31.54, -16.5, 17.57)], [(31.54, -16.5, 17.57), (31.265, -16.5, 18.174), (30.936, -16.5, 18.864), (30.614, -16.5, 19.558), (30.324, -16.5, 20.152), (29.96, -16.5, 20.901), (29.686, -16.5, 21.432), (29.371, -16.5, 22.0)], [(29.371, -16.5, 22.0), (28.871, -18.055, 22.646), (27.703, -20.45, 23.904), (26.269, -22.728, 25.119), (25.425, -23.853, 25.73)], [(25.425, -23.853, 25.73), (25.967, -25.208, 24.796), (26.946, -27.718, 22.726), (27.778, -30.089, 20.281), (28.151, -31.423, 18.602), (28.427, -32.677, 16.834), (28.63, -33.842, 15.07), (28.786, -34.907, 13.4)], [(28.786, -34.907, 13.4), (29.16, -33.754, 13.4), (29.473, -32.645, 13.4), (29.747, -31.565, 13.4), (30.0, -30.5, 13.4)]]

# Hump/Heeel Details
s6a_pts = [[(5.896, -12.261, 33.822), (5.583, -10.92, 33.823), (4.889, -8.313, 33.78), (4.5, -7.0, 33.74)], [(4.5, -7.0, 33.74), (2.813, -7.0, 33.74), (1.125, -7.0, 33.74), (0.0, -7.0, 33.74)], [(0.0, -7.0, 33.74), (0.0, -7.232, 33.79), (0.0, -7.9, 33.925), (0.0, -8.938, 34.109), (0.0, -10.287, 34.293), (0.0, -11.952, 34.436), (0.0, -13.993, 34.494)], [(0.0, -13.993, 34.494), (2.213, -13.534, 34.391), (5.896, -12.261, 33.822)]]
s6b_pts = [[(6.942, -18.562, 33.532), (6.724, -16.901, 33.654), (6.403, -14.84, 33.763), (5.896, -12.261, 33.822)], [(5.896, -12.261, 33.822), (2.213, -13.534, 34.391), (0.0, -13.993, 34.494)], [(0.0, -13.993, 34.494), (0.0, -16.659, 34.424), (0.0, -20.139, 34.167), (0.0, -22.67, 33.885)], [(0.0, -22.67, 33.885), (3.842, -20.749, 33.841), (6.942, -18.562, 33.532)]]
s6c_pts = [[(8.153, -34.783, 30.636), (8.125, -33.048, 31.246), (8.028, -30.664, 31.894), (7.858, -28.093, 32.395), (7.636, -25.374, 32.798), (7.273, -21.529, 33.253), (6.942, -18.562, 33.532)], [(6.942, -18.562, 33.532), (3.842, -20.749, 33.841), (0.0, -22.67, 33.885)], [(0.0, -22.67, 33.885), (0.0, -25.362, 33.51), (0.0, -28.03, 33.052), (0.0, -30.49, 32.521), (0.0, -32.756, 31.9), (0.0, -34.973, 31.151), (0.0, -37.158, 30.251)], [(0.0, -37.158, 30.251), (3.023, -36.607, 30.405), (8.153, -34.783, 30.636)]]
s6d_pts = [[(7.696, -50.555, 20.465), (7.887, -48.101, 22.585), (7.987, -45.537, 24.624), (8.04, -43.278, 26.219), (8.099, -40.288, 28.038), (8.14, -37.692, 29.38), (8.153, -34.783, 30.636)], [(8.153, -34.783, 30.636), (3.023, -36.607, 30.405), (0.0, -37.158, 30.251)], [(0.0, -37.158, 30.251), (0.0, -39.327, 29.179), (0.0, -41.489, 27.923), (0.0, -43.618, 26.521), (0.0, -45.682, 25.025), (0.0, -47.649, 23.484), (0.0, -49.486, 21.95), (0.0, -51.16, 20.472), (0.0, -52.639, 19.102)], [(0.0, -52.639, 19.102), (4.385, -51.877, 19.632), (7.696, -50.555, 20.465)]]
s6e_pts = [[(6.563, -56.656, 13.4), (6.771, -55.906, 14.873), (7.01, -54.858, 16.277), (7.428, -52.598, 18.605), (7.696, -50.555, 20.465)], [(7.696, -50.555, 20.465), (4.385, -51.877, 19.632), (0.0, -52.639, 19.102)], [(0.0, -52.639, 19.102), (0.0, -53.891, 17.889), (0.0, -55.667, 16.038), (0.0, -56.663, 14.811), (0.0, -57.353, 13.4)], [(0.0, -57.353, 13.4), (1.962, -57.297, 13.4), (3.918, -57.123, 13.4), (5.86, -56.819, 13.4), (6.563, -56.656, 13.4)]]

# Left side flares
s7a_pts = [[(-6.0,-2.5,33.24),(-10.104,-11.199,32.887),(-12.682,-18.191,32.251)], [(-12.682,-18.191,32.251),(-15.533,-18.95,31.407),(-18.473,-19.14,30.423),(-23.676,-19.035,28.132)], [(-23.676,-19.035,28.132),(-25.056,-16.668,27.622),(-26.17,-14.132,27.205),(-27.03,-11.55,26.888),(-27.645,-9.046,26.674),(-28.083,-6.607,26.628),(-28.43,-4.129,26.738),(-28.723,-1.598,26.898),(-29.0,1.0,27.0)], [(-29.0,1.0,27.0),(-26.0,1.0,29.24),(-23.5,0.562,29.74),(-18.5,-0.313,30.74),(-13.5,-1.188,31.74),(-6.0,-2.5,33.24)]]
s7b_pts = [[(-23.676,-19.035,28.132),(-25.056,-16.668,27.622),(-29.0,1.0,27.0)], [(-29.0,1.0,27.0),(-29.618,0.0,24.0)], [(-29.618,0.0,24.0),(-27.629,-20.435,24.0)], [(-27.629,-20.435,24.0),(-23.676,-19.035,28.132)]]
s7c_pts = [[(-18.665,-42.295,23.648),(-17.361,-32.184,29.072),(-12.682,-18.191,32.251)], [(-12.682,-18.191,32.251),(-23.676,-19.035,28.132)], [(-23.676,-19.035,28.132),(-18.665,-42.295,23.648)]]
s7d_pts = [[(-23.676,-19.035,28.132),(-21.25,-34.119,26.438),(-18.665,-42.295,23.648)], [(-18.665,-42.295,23.648),(-18.684,-43.268,22.849)], [(-18.684,-43.268,22.849),(-27.629,-20.435,24.0)], [(-27.629,-20.435,24.0),(-23.676,-19.035,28.132)]]
s8_pts = [[(-25.353,-29.873,24.0),(-18.684,-43.268,22.849)], [(-18.684,-43.268,22.849),(-17.686,-50.911,13.4)], [(-17.686,-50.911,13.4),(-29.881,-31.0,13.4)], [(-29.881,-31.0,13.4),(-25.353,-29.873,24.0)]]

# Front panels
s10_pts = [[(4.5,-7.0,33.74),(-4.5,-7.0,33.74)], [(-4.5,-7.0,33.74),(-4.5,-5.423,32.998)], [(-4.5,-5.423,32.998),(4.5,-5.423,32.998)], [(4.5,-5.423,32.998),(4.5,-7.0,33.74)]]
s11_pts = [s10_pts[2], [(4.5,-5.423,32.998),(4.508,-3.771,33.23)], [(4.508,-3.771,33.23),(-4.508,-3.771,33.23)], [(-4.508,-3.771,33.23),(-4.5,-5.423,32.998)]]
s12_pts = [s11_pts[2], [(-4.508,-3.771,33.23),(-2.271,4.603,32.725)], [(-2.271,4.603,32.725),(0.0,10.058,31.745),(2.271,4.603,32.725)], [(2.271,4.603,32.725),(4.508,-3.771,33.23)]]

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD SHELL SOLIDS
# ═══════════════════════════════════════════════════════════════════════════════

print("\n--- Generating Surfaces ---")
solid1 = make_solid_from_splines(s1_pts, label="surface_1")
solid2 = make_solid_from_splines(s2_pts, label="surface_2")
solid3 = make_solid_from_splines(s3_pts, label="surface_3")
solid4 = make_solid_from_splines(s4_pts, label="surface_4")
solid5 = make_solid_from_splines(s5_pts, label="surface_5")

solid6a = make_solid_from_splines(s6a_pts, label="surface_6a")
solid6b = make_solid_from_splines(s6b_pts, label="surface_6b")
solid6c = make_solid_from_splines(s6c_pts, label="surface_6c")
solid6d = make_solid_from_splines(s6d_pts, label="surface_6d")
solid6e = make_solid_from_splines(s6e_pts, label="surface_6e")

solid7a = make_solid_from_splines(s7a_pts, label="surface_7a")
solid7b = make_solid_from_splines(s7b_pts, label="surface_7b")
solid7c = make_solid_from_splines(s7c_pts, label="surface_7c")
solid7d = make_solid_from_splines(s7d_pts, label="surface_7d")
solid8 = make_solid_from_splines(s8_pts, label="surface_8")

solid9a = make_solid_from_splines(s9a_pts, label="surface_9a")
solid9b = make_solid_from_splines(s9b_pts, label="surface_9b")
solid9c = make_solid_from_splines(s9c_pts, label="surface_9c")
solid9d = make_solid_from_splines(s9d_pts, label="surface_9d")
solid9e = make_solid_from_splines(s9e_pts, label="surface_9e")
solid9f = make_solid_from_splines(s9f_pts, label="surface_9f")

solid10 = make_solid_from_splines(s10_pts, label="surface_10")
solid11 = make_solid_from_splines(s11_pts, label="surface_11")
solid12 = make_solid_from_splines(s12_pts, label="surface_12")

# Mirror appropriate surfaces
print("Mirroring selected surfaces...")
solids_to_mirror = [solid1, solid2, solid3, solid5, solid6a, solid6b, solid6c, solid6d, solid6e]
mirrored_solids = [s.mirror(Plane.YZ) for s in solids_to_mirror]

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD MECHANICAL INTERNAL SOLIDS
# ═══════════════════════════════════════════════════════════════════════════════

print("\n--- Generating Mechanical Components ---")
# LOFT 1 — Rectangle to Rectangle + Mirror
rect1_pts = [Vector(21.0,25.0,22.367), Vector(17.0,25.0,22.967), Vector(17.0,21.0,24.573), Vector(21.0,21.0,23.928)]
rect2_pts = [Vector(22.6,26.0,13.4), Vector(16.6,26.0,13.4), Vector(16.6,20.0,13.4), Vector(22.6,20.0,13.4)]
loft1 = capped_loft([make_closed_wire(rect1_pts), make_closed_wire(rect2_pts)], "loft1")
loft1_mirror = mirror_solid(loft1, mirror_trsf, "loft1_mirror")

# LOFT 2 — Three rectangle cross-sections + Mirror
loft2_r1 = [Vector(-14.404,36.416,17.978), Vector(-15.404,36.416,17.81), Vector(-15.367,35.237,17.062), Vector(-14.367,35.237,17.23)]
loft2_r2 = [Vector(-14.496,21.0,24.958), Vector(-14.5,20.003,23.7), Vector(-15.5,20.003,23.532), Vector(-15.496,21.0,24.79)]
loft2_r3 = [Vector(-14.588,3.584,30.055), Vector(-14.633,4.769,28.288), Vector(-15.633,4.769,28.12), Vector(-15.588,3.584,29.887)]
loft2a = capped_loft([make_closed_wire(loft2_r1), make_closed_wire(loft2_r2)], "loft2a")
loft2b = capped_loft([make_closed_wire(loft2_r2), make_closed_wire(loft2_r3)], "loft2b")
loft2a_mirror = mirror_solid(loft2a, mirror_trsf, "loft2a_mirror")
loft2b_mirror = mirror_solid(loft2b, mirror_trsf, "loft2b_mirror")

# LOFT 3 — Multi-section column
profA = [Vector(1.9,8.238,31.478), Vector(1.9,4.238,32.478), Vector(-1.9,4.238,32.478), Vector(-1.9,8.238,31.478)]
profB = [Vector(1.925,4.87,24.676), Vector(1.925,0.87,25.426), Vector(-1.925,0.87,25.426), Vector(-1.925,4.87,24.676)]
profC = [Vector(1.95,4.0,16.888), Vector(1.95,0.0,17.388), Vector(-1.95,0.0,17.388), Vector(-1.95,4.0,16.888)]
profD = [Vector(3.0,4.603,13.4), Vector(3.0,1.731,13.4), Vector(3.0,0.0,15.4), Vector(-3.0,0.0,15.4), Vector(-3.0,1.731,13.4), Vector(-3.0,4.603,13.4)]
loft3_upper = capped_loft([make_closed_wire(profA), make_closed_wire(profB), make_closed_wire(profC)], "loft3_upper")
profC_6 = [
    Vector(1.95, 4.0, 16.888), Vector(1.95, 2.0, 17.138), Vector(1.95, 0.0, 17.388),
    Vector(-1.95, 0.0, 17.388), Vector(-1.95, 2.0, 17.138), Vector(-1.95, 4.0, 16.888),
]
loft3_lower = capped_loft([make_closed_wire(profC_6), make_closed_wire(profD)], "loft3_lower")

# EXTRUDED PROFILE
print("Building extruded profile...")
p1 = Vector(3.0, -47.0, 22.92)
p2 = Vector(3.0, -47.0, 13.4)
p3 = Vector(3.0, -57.0, 13.4)
p4 = Vector(3.0, -51.0, 19.641)
profile_wire = make_closed_wire([p1, p2, p3, p4])
face_builder = BRepBuilderAPI_MakeFace(profile_wire.wrapped)
face_builder.Build()
if not face_builder.IsDone(): raise RuntimeError("BRepBuilderAPI_MakeFace failed for extruded profile.")
extruded_solid = extrude_face_solid(face_builder.Face(), gp_Vec(-1.9, 0, 0), "extruded_profile")
extruded_mirror = mirror_solid(extruded_solid, mirror_trsf, "extruded_profile_mirror")

# EXTRUDED CIRCLE
print("Building extruded circle...")
circle_centre = gp_Pnt(0.0, -39.0, 13.429)
circle_dir = gp_Dir(0, 0, 1)
circle_radius = 4.16 / 2.0 
circle_height = 14.273
cylinder = BRepPrimAPI_MakeCylinder(gp_Ax2(circle_centre, circle_dir), circle_radius, circle_height)
cylinder.Build()
if not cylinder.IsDone(): raise RuntimeError("BRepPrimAPI_MakeCylinder failed.")
extruded_circle = Solid(cylinder.Shape())

# SPLINE PROFILE LOFTED TO CYLINDER TOP
print("Building spline-to-cylinder loft...")
spline_pts = [
    Vector(-1.6, -38.976, 29.199), Vector(-1.478, -38.364, 29.438), Vector(-1.131, -37.845, 29.608), Vector(-0.612, -37.522, 29.722),
    Vector(0.0, -37.4, 29.722), Vector(0.612, -37.522, 29.722), Vector(1.131, -37.845, 29.608), Vector(1.478, -38.364, 29.438),
    Vector(1.6, -38.976, 29.199), Vector(1.478, -39.588, 28.869), Vector(1.131, -40.131, 28.564), Vector(0.612, -40.478, 28.268),
    Vector(-0.612, -40.478, 28.268), Vector(-1.131, -40.131, 28.564), Vector(-1.478, -39.588, 28.869),
]
spline_pts_closed = spline_pts + [spline_pts[0]]
spline_edge = Edge.make_spline(spline_pts_closed)
spline_wire = Wire([spline_edge])
cyl_bottom_z = 13.429 + 14.273
cyl_bottom_ax2 = gp_Ax2(gp_Pnt(0.0, -39.0, cyl_bottom_z), gp_Dir(0, 0, 1))
circle_geom = GC_MakeCircle(cyl_bottom_ax2, circle_radius)
circle_edge_builder = BRepBuilderAPI_MakeEdge(circle_geom.Value())
circle_edge_builder.Build()
circle_wire_builder = BRepBuilderAPI_MakeWire(circle_edge_builder.Edge())
circle_wire_builder.Build()
spline_to_cyl_loft = capped_loft([Wire(circle_wire_builder.Wire()), spline_wire], "spline_to_cylinder_loft")

# TRIANGLE LOFT
print("Building triangle loft...")
tri1_pts = [Vector(-1.5, -39.5, 24.0), Vector(-8.0, -39.5, 28.006), Vector(-0.5, -39.5, 28.673)]
tri2_pts = [Vector(-1.5, -38.5, 24.0), Vector(-8.0, -38.5, 28.506), Vector(-0.5, -38.5, 29.173)]
tri_loft = capped_loft([make_closed_wire(tri1_pts), make_closed_wire(tri2_pts)], "triangle_loft")
tri_loft_mirror = mirror_solid(tri_loft, mirror_trsf, "triangle_loft_mirror")

# EXTRUDED TRIANGLES
print("Building extruded triangle 1...")
tri_ext_pts = [Vector(-0.5, -39.5, 28.673), Vector(-0.5, -43.645, 25.677), Vector(-0.5, -40.5, 24.0)]
tri_ext_face_builder = BRepBuilderAPI_MakeFace(make_closed_wire(tri_ext_pts).wrapped)
tri_ext_face_builder.Build()
extruded_triangle = extrude_face_solid(tri_ext_face_builder.Face(), gp_Vec(1.0, 0, 0), "extruded_triangle")

print("Building extruded triangle 2...")
tri_ext2_pts = [Vector(-0.5, -38.5, 29.173), Vector(-0.5, -37.5, 24.0), Vector(-0.5, -30.333, 31.932)]
tri_ext2_face_builder = BRepBuilderAPI_MakeFace(make_closed_wire(tri_ext2_pts).wrapped)
tri_ext2_face_builder.Build()
extruded_triangle2 = extrude_face_solid(tri_ext2_face_builder.Face(), gp_Vec(1.0, 0, 0), "extruded_triangle2")

# QUAD LOFT
print("Building quad loft...")
quad1_pts = [Vector(-17.0, -14.5, 25.0), Vector(-17.0, -19.5, 30.431), Vector(-17.0, -6.5, 31.0), Vector(-17.0, -12.5, 25.0)]
quad2_pts = [Vector(-14.0, -14.5, 25.0), Vector(-14.0, -20.5, 31.431), Vector(-14.0, -6.5, 31.0), Vector(-14.0, -12.5, 25.0)]
quad_loft = capped_loft([make_closed_wire(quad1_pts), make_closed_wire(quad2_pts)], "quad_loft")
quad_loft_mirror = mirror_solid(quad_loft, mirror_trsf, "quad_loft_mirror")

# EXTRUDED CIRCLE 2
print("Building extruded circle 2...")
circ2_centre = gp_Pnt(-27.0, -13.5, 21.0)
circ2_target = gp_Pnt(-13.0, -12.845, 19.418)
circ2_radius = 3.424 / 2.0 
circ2_vec = gp_Vec(circ2_target.X() - circ2_centre.X(), circ2_target.Y() - circ2_centre.Y(), circ2_target.Z() - circ2_centre.Z())
circ2_ax2 = gp_Ax2(circ2_centre, gp_Dir(circ2_vec))
circ2_geom = GC_MakeCircle(circ2_ax2, circ2_radius)
circ2_edge_builder = BRepBuilderAPI_MakeEdge(circ2_geom.Value())
circ2_edge_builder.Build()
circ2_wire_builder = BRepBuilderAPI_MakeWire(circ2_edge_builder.Edge())
circ2_wire_builder.Build()
circ2_face_builder = BRepBuilderAPI_MakeFace(circ2_wire_builder.Wire())
circ2_face_builder.Build()
extruded_circle2 = extrude_face_solid(circ2_face_builder.Face(), circ2_vec, "extruded_circle2")

# EXTRUDED 8-POINT PROFILE AND FUSE
print("Building extruded 8-point profile and fusing...")
oct_pts = [
    Vector(-27.0, -12.5, 22.0), Vector(-27.0, -12.5, 24.0), Vector(-26.49, -12.5, 26.0), Vector(-25.49, -12.5, 27.823),
    Vector(-13.0, -12.5, 32.0), Vector(0.0, -12.5, 34.218), Vector(0.0, -12.5, 22.0), Vector(-13.0, -12.5, 22.0),
]
oct_face_builder = BRepBuilderAPI_MakeFace(make_closed_wire(oct_pts).wrapped)
oct_face_builder.Build()
extruded_oct = extrude_face_solid(oct_face_builder.Face(), gp_Vec(0, -2.0, 0), "extruded_8pt_profile")

fuse_op = BRepAlgoAPI_Fuse(extruded_oct.wrapped, extruded_circle2.wrapped)
fuse_op.Build()
fused_oct_cyl = Solid(fuse_op.Shape())

# HOLE IN FUSED BODY
print("Building hole in fused body...")
hole_centre = gp_Pnt(-27.0, -13.5, 21.0)
hole_target = gp_Pnt(-18.0, -13.5, 21.0)
hole_radius = 1.779 / 2.0
hole_vec = gp_Vec(hole_target.X() - hole_centre.X(), hole_target.Y() - hole_centre.Y(), hole_target.Z() - hole_centre.Z())
hole_ax2 = gp_Ax2(hole_centre, gp_Dir(hole_vec))
hole_geom = GC_MakeCircle(hole_ax2, hole_radius)
hole_edge_builder = BRepBuilderAPI_MakeEdge(hole_geom.Value())
hole_edge_builder.Build()
hole_wire_builder = BRepBuilderAPI_MakeWire(hole_edge_builder.Edge())
hole_wire_builder.Build()
hole_face_builder = BRepBuilderAPI_MakeFace(hole_wire_builder.Wire())
hole_face_builder.Build()
hole_solid = extrude_face_solid(hole_face_builder.Face(), hole_vec, "hole_tool")

cut_op = BRepAlgoAPI_Cut(fused_oct_cyl.wrapped, hole_solid.wrapped)
cut_op.Build()
fused_oct_cyl = Solid(cut_op.Shape())
fused_oct_cyl_mirror = mirror_solid(fused_oct_cyl, mirror_trsf, "fused_oct_cyl_mirror")

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL VALIDATION & DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

shell_components = [
    solid1, solid2, solid3, solid4, solid5, 
    solid6a, solid6b, solid6c, solid6d, solid6e,
    solid7a, solid7b, solid7c, solid7d, solid8,
    solid9a, solid9b, solid9c, solid9d, solid9e, solid9f,
    solid10, solid11, solid12
] + mirrored_solids

mechanical_components = [
    loft1, loft1_mirror,
    loft2a, loft2b, loft2a_mirror, loft2b_mirror,
    loft3_upper, loft3_lower,
    extruded_solid, extruded_mirror,
    extruded_circle,
    spline_to_cyl_loft,
    tri_loft, tri_loft_mirror,
    extruded_triangle,
    extruded_triangle2,
    quad_loft, quad_loft_mirror,
    fused_oct_cyl, fused_oct_cyl_mirror,
]

all_bodies = shell_components + mechanical_components

print(f"\nSuccessfully built {len(all_bodies)} total bodies. Rendering to viewport...")
show(*all_bodies, reset_camera=Camera.RESET)
print("Done.")

from build123d import export_stl

print("\nGrouping bodies into a Compound...")
combined_mouse = Compound(children=all_bodies)

print("Exporting compound to mouse_top.stl...")
export_stl(combined_mouse, "mouse_top.stl")
print("✓ Successfully exported grouped mouse_top.stl!")
