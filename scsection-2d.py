
part = GetRootPart()
part.SetName('SECTION')

# Vars

radius = 5 
pitch = 10
height = .4
delta = .5

# Functions

def clear_all():
	selection = Selection.Create(GetRootPart().Bodies)
	result = Delete.Execute(selection)

def curve(x1, y1, z1, x2, y2, z2):
	new = CurveSegment.Create(Point.Create(MM(x1),MM(y1),MM(z1)), Point.Create(MM(x2),MM(y2),MM(z2)))	
	curves.Add(new)

def rect(x1, y1, z1, x2, y2, z2, plane):
	curves = List[ITrimmedCurve]()
	curveSegment = CurveSegment.Create(Point.Create(MM(x1),MM(y1),MM(z1)), Point.Create(MM(x1),MM(y2),MM(z1)))
	curves.Add(curveSegment)
	curveSegment = CurveSegment.Create(Point.Create(MM(x1),MM(y2),MM(z1)), Point.Create(MM(x2),MM(y2),MM(z1)))
	curves.Add(curveSegment)
	curveSegment = CurveSegment.Create(Point.Create(MM(x2),MM(y2),MM(z2)), Point.Create(MM(x2),MM(y1),MM(z1)))
	curves.Add(curveSegment)
	curveSegment = CurveSegment.Create(Point.Create(MM(x2),MM(y1),MM(z2)), Point.Create(MM(x1),MM(y1),MM(z1)))
	curves.Add(curveSegment)
	PlanarBody.Create(plane, curves)

def share_topology(tolerance):
	options = ShareTopologyOptions()
	options.Tolerance = MM(tolerance)
	ShareTopology.FindAndFix(options)

# Create Planes

clear_all()

plane = Plane.PlaneXY

curves = List[ITrimmedCurve]()
curve(0, 0, 0, 0, radius, 0)
curve(0, radius, 0, pitch/2 - delta/2, radius, 0)
curve(pitch/2 - delta/2, radius, 0, pitch/2 - delta/2, radius - height, 0)
curve(pitch/2 - delta/2, radius - height, 0, pitch/2 + delta/2, radius - height, 0)
curve(pitch/2 + delta/2, radius - height, 0, pitch/2 + delta/2, radius, 0)
curve(pitch/2 + delta/2, radius, 0, pitch, radius, 0)
curve(pitch, radius, 0, pitch, 0, 0) 
curve(pitch, 0, 0, 0, 0, 0)
PlanarBody.Create(plane, curves)

fluid_rect = GetRootPart().Bodies[0]
fluid_rect.Name = 'FLUID'

rect(pitch/2 - delta/2, radius - height, 0, pitch/2 + delta/2, radius, 0, plane)
solid_rect = GetRootPart().Bodies[1]
solid_rect.Name = 'SOLID'

share_topology(0.1)
ViewHelper.ZoomToEntity()

DocumentSave.Execute(
	r'C:\\Users\frenc\\YandexDisk\\ans\\geo\\TEST_{0}_{1}.scdoc'
	.format(int(height*10), int(pitch*10))
	)
