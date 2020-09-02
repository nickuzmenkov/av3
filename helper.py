import os
from glob import glob
import pyjou as pj

class Helper():

	heights = {
		'10': .1e-3,
		'20': .2e-3,
		'30': .3e-3,
		'40': .4e-3,
		'50': .5e-3,
		'60': .6e-3
	}

	pitches = {
		'025': 2.5e-3,
		'050': 5e-3,
		'075': 7.5e-3,
		'100': 10e-3,
		'125': 12.5e-3,
		'150': 15e-3
	}

	reynolds = {
		'010': 14.60735,
		'020': 29.21469,
		'040': 58.42939,
		'100': 146.07347,
		'200': 292.14694,
		'400': 584.29388
	}

	def __init__(self, folder, cls_folder = True, local = False, cyclic = True, **kwargs):
		self.folder = folder
		self.job = None

		if cls_folder:
			self.cls_folder()

		self.local = local
		if not local:
			self.hours = kwargs.get('hours') if kwargs.get('hours') != None else 12
			self.part = kwargs.get('partition') if kwargs.get('partition') != None else 'cascadelake'
			self.cpus = kwargs.get('cpus')
			self.cls_script = kwargs.get('cls_script') if kwargs.get('cls_script') != None else True

		if not cyclic:
			try:
				self.h_keys = kwargs['h_keys']
				self.p_keys = kwargs['p_keys']
				self.r_keys = kwargs['r_keys']
				if self.h_keys == 'all':
					self.h_keys = list(Helper.heights.keys())
				if self.p_keys == 'all':
					self.p_keys = list(Helper.pitches.keys())
				if self.r_keys == 'all':
					self.r_keys = list(Helper.reynolds.keys())
			except KeyError:
				print('If cyclic option is disabled, the following keyword arguments must be defined: h_keys, p_keys, r_keys')
				raise
		else:
			self.h_keys = list(Helper.heights.keys())
			self.p_keys = list(Helper.pitches.keys())
			self.r_keys = list(Helper.reynolds.keys())

	def cls_folder(self):
		for file in glob(self.folder + '/*'):
			try:
				os.remove(file)
			except:
				print(f'failed deleting {file}\n')
				continue

	def _cluster(self):

			import shutil
			import io

			shutil.copy('passport.json', self.folder + '/passport.json')
			shutil.copy('dispatcher.json', self.folder + '/dispatcher.json')

			with open('cmd.txt', 'r') as file:
				cmd = file.read()

			cmd = cmd.replace('[hours]', str(self.hours))
			cmd = cmd.replace('[partition]', self.part)

			if self.cpus == None:
				if self.job == 'build':
					self.cpus = 1
				else:
					self.cpus = 32

			cmd = cmd.replace('[cpus]', str(self.cpus))

			if self.cls_script:
				shutil.copy('pycleaner.py', self.folder + '/pycleaner.py')
				cmd = cmd.replace('[postscript]', 'python pycleaner.py')
			else:
				cmd = cmd.replace('[postscript]', '')

			with io.open(self.folder + '/cmd.sh', 'w', newline='\n') as file:
				file.write(cmd)

	@staticmethod
	def _kwarg_parse(kwarg, default):
		return kwarg if kwarg != None else default
		
	@staticmethod
	def _name_constructor(*args, prefix = None, suffix = None):
		name = [str(x) for x in [prefix] + list(args) + [suffix] if x != None]
		return '-'.join(name)

	def build(self, test_name, stab_name, **kwargs):

		prefixes = self._kwarg_parse(kwargs.get('prefixes'), [None])
		suffixes = self._kwarg_parse(kwargs.get('suffixes'), [None])

		self.job = 'build'
		if not self.local:
			self._cluster()

		master = pj.Journal()
		names = []

		def sec_first(name):
			first = pj.Journal()
			first.mesh.translate.set(x = Helper.pitches.get(
				p_key), y = 0)
			first.mesh.modify_zones.append_mesh.set(
				path = f'../msh/{name}.msh')
			first.mesh.modify_zones.merge_zones.set(
				list_zones = ['fluid', 'fluid.1'])
			first.mesh.modify_zones.merge_zones.set(
				list_zones = ['axis', 'axis.1'])
			first.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior', 'interior.1'])
			first.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior-fluid', 'interior-fluid.1'])
			first.mesh.modify_zones.zone_name.set(
				old_name = 'wall', new_name = 'wall-out')
			first.mesh.modify_zones.fuse_face_zones.set(
				list_zones = ['inlet', 'outlet.1'], 
				fused_name = 'delete-me')
			first.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior', 'delete-me'])
			first.mesh.modify_zones.zone_name.set(
				old_name = 'inlet.1', new_name = 'inlet')
			return first

		def sec_nth(name):
			nth = pj.Journal()
			nth.mesh.translate.set(
				x = Helper.pitches.get(p_key), y = 0)
			nth.mesh.modify_zones.append_mesh.set(
				path = f'../msh/{name}.msh')
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['fluid', 'fluid.1'])
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['solid', 'solid.1'])
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['axis', 'axis.1'])
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior', 'interior.1'])
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior-fluid', 'interior-fluid.1'])
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior-solid', 'interior-solid.1'])
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['sides', 'sides.1'])
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['wall-fluid', 'wall-fluid.1'])
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['wall-solid', 'wall-solid.1'])
			nth.mesh.modify_zones.fuse_face_zones.set(
				list_zones = ['inlet', 'outlet.1'], 
				fused_name = 'delete-me')
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior', 'delete-me'])
			nth.mesh.modify_zones.zone_name.set(
				old_name = 'inlet.1', new_name = 'inlet')
			return nth

		def sec_last(name):
			last = pj.Journal()
			last.mesh.translate.set(
				x = .1, y = 0)
			last.mesh.modify_zones.append_mesh.set(
				path = f'../msh/{name}.msh')
			last.mesh.modify_zones.merge_zones.set(
				list_zones = ['fluid', 'fluid.1'])
			last.mesh.modify_zones.merge_zones.set(
				list_zones = ['axis', 'axis.1'])
			last.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior', 'interior.1'])
			last.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior-fluid', 'interior-fluid.1'])
			last.mesh.modify_zones.merge_zones.set(
				list_zones = ['wall-out', 'wall'])
			last.mesh.modify_zones.fuse_face_zones.set(
				list_zones = ['inlet', 'outlet.1'], 
				fused_name = 'delete-me')
			last.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior', 'delete-me'])
			last.mesh.modify_zones.zone_name.set(
				old_name = 'inlet.1', new_name = 'inlet')
			return last

		def underloop(name, h_key, r_key):
			jou = pj.Journal()

			jou.file.read_case.set(path = '../cas/start.cas')
			jou.file.mesh_replace.set(
				path = f'../msh/{stab_name}-{h_key}-100-{r_key}.msh')

			jou += sec_first(f'{test_name}-{name}')
			jou += sec_nth(f'{test_name}-{name}') * int(8e-1/Helper.pitches[p_key])
			jou += sec_last(f'{stab_name}-{name}')

			jou.mesh.check.set()
			jou.mesh.repair_improve.repair.set()
			jou.define.boundary_conditions.velocity_inlet.set(
				name = 'inlet', velocity = Helper.reynolds.get(r_key), 
				temperature = 300)
			jou.define.boundary_conditions.pressure_outlet.set(
				name = 'outlet', temperature = 300)
			jou.define.boundary_conditions.wall.set(
				name = 'wall-fluid', temperature = 1000)
			jou.define.boundary_conditions.wall.set(
				name = 'wall-solid', temperature = 1000, fluid = False)
			jou.define.boundary_conditions.wall.set(
				name = 'wall-out', temperature = 1000)

			jou.file.write_case.set(path = f'../cas/{name}.cas')
			jou.save(f'../cls/cmd-{name}.jou')	

		master = pj.Journal()
		names = []

		for prefix in prefixes:
			for r_key in self.r_keys:
				for h_key in self.h_keys: 
					for p_key in self.p_keys:
						for suffix in suffixes:

							name = self._name_constructor(h_key, p_key, r_key, prefix = prefix, suffix = suffix)
							names += [name]
							underloop(name, h_key, r_key)

		master.file.read_journal.set(path = [f'../cls/cmd-{x}.jou' for x in names])
		master.save(self.folder + '/cmd.jou')

	def solve(self, **kwargs):

		prefixes = self._kwarg_parse(kwargs.get('prefixes'), [None])
		suffixes = self._kwarg_parse(kwargs.get('suffixes'), [None])
		iters = self._kwarg_parse(kwargs.get('iters'), 1e3)
		model = self._kwarg_parse(kwargs.get('model'), 'kw-sst')
		criteria = self._kwarg_parse(kwargs.get('criteria'), 1e-6)

		self.job = 'solve'
		if not self.local:
			self._cluster()

		def underloop(name, r_key):
			jou = pj.Journal()

			jou.file.read_case.set(
				path = f'../cas/{name}.cas')

			jou.define.models.viscous.set(model = model)
			jou.solve.monitors.residual.convergence_criteria.set(
				criteria = [criteria for x in range(6)])
			jou.surface.line_surface.set(
				name = 'cut-1', x1 = .1, y1 = 0, x2 = .1, y2 = .005)
			jou.surface.line_surface.set(
				name = 'cut-2', x1 = .9, y1 = 0, x2 = .9, y2 = .005)

			jou.define.boundary_conditions.velocity_inlet.set(
				name = 'inlet', velocity = Helper.reynolds.get(r_key),
				temperature = 300)
			jou.define.boundary_conditions.pressure_outlet.set(
				name = 'outlet', temperature = 300)
			jou.define.boundary_conditions.wall.set(
				name = 'wall-fluid', temperature = 1000)
			jou.define.boundary_conditions.wall.set(
				name = 'wall-solid', temperature = 1000, fluid = False)
			jou.define.boundary_conditions.wall.set(
				name = 'wall-out', temperature = 1000)

			jou.solve.initialize.compute_defaults.velocity_inlet.set(
				name = 'inlet')
			jou.solve.initialize.initialize_flow.set()
			jou.solve.iterate.set(iters = iters)

			jou.report.surface_integrals.area.set(
				path = f'../out/out-{name}.txt', 
				list_zones = ['wall-fluid', 'wall-solid'])
			jou.report.fluxes.heat_transfer.set(
				path = f'../out/out-{name}.txt', 
				all_zones = False, list_zones=['wall-fluid', 'wall-solid'])
			jou.report.surface_integrals.facet_avg.set(
				path = f'../out/out-{name}.txt', 
				value = 'temperature', list_zones = 'axis')
			jou.report.surface_integrals.facet_avg.set(
				path = f'../out/out-{name}.txt', 
				value = 'pressure', list_zones = ['cut-1', 'cut-2'])
			
			jou.file.write_case_data.set(path = f'../cas/{name}.cas')
			jou.save(f'../cls/cmd-{name}.jou')

		master = pj.Journal()
		names = []

		for prefix in prefixes:
			for r_key in self.r_keys:
				for h_key in self.h_keys: 
					for p_key in self.p_keys:
						for suffix in suffixes:

							name = self._name_constructor(h_key, p_key, r_key, prefix = prefix, suffix = suffix)
							names += [name]
							underloop(name, r_key)

		master.file.read_journal.set(path = [f'../cls/cmd-{x}.jou' for x in names])
		master.save(self.folder + '/cmd.jou')

	def grind(self, **kwargs):

		prefixes = self._kwarg_parse(kwargs.get('prefixes'), [None])
		suffixes = self._kwarg_parse(kwargs.get('suffixes'), [None])
		iters = self._kwarg_parse(kwargs.get('iters'), 1e3)
		model = self._kwarg_parse(kwargs.get('model'), 'kw-sst')
		criteria = self._kwarg_parse(kwargs.get('criteria'), 1e-6)
		test_points = self._kwarg_parse(kwargs.get('test_points'), {})

		self.job = 'grind'
		if not self.local:
			self._cluster()

		def underloop(name, r_key):

			jou = pj.Journal()
			jou.file.read_case.set(path = '../cas/start.cas')
			jou.file.mesh_replace.set(path = f'../msh/{name}.msh')
			
			jou.define.models.viscous.set(model = model)
			jou.solve.monitors.residual.convergence_criteria.set(
				criteria = [criteria for x in range(6)])

			for point, (x, y) in test_points.items():
				jou.surface.point_surface.set(
					name = point, x = x, y = y)

			jou.define.boundary_conditions.velocity_inlet.set( 
				name = 'inlet', velocity = Helper.reynolds.get(r_key), 
				temperature = 300)
			jou.define.boundary_conditions.pressure_outlet.set(
				name = 'outlet', temperature = 300)
			jou.define.boundary_conditions.wall.set(
				name = 'wall-fluid', temperature = 1000)
			jou.define.boundary_conditions.wall.set(
				name = 'wall-solid', temperature = 1000, fluid = False)

			jou.solve.initialize.compute_defaults.velocity_inlet.set(
				name = 'inlet')
			jou.solve.initialize.initialize_flow.set()
			jou.solve.iterate.set(iters = iters)

			jou.report.fluxes.mass_flow.set(
				path = f'../out/out-{name}.txt',
				all_zones = False, list_zones = ['inlet', 'outlet'])
			jou.report.fluxes.heat_transfer.set(
				path = f'../out/out-{name}.txt',
				all_zones = False, 
				list_zones = ['wall-fluid', 'wall-solid', 'inlet', 'outlet'])
			jou.report.surface_integrals.facet_avg.set(
				path = f'../out/out-{name}.txt', value = 'temperature', 
				list_zones = list(test_points.keys()))
			jou.report.surface_integrals.facet_avg.set(
				path = f'../out/out-{name}.txt', value = 'pressure', 
				list_zones = ['inlet', 'outlet'])
			
			jou.file.write_case_data.set(path = f'../cas/{name}.cas')
			jou.save(f'../cls/cmd-{name}.jou')

		master = pj.Journal()
		names = []

		for prefix in prefixes:
			for r_key in self.r_keys:
				for h_key in self.h_keys: 
					for p_key in self.p_keys:
						for suffix in suffixes:

							name = self._name_constructor(h_key, p_key, r_key, prefix = prefix, suffix = suffix)
							names += [name]
							underloop(name, r_key)

		master.file.read_journal.set(path = [f'../cls/cmd-{x}.jou' for x in names])
		master.save(self.folder + '/cmd.jou')

	def evaluate(self, **kwargs):

		prefixes = self._kwarg_parse(kwargs.get('prefixes'), [None])
		suffixes = self._kwarg_parse(kwargs.get('suffixes'), [None])

		def file_eval(path, r_key):

			from math import pi

			vals = []
			with open(path, 'r') as f:
				for line in f.readlines():
					for char in line.split():
						try:
							vals += [float(char)]
						except:
							continue
			
			area, heat, temp, pres = vals[2], vals[5], vals[6], vals[7] - vals[8]

			return [heat*1e-2/area/(1000 - temp)/0.0242, 2*pres*pi*1e-4/area/1.225/Helper.reynolds.get(r_key)**2]


		def underloop(name, r_key, file):
			vals = file_eval(f'../out/out-{name}.txt', r_key)
			vals = ['%.4f' % x for x in vals]
			file.write(f'{name}:\t' + '\t'.join(vals) + '\n')

		with open('../out/out.txt', 'w') as f:
			for prefix in prefixes:
				for h_key in self.h_keys:
					for p_key in self.p_keys:
						for r_key in self.r_keys:
							for suffix in suffixes:

								name = self._name_constructor(h_key, p_key, r_key, prefix = prefix, suffix = suffix)
								underloop(name, r_key, f)
