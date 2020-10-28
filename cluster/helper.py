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

	Nu0 = {
		'010': 1,
		'020': 1,
		'040': 1,
		'100': 1,
		'200': 1,
		'400': 1
	}

	f0 = {
		'010': 1,
		'020': 1,
		'040': 1,
		'100': 1,
		'200': 1,
		'400': 1
	}

	def __init__(self, folder, cls_folder = True, local = False, cyclic = True, dim=2, **kwargs):
		self.folder = folder
		self.job = None
		self.dim = dim

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

			with open('cmd.sh', 'r') as file:
				cmd = file.read()

			cmd = cmd.replace('[hours]', str(self.hours))
			cmd = cmd.replace('[partition]', self.part)

			if self.cpus == None:
				if self.job == 'build':
					self.cpus = 1
				else:
					self.cpus = 32

			cmd = cmd.replace('[cpus]', str(self.cpus))
			cmd = cmd.replace('[dim]', str(self.dim))

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

	@staticmethod
	def help(thing):
		guide = {
			'wall_function': ['enhanced-wall-treatment', 'scalable-wall-functions', 'non-equilibrium-wall-fn', 'menter-lechner', 'user-defined-wall-functions'],
			'model': ['inviscid', 'laminar', 'k-kl-w', 'ke-realizible', 're-rng', 'ke-standard', 'kw-bsl', 'kw-geko', 'kw-sst', 'kw-standard', 'reynolds-stress-model', 'spalart-allmaras', 'sas', 'transition-sst', 'detached-eddy-simulation']
		}
		try:
			print(f'Keyword "{thing}" has the following avaliable values:\n', ', '.join(guide[thing]), '\n')
		except KeyError:
			print(f'No help on "{thing}" keyword is avaliable.')

	def build(self, test_name, stab_name, **kwargs):

		prefixes = self._kwarg_parse(kwargs.get('prefixes'), [None])
		suffixes = self._kwarg_parse(kwargs.get('suffixes'), [None])

		self.job = 'build'
		if not self.local:
			self._cluster()

		master = pj.Journal()
		names = []

		def sec_first(name, p_key):
			jou = pj.Journal()
			if self.dim == 3:
				jou._cmd += [f'/mesh/translate 0 0 {Helper.pitches.get(p_key)} ']
			else:
				jou.mesh.translate.set(Helper.pitches.get(p_key), 0)
			jou.mesh.modify_zones.append_mesh.set(f'../../../msh/{name}.msh')
			jou.mesh.modify_zones.merge_zones.set('fluid', 'fluid.1')
			if self.dim == 2:
				jou.mesh.modify_zones.merge_zones.set('axis', 'axis.1')
			jou.mesh.modify_zones.merge_zones.set('interior', 'interior.1')
			jou.mesh.modify_zones.merge_zones.set('interior-fluid', 'interior-fluid.1')
			jou.mesh.modify_zones.zone_name.set('wall', 'wall-out')
			jou.mesh.modify_zones.fuse_face_zones.set('inlet', 'outlet.1', fused_name = 'delete-me')
			jou.mesh.modify_zones.merge_zones.set('interior', 'delete-me')
			jou.mesh.modify_zones.zone_name.set('inlet.1', 'inlet')
			return jou

		def sec_nth(name, p_key):
			jou = pj.Journal()
			if self.dim == 3:
				jou._cmd += [f'/mesh/translate 0 0 {Helper.pitches.get(p_key)} ']
			else:
				jou.mesh.translate.set(Helper.pitches.get(p_key), 0)
			jou.mesh.modify_zones.append_mesh.set(f'../../../msh/{name}.msh')
			jou.mesh.modify_zones.merge_zones.set('fluid', 'fluid.1')
			jou.mesh.modify_zones.merge_zones.set('solid', 'solid.1')
			if self.dim == 2:
				jou.mesh.modify_zones.merge_zones.set('axis', 'axis.1')
			jou.mesh.modify_zones.merge_zones.set('interior', 'interior.1')
			jou.mesh.modify_zones.merge_zones.set('interior-fluid', 'interior-fluid.1')
			jou.mesh.modify_zones.merge_zones.set('interior-solid', 'interior-solid.1')
			jou.mesh.modify_zones.merge_zones.set('sides', 'sides.1')
			jou.mesh.modify_zones.merge_zones.set('wall-fluid', 'wall-fluid.1')
			jou.mesh.modify_zones.merge_zones.set('wall-solid', 'wall-solid.1')
			jou.mesh.modify_zones.fuse_face_zones.set('inlet', 'outlet.1', fused_name = 'delete-me')
			jou.mesh.modify_zones.merge_zones.set('interior', 'delete-me')
			jou.mesh.modify_zones.zone_name.set('inlet.1', 'inlet')
			return jou

		def sec_last(name):
			jou = pj.Journal()
			if self.dim == 3:
				jou._cmd += [f'/mesh/translate 0 0 {.1} ']
			else:
				jou.mesh.translate.set(.1, 0)
			jou.mesh.modify_zones.append_mesh.set(f'../../../msh/{name}.msh')
			jou.mesh.modify_zones.merge_zones.set('fluid', 'fluid.1')
			if self.dim == 2:
				jou.mesh.modify_zones.merge_zones.set('axis', 'axis.1')
			jou.mesh.modify_zones.merge_zones.set('interior', 'interior.1')
			jou.mesh.modify_zones.merge_zones.set('interior-fluid', 'interior-fluid.1')
			jou.mesh.modify_zones.merge_zones.set('wall-out', 'wall')
			jou.mesh.modify_zones.fuse_face_zones.set('inlet', 'outlet.1', fused_name = 'delete-me')
			jou.mesh.modify_zones.merge_zones.set('interior', 'delete-me')
			jou.mesh.modify_zones.zone_name.set('inlet.1', 'inlet')
			return jou

		def underloop(name, h_key, p_key, r_key, suffix):
			jou = pj.Journal()

			jou.file.read_case.set('../../../cas/start.cas')
			jou.file.mesh_replace.set(f'../../../msh/{stab_name}-{h_key}-100-{r_key}.msh')

			jou += sec_first(f'{test_name}-{name}', p_key)
			section_nth = sec_nth(f'{test_name}-{name}', p_key)
			for i in range(int(8e-1/Helper.pitches[p_key])):
				jou +=  section_nth
			jou += sec_last(f'{stab_name}-{h_key}-100-{r_key}')

			jou.mesh.check.set()
			jou.mesh.repair_improve.repair.set()
			jou.surface.line_surface.set('cut-1', .1, 0, .1, .005)
			jou.surface.line_surface.set('cut-2', .9, 0, .9, .005)
			jou.define.boundary_conditions.velocity_inlet.set('inlet', Helper.reynolds.get(r_key), 300)
			jou.define.boundary_conditions.pressure_outlet.set('outlet', 300)
			jou.define.boundary_conditions.wall.set('wall-fluid', 1000)
			jou.define.boundary_conditions.wall.set('wall-solid', 1000, fluid = False)
			jou.define.boundary_conditions.wall.set('wall-out', 1000)

			jou.file.write_case.set(f'../../../cas/{name}.cas')
			jou.save(f'../../../cls/cmd-{name}.jou')	

		master = pj.Journal()
		names = []

		for prefix in prefixes:
			for r_key in self.r_keys:
				for h_key in self.h_keys: 
					for p_key in self.p_keys:
						for suffix in suffixes:

							name = self._name_constructor(h_key, p_key, r_key, prefix = prefix, suffix = suffix)
							names += [name]
							underloop(name, h_key, p_key, r_key, suffix)

		master.file.read_journal.set('\n'.join([f'../../../cls/cmd-{x}.jou' for x in names]))
		master.save(self.folder + '/cmd.jou')

	def solve(self, **kwargs):

		prefixes = self._kwarg_parse(kwargs.get('prefixes'), [None])
		suffixes = self._kwarg_parse(kwargs.get('suffixes'), [None])
		iters = self._kwarg_parse(kwargs.get('iters'), 1e3)
		model = self._kwarg_parse(kwargs.get('model'), 'kw-sst')
		wall_function = self._kwarg_parse(kwargs.get('wall_function'), 'enhanced-wall-treatment')
		criteria = self._kwarg_parse(kwargs.get('criteria'), 1e-6)

		self.job = 'solve'
		if not self.local:
			self._cluster()

		def underloop(name, r_key):
			jou = pj.Journal()

			jou.file.read_case.set(f'../../../cas/{name}.cas')

			jou.define.models.viscous.set(model)
			if model in ['ke-standard', 'ke-rng', 'ke-realizable']:
				if wall_function == 'standard':
					jou.define.models.viscous.near_wall_treatment.set('enhanced-wall-treatment')
					jou.define.models.viscous.near_wall_treatment.set('enhanced-wall-treatment no')
				else:
					jou.define.models.viscous.near_wall_treatment.set(wall_function)

			jou.solve.monitors.residual.convergence_criteria.set(1e-6)
			jou.define.boundary_conditions.velocity_inlet.set('inlet', Helper.reynolds.get(r_key), 300)
			jou.define.boundary_conditions.pressure_outlet.set('outlet', 300)
			jou.define.boundary_conditions.wall.set('wall-fluid', 1000)
			jou.define.boundary_conditions.wall.set('wall-out', 1000)
			jou.define.boundary_conditions.wall.set('wall-solid', 1000, fluid = False)
			
			jou.solve.initialize.compute_defaults.velocity_inlet.set('inlet')
			jou.solve.initialize.initialize_flow.set()
			jou.solve.iterate.set(iters)

			jou.report.surface_integrals.area.set(f'../../../out/out-{name}.txt', 'wall-fluid', 'wall-solid')
			jou.report.fluxes.heat_transfer.set(f'../../../out/out-{name}.txt', 'wall-fluid', 'wall-solid')
			jou.report.surface_integrals.facet_avg.set(f'../../../out/out-{name}.txt', 'temperature', 'axis')
			jou.report.surface_integrals.facet_avg.set(f'../../../out/out-{name}.txt', 'pressure', 'cut-1', 'cut-2')
			
			jou.file.write_case_data.set(f'../../../cas/{name}.cas')
			jou.save(f'../../../cls/cmd-{name}.jou')

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

		master.file.read_journal.set('\n'.join([f'../../../cls/cmd-{x}.jou' for x in names]))
		master.save(self.folder + '/cmd.jou')

	def solve_flat(self, **kwargs):

		prefixes = self._kwarg_parse(kwargs.get('prefixes'), [None])
		suffixes = self._kwarg_parse(kwargs.get('suffixes'), [None])
		iters = self._kwarg_parse(kwargs.get('iters'), 1e3)
		model = self._kwarg_parse(kwargs.get('model'), 'kw-sst')
		wall_function = self._kwarg_parse(kwargs.get('wall_function'), 'enhanced-wall-treatment')
		criteria = self._kwarg_parse(kwargs.get('criteria'), 1e-6)

		self.job = 'solve'
		if not self.local:
			self._cluster()

		def underloop(name, r_key):
			jou = pj.Journal()

			jou.file.read_case.set('../../../cas/start.cas')
			jou.file.mesh_replace.set(f'../../../msh/FLAT-{name}.msh')

			jou.define.models.viscous.set(model)
			if model in ['ke-standard', 'ke-rng', 'ke-realizable']:
				if wall_function == 'standard':
					jou.define.models.viscous.near_wall_treatment.set('enhanced-wall-treatment')
					jou.define.models.viscous.near_wall_treatment.set('enhanced-wall-treatment no')
				else:
					jou.define.models.viscous.near_wall_treatment.set(wall_function)

			jou.solve.monitors.residual.convergence_criteria.set(1e-6)
			jou.surface.line_surface.set('cut-1', .1, 0, .1, .005)
			jou.surface.line_surface.set('cut-2', .9, 0, .9, .005)
			jou.define.boundary_conditions.velocity_inlet.set('inlet', Helper.reynolds.get(r_key), 300)
			jou.define.boundary_conditions.pressure_outlet.set('outlet', 300)
			jou.define.boundary_conditions.wall.set('wall', 1000)
			jou.define.boundary_conditions.wall.set('wall-out', 1000)

			jou.solve.initialize.compute_defaults.velocity_inlet.set('inlet')
			jou.solve.initialize.initialize_flow.set()
			jou.solve.iterate.set(iters)

			jou.report.surface_integrals.area.set(f'../../../out/out-{name}.txt', 'wall')
			jou.report.fluxes.heat_transfer.set(f'../../../out/out-{name}.txt', 'wall')
			jou.report.surface_integrals.facet_avg.set(f'../../../out/out-{name}.txt', 'temperature', 'axis')
			jou.report.surface_integrals.facet_avg.set(f'../../../out/out-{name}.txt', 'pressure', 'cut-1', 'cut-2')
			
			jou.file.write_case_data.set(f'../../../cas/{name}.cas')
			jou.save(f'../../../cls/cmd-{name}.jou')

		master = pj.Journal()
		names = []

		for prefix in prefixes:
			for r_key in self.r_keys:
				for suffix in suffixes:

					name = self._name_constructor('00', '000', r_key, prefix = prefix, suffix = suffix)
					names += [name]
					underloop(name, r_key)

		master.file.read_journal.set('\n'.join([f'../../../cls/cmd-{x}.jou' for x in names]))
		master.save(self.folder + '/cmd.jou')

	def grind(self, **kwargs):

		prefixes = self._kwarg_parse(kwargs.get('prefixes'), [None])
		suffixes = self._kwarg_parse(kwargs.get('suffixes'), [None])
		iters = self._kwarg_parse(kwargs.get('iters'), 1e3)
		model = self._kwarg_parse(kwargs.get('model'), 'kw-sst')
		wall_function = self._kwarg_parse(kwargs.get('wall_function'), 'enhanced-wall-treatment')
		criteria = self._kwarg_parse(kwargs.get('criteria'), 1e-6)
		test_points = self._kwarg_parse(kwargs.get('test_points'), {})

		self.job = 'grind'
		if not self.local:
			self._cluster()

		def underloop(name, r_key):

			jou = pj.Journal()
			jou.file.read_case.set('../../../cas/start.cas')
			jou.file.mesh_replace.set(f'../../../msh/{name}.msh')
			
			jou.define.models.viscous.set(model)
			if model in ['ke-standard', 'ke-rng', 'ke-realizible']:
				if wall_function == 'standard':
					jou.define.models.viscous.near_wall_treatment.set('enhanced-wall-treatment')
					jou.define.models.viscous.near_wall_treatment.set('enhanced-wall-treatment no')
				else:
					jou.define.models.viscous.near_wall_treatment.set(wall_function)
					
			jou.solve.monitors.residual.convergence_criteria.set(1e-6)
			for point, (x, y) in test_points.items():
				jou.surface.point_surface.set(point, x, y)

			jou.define.boundary_conditions.velocity_inlet.set('inlet', Helper.reynolds.get(r_key), 300)
			jou.define.boundary_conditions.pressure_outlet.set('outlet', 300)
			jou.define.boundary_conditions.wall.set('wall-fluid', 1000)
			jou.define.boundary_conditions.wall.set('wall-solid', 1000, False)

			jou.solve.initialize.compute_defaults.velocity_inlet.set('inlet')
			jou.solve.initialize.initialize_flow.set()
			jou.solve.iterate.set(iters)

			jou.report.fluxes.mass_flow.set(f'../../../out/out-{name}.txt', 'inlet', 'outlet')
			jou.report.fluxes.heat_transfer.set(f'../../../out/out-{name}.txt', 'wall-fluid', 'wall-solid', 'inlet', 'outlet')
			jou.report.surface_integrals.facet_avg.set(f'../../../out/out-{name}.txt', 'temperature', ' '.join(list(test_points.keys())))
			jou.report.surface_integrals.facet_avg.set(f'../../../out/out-{name}.txt', 'pressure', 'inlet', 'outlet')
			
			jou.file.write_case_data.set(f'../../../cas/{name}.cas')
			jou.save(f'../../../cls/cmd-{name}.jou')

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

		master.file.read_journal.set('\n'.join([f'../../../cls/cmd-{x}.jou' for x in names]))
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

			Nu = heat*1e-2/area/(1000 - temp)/0.0242/Helper.Nu0.get(r_key)
			f = 2*pres*pi*1e-4/area/1.225/Helper.reynolds.get(r_key)**2/Helper.f0.get(r_key)

			return Nu, f 

		def underloop(name, r_key, file):
			vals = file_eval(f'../../../out/out-{name}.txt', r_key)
			vals = ['%.4f' % x for x in vals]
			file.write(f'{name}:\t' + '\t'.join(vals) + '\n')

		with open('../../../out/out.txt', 'w') as f:
			for prefix in prefixes:
				for h_key in self.h_keys:
					for p_key in self.p_keys:
						for r_key in self.r_keys:
							for suffix in suffixes:

								name = self._name_constructor(h_key, p_key, r_key, prefix = prefix, suffix = suffix)
								underloop(name, r_key, f)

	def evaluate_flat(self, **kwargs):
		
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
			
			area, heat, temp, pres = vals[0], vals[2], vals[3], vals[4] - vals[5]

			return [heat*1e-2/area/(1000 - temp)/0.0242, 2*pres*pi*1e-4/area/1.225/Helper.reynolds.get(r_key)**2]

		def underloop(name, r_key, file):
			vals = file_eval(f'../../../out/out-{name}.txt', r_key)
			vals = ['%.4f' % x for x in vals]
			file.write(f'{name}:\t' + '\t'.join(vals) + '\n')

		with open('../../../out/out.txt', 'w') as f:
			for prefix in prefixes:
				for h_key in self.h_keys:
					for p_key in self.p_keys:
						for r_key in self.r_keys:
							for suffix in suffixes:

								name = self._name_constructor(h_key, p_key, r_key, prefix = prefix, suffix = suffix)
								underloop(name, r_key, f)