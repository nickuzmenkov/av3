
import math

# vars
radius = 5
height = .5
delta = .5
pitch = 10

part = GetRootPart()
part.SetName('section')

# Functions

def rect(x1, y1, z1, x2, y2, z2, plane):
	curves = List[ITrimmedCurve]()
	curveSegment = CurveSegment.Create(Point.Create(MM(x1),MM(y1),MM(z1)), Point.Create(MM(x1),MM(y2),MM(z1)))
	curves.Add(curveSegment)
	curveSegment = CurveSegment.Create(Point.Create(MM(x1),MM(y2),MM(z1)), Point.Create(MM(x2),MM(y2),MM(z2)))
	curves.Add(curveSegment)
	curveSegment = CurveSegment.Create(Point.Create(MM(x2),MM(y2),MM(z2)), Point.Create(MM(x1),MM(y1),MM(z2)))
	curves.Add(curveSegment)
	curveSegment = CurveSegment.Create(Point.Create(MM(x1),MM(y1),MM(z2)), Point.Create(MM(x1),MM(y1),MM(z1)))
	curves.Add(curveSegment)
	return PlanarBody.Create(plane, curves).CreatedBody

def rotate(face, axis):
	options = RevolveFaceOptions()
	options.ExtrudeType = ExtrudeType.ForceIndependent
	RevolveFaces.Execute(face, axis, DEG(360), options)

def splitface(face, cutter):
	options = SplitFaceOptions()
	face = Selection.Create(face)
	cutter = Selection.Create(cutter)
	return SplitFace.Execute(face, cutter, options)

def share_topology(tolerance):
	options = ShareTopologyOptions()
	options.Tolerance = MM(tolerance)
	ShareTopology.FindAndFix(options)

# Create Bodies

axis = Line.Create(Point.Create(MM(0), MM(0), MM(0)), -Direction.DirZ)

half1_inner = rect(0, 0, 0, 0, radius - height, pitch/2 - delta/2, Plane.PlaneYZ)
rotate(Selection.Create(half1_inner.Faces[0]), axis)
half1_inner = GetRootPart().Bodies[0]
half1_inner.Name = 'half1_inner'

half1_outer = rect(0, radius - height, 0, 0, radius, pitch/2 - delta/2, Plane.PlaneYZ)
rotate(Selection.Create(half1_outer.Faces[0]), axis)
half1_outer = GetRootPart().Bodies[1]
half1_outer.Name = 'half1_outer'

rib_inner = rect(0, 0, pitch/2 - delta/2,  0, radius - height, pitch/2 + delta/2, Plane.PlaneYZ)
rotate(Selection.Create(rib_inner.Faces[0]), axis)
rib_inner = GetRootPart().Bodies[2]
rib_inner.Name = 'rib_inner'

rib_outer = rect(0, radius - height, pitch/2 - delta/2, 0, radius, pitch/2 + delta/2, Plane.PlaneYZ)
rotate(Selection.Create(rib_outer.Faces[0]), axis)
rib_outer = GetRootPart().Bodies[3]
rib_outer.Name = 'rib_outer'

half2_inner = rect(0, 0, pitch/2 + delta/2, 0, radius - height, pitch, Plane.PlaneYZ)
rotate(Selection.Create(half2_inner.Faces[0]), axis)
half2_inner = GetRootPart().Bodies[4]
half2_inner.Name = 'half2_inner'

half2_outer = rect(0, radius - height, pitch/2 + delta/2, 0, radius, pitch, Plane.PlaneYZ)
rotate(Selection.Create(half2_outer.Faces[0]), axis)
half2_outer = GetRootPart().Bodies[5]
half2_outer.Name = 'half2_outer'

result = ViewHelper.SetViewMode(InteractionMode.Solid)

# Cut

DatumPlaneCreator.Create(Point.Create(MM(0), MM(0), MM(0)), Direction.DirY, False)
cutter = GetRootPart().DatumPlanes[0]
cutter.Name = 'cutter'


for face in half1_outer.Faces:
	splitface(face, cutter)

for face in half2_outer.Faces:
	splitface(face, cutter)

share_topology(0.1)
ViewHelper.ZoomToEntity()