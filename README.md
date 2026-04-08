# DIY-Mouse-
Each Stl part was imported into Fusion 360 and converted into Body
Using the node location geometry for each part was created using 2d profile combined with extrusion, lofting or mirrors
If the Body was too complex, Brep was used by finding the fit spline points for the surface on body using the node locations

How Volumetric difference is calculated: The script reads the raw triangles (mesh) directly from both STL files (original and rebuilt) and calculates the volumes of each mesh using Divergence theorem. It then simply subtracts one from the other.

Divergence Theorem: V = 1/6 | n∑i=1 v1.(v2xv3) | Where, v1,v2,v3: 3 corner vertices of each triangle X is cross product . is dot product n∑i=1, is sum over all n triangles in mesh

How Symmetric difference is calculated: Boolean operation are used via. trimesh and manifold3d, Steps:

Both meshes are centre aligned by subtracting their bounding box midpoints
All 24 axis-aligned rotation (6 faces x 4 rotations about vertical axis (0,90,180,270 degrees) = 24) are generated to find best matching orientation btw the two meshes
Once aligned it performs two boolean subtractions: 3.1) B-A = material only in original 3.2) A-B = material only in rebuilt 4 Add both leftover volumes together = total symmetric difference

--- Validation Report ---
Bottom shell     | Volume Error:  9.1904%  |  Surface Area Error:  7.4192%
Top shell        | Volume Error:  3.6097%  |  Surface Area Error:  9.7882%
Thumb button A   | Volume Error:  0.6278%  |  Surface Area Error:  3.0197%
Thumb button B   | Volume Error:  2.0003%  |  Surface Area Error:  3.6340%
Scroll wheel     | Volume Error:  2.0529%  |  Surface Area Error:  4.4442%
Wheel brace      | Volume Error:  0.0034%  |  Surface Area Error:  0.0011%
-------------------------
Time Taken: 55 hours
