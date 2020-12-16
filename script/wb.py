import time

''' -------------------------------------------------------
define helpful classes
------------------------------------------------------- '''
''' parameter class '''
class Parameter():

	def __init__(self, number):
		self.designPoint = Parameters.GetDesignPoint(Name = '0')
		self.key = Parameters.GetParameter(Name='P{}'.format(number))

	def set(self, value, multiplyer = 1, units='m'):
		self.designPoint.SetParameterExpression(
			Parameter = self.key,
			Expression = '{} [{}]'.format(value * multiplyer, units)
		)

''' geometry class '''
class Geometry():

	def __init__(self, parent):
		self.geometry = parent.system.GetContainer(ComponentName='Geometry')

	def set(self, path):
		self.geometry.SetFile(FilePath=path)

''' mesh class '''
class Mesh():

	def __init__(self, parent):
		self.mesh = parent.system.GetContainer(ComponentName='Mesh')

	def edit(self):
		self.mesh.Edit()

	def exit(self):
		self.mesh.Exit()

	def export(self, path):
		cmd = 'DS = WB.AppletList.Applet("DSApplet").App;\nvar meshBranch = DS.Tree.FirstActiveBranch.MeshControlGroup;\nvar filename = "{}";\nDS.Script.doFileExport(filename);'
		path = path.replace('\\', '\\\\')
		self.mesh.SendCommand(Command=cmd.format(path))

''' system class '''
class System():

	def __init__(self, name, parameters):
		self.system = GetSystem(Name=name)
		self.geometry = Geometry(self)
		self.mesh = Mesh(self)

		for key, value in parameters.items():
			setattr(self, key, Parameter(value))

''' -------------------------------------------------------
START FROM HERE
------------------------------------------------------- '''
''' define loop parameters '''
heights = {'10': .1e-3,
		   '20': .2e-3,
		   '30': .3e-3,
		   '40': .4e-3,
		   '50': .5e-3, 
		   '60': .6e-3,
		   '70': .7e-3}

pitches = {'025': 2.5e-3,
		   '050': 5.0e-3,
		   '100': 10e-3,
		   '150': 15e-3}

# layers = {'10': 1.59E-05,
# 		  '20': 8.67E-06,
# 		  '30': 6.08E-06,
# 		  '40': 4.73E-06,
# 		  '50': 3.89E-06,
# 		  '60': 3.32E-06}
layer = 3.32e-6

''' define system parameters '''
# parameters={'radius': 7,
# 			'height': 9,
# 			'pitch': 8,
# 			'delta': 10,
# 			'layer': 11}
parameters={'radius': 10,
			'height': 11,
			'pitch':  12,
			'delta':  13,
			'layer':  18}

''' define root directory '''
path = 'c:\\users\\frenc\\yandexdisk\\cfd\\'
mode = 'V'
# path = '..\\'

''' define system '''
pipe = System('SYS 1', parameters)

''' -------------------------------------------------------
main loop
------------------------------------------------------- '''
pipe.mesh.edit()

for p_key, p_val in pitches.items():
	pipe.pitch.set(p_val)

	for h_key, h_val in heights.items():
		pipe.height.set(h_val)

		pipe.geometry.set(path + 'geo\\2{}-{}-{}.scdoc'.\
			format(mode, h_key, p_key))

		pipe.layer.set(layer)
		pipe.system.Update()
		pipe.mesh.export(path + 'msh\\2{}-{}-{}.msh'.\
			format(mode, h_key, p_key))

time.sleep(5)
pipe.mesh.exit()