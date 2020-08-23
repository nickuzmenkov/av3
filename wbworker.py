class designParameter:

	param_types = {
		'height':	Parameters.GetParameter(Name = "P34"),
		'pitch':	Parameters.GetParameter(Name = "P40"),
		'layer':	Parameters.GetParameter(Name = "P41"),
		'length':	Parameters.GetParameter(Name = "P42")
	}

	def __init__(self, name, dictionary):
		self.designPoint = Parameters.GetDesignPoint(Name = '0')
		self.parameter = designParameter.param_types.get(name)
		self.dictionary = dictionary

	def set_parameter(self, val_key, multiplyer = 1, units='m'):
		self.designPoint.SetParameterExpression(
			Parameter = self.parameter,
			Expression = '{} [{}]'.format(self.dictionary.get(val_key) * multiplyer, units)
		)

class designSystem:

	path = 'C:\\\\users\\\\frenc\\\\yandexdisk\\\\ans\\\\msh\\\\{}.msh'

	cmd = 'DS = WB.AppletList.Applet("DSApplet").App;\nvar meshBranch = DS.Tree.FirstActiveBranch.MeshControlGroup;\nvar filename = "{}";\nDS.Script.doFileExport(filename);'

	heights = {
		# '00': .1e-4,
		'10': .1e-3,
		'20': .2e-3,
		'30': .3e-3,
		'40': .4e-3,
		'50': .5e-3,
		'60': .6e-3
	}

	pitches = {
		# '000': 1e-3,
		'025': 2.5e-3,
		'050': 5e-3,
		'075': 7.5e-3,
		'100': 10e-3,
		'125': 12.5e-3,
		'150': 15e-3
	}

	layers = {
		'010': 0.0159011e-3,
		'020': 0.0086701e-3,
		'040': 0.0047274e-3,
		'100': 0.0021204e-3,
		'200': 0.0011562e-3,
		'400': 0.0006304e-3
	}

	lengths = {
		'100': 100e-3
	}

	def __init__(self, sys, sys_type):
		self.system = sys
		self.sys_type = sys_type
		self.mesh = sys.GetContainer(ComponentName = 'Mesh')

		self.height = designParameter('height', designSystem.heights)
		self.pitch = designParameter('pitch', designSystem.pitches)
		self.layer = designParameter('layer', designSystem.layers)
		self.length = designParameter('length', designSystem.lengths)

		self.height_key	= '000'
		self.pitch_key	= '000'
		self.layer_key	= '000'
		self.prefix		= ''

	def case(self):
		return '{}-{}-{}-{}{}'.\
			format(self.sys_type,  self.height_key, self.pitch_key, self.layer_key, self.prefix)

	def set_prefix(self, multiplyer):
		self.prefix = '-{}'.format(multiplyer)

	def export_mesh(self, path=''):
		if path == '':
			path = designSystem.path.format(self.case())
		self.mesh.SendCommand(Command = designSystem.cmd.format(path))

	def export_cyclic(self, h_keys = list(heights.keys()), p_keys = list(pitches.keys()), l_keys = list(layers.keys()), multiplyers=[1]):
		self.mesh.Edit()

		for h_key in h_keys:
			self.height_key = h_key
			self.height.set_parameter(h_key)

			for p_key in p_keys:
				self.pitch_key = p_key
				self.pitch.set_parameter(p_key)

				for l_key in l_keys:
					self.layer_key = l_key

					try:
						multiplyers[1]
						for multiplyer in multiplyers:
							self.layer.set_parameter(l_key, multiplyer)
							self.set_prefix(multiplyer)

							self.system.Update()
							self.export_mesh()

					except IndexError:
						self.layer.set_parameter(l_key, multiplyers[0])

						self.system.Update()
						self.export_mesh()	
						
		self.mesh.Exit()

# SYSTEMS
# --------------------------------------------------------
sysStab	= designSystem(GetSystem(Name='SYS 1'), 'STAB')
sysRec	= designSystem(GetSystem(Name='SYS'), 'REC')
sysCut	= designSystem(GetSystem(Name='SYS 3'), 'CUT')
sysFlat	= designSystem(GetSystem(Name='SYS 2'), 'FLAT')