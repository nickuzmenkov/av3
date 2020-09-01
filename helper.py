import os
import math
from glob import glob
import pyjou as pj
from functools import wraps

class Helper():

	'''
	helper dictionaries
	'''
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

	'''
	build method
	'''
	def build(self, test_name, stab_name, **kwargs):

		work_name = self._kwarg_parse(kwargs.get('work_name'), '')

		self.job = 'build'
		if not self.local:
			self._cluster()

		master = pj.root()
		slave_names = []

		'''
		helper functions
		'''
		def sec_first(h_key, p_key, r_key):
			first = pj.root()
			first.mesh.translate.set(x = Helper.pitches.get(
				p_key), y = 0)
			first.mesh.modify_zones.append_mesh.set(
				path = '../msh/{}-{}-{}-{}.msh'.format(test_name, h_key, p_key, r_key))
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
				list_zones = ['inlet', 'outlet.1'], fused_name = 'delete-me')
			first.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior', 'delete-me'])
			first.mesh.modify_zones.zone_name.set(
				old_name = 'inlet.1', new_name = 'inlet')
			return first

		def sec_nth(h_key, p_key, r_key):
			nth = pj.root()
			nth.mesh.translate.set(
				x = Helper.pitches.get(p_key), y = 0)
			nth.mesh.modify_zones.append_mesh.set(
				path = '../msh/{}-{}-{}-{}.msh'.format(test_name, h_key, p_key, r_key))
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
				list_zones = ['inlet', 'outlet.1'], fused_name = 'delete-me')
			nth.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior', 'delete-me'])
			nth.mesh.modify_zones.zone_name.set(
				old_name = 'inlet.1', new_name = 'inlet')
			return nth

		def sec_last(h_key, p_key, r_key):
			last = pj.root()
			last.mesh.translate.set(
				x = .1, y = 0)
			last.mesh.modify_zones.append_mesh.set(
				path = '../msh/{}-{}-{}-{}.msh'.format(stab_name, h_key, p_key, r_key))
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
				list_zones = ['inlet', 'outlet.1'], fused_name = 'delete-me')
			last.mesh.modify_zones.merge_zones.set(
				list_zones = ['interior', 'delete-me'])
			last.mesh.modify_zones.zone_name.set(
				old_name = 'inlet.1', new_name = 'inlet')
			return last

		'''
		main loop start
		'''
		for r_key in self.r_keys:
			for h_key in self.h_keys: 
				for p_key in self.p_keys:

					'''
					setup
					'''
					slave = pj.root()
					slave_name = '{}-{}-{}'.format(h_key, p_key, r_key)

					slave.file.read_case.set(
						path = '../cas/start.cas')
					slave.file.mesh_replace.set(
						path = '../msh/{}-{}-{}-{}.msh'.\
						format(stab_name, h_key, '100', r_key))

					'''
					stack build commands
					'''
					slave += sec_first(h_key, p_key, r_key)
					numsec = int(8e-1/Helper.pitches[p_key])
					nth = sec_nth(h_key, p_key, r_key)
					for i in range(0, numsec - 1):
						slave += nth
					slave += sec_last(h_key, p_key, r_key)

					'''
					setting bc
					'''
					slave.mesh.check.set()
					slave.mesh.repair_improve.repair.set()
					slave.define.boundary_conditions.velocity_inlet.set(
						name = 'inlet', velocity = Helper.reynolds.get(r_key), temperature = 300)
					slave.define.boundary_conditions.pressure_outlet.set(
						name = 'outlet', temperature = 300)
					slave.define.boundary_conditions.wall.set(
						name = 'wall-fluid', temperature = 1000)
					slave.define.boundary_conditions.wall.set(
						name = 'wall-solid', temperature = 1000, fluid = False)
					slave.define.boundary_conditions.wall.set(
						name = 'wall-out', temperature = 1000)
					slave.file.write_case.set(
						path = '../cas/{}{}'.format(work_name, slave_name))

					'''
					ending
					'''
					slave_name = 'cmd-{}.jou'.format(slave_name)
					slave_names += [slave_name]
					slave.save('../cls/{}'.format(slave_name))		

		'''
		saving all in a master file
		'''
		master.file.read_journal.set(path = slave_names)
		master.save(self.folder + '/cmd.jou')

	'''
	solve method
	'''
	def solve(self, **kwargs):

		'''
		parsing kwargs
		'''
		iters = self._kwarg_parse(kwargs.get('iters'), 1e3)
		model = self._kwarg_parse(kwargs.get('model'), 'kw-sst')
		work_name = self._kwarg_parse(kwargs.get('work_name'), '')

		self.job = 'solve'
		if not self.local:
			self._cluster()

		master = pj.root()
		slave_names = []

		'''
		main loop start
		'''
		for r_key in self.r_keys:
			for h_key in self.h_keys: 
				for p_key in self.p_keys:

					'''
					setup
					'''
					slave = pj.root()
					slave_name = '{}-{}-{}'.format(h_key, p_key, r_key)

					slave.file.read_case.set(
						path = '../cas/{}{}.cas'.format(work_name, slave_name))

					'''
					defining models
					'''
					slave.define.models.viscous.set(
						model = model)
					slave.solve.monitors.residual.convergence_criteria.set(
						criteria = [1e-6, 1e-6, 1e-6, 1e-6, 1e-6, 1e-6])
					slave.surface.line_surface.set(
						name = 'cut-1', x1 = .1, y1 = 0, x2 = .1, y2 = .005)
					slave.surface.line_surface.set(
						name = 'cut-2', x1 = .9, y1 = 0, x2 = .9, y2 = .005)

					'''
					defining bc
					'''
					slave.define.boundary_conditions.velocity_inlet.set(
						name = 'inlet', velocity = Helper.reynolds.get(r_key),
						temperature = 300)
					slave.define.boundary_conditions.pressure_outlet.set(
						name = 'outlet', temperature = 300)
					slave.define.boundary_conditions.wall.set(
						name = 'wall-fluid', temperature = 1000)
					slave.define.boundary_conditions.wall.set(
						name = 'wall-solid', temperature = 1000, fluid = False)
					slave.define.boundary_conditions.wall.set(
						name = 'wall-out', temperature = 1000)

					'''
					solving
					'''
					slave.solve.initialize.compute_defaults.velocity_inlet.set(
						name = 'inlet')
					slave.solve.initialize.initialize_flow.set()
					slave.solve.iterate.set(
						iters = iters)

					'''
					reporting
					'''
					slave.report.surface_integrals.area.set(
						path = '../out/out-{}{}.txt'.format(work_name, slave_name), 
						list_zones = ['wall-fluid', 'wall-solid'])
					slave.report.fluxes.heat_transfer.set(
						path = '../out/out-{}{}.txt'.format(work_name, slave_name), 
						all_zones = False, list_zones=['wall-fluid', 'wall-solid'])
					slave.report.surface_integrals.facet_avg.set(
						path = '../out/out-{}{}.txt'.format(work_name, slave_name), 
						value = 'temperature', list_zones = 'axis')
					slave.report.surface_integrals.facet_avg.set(
						path = '../out/out-{}{}.txt'.format(work_name, slave_name), 
						value = 'pressure', list_zones = ['cut-1', 'cut-2'])
					
					slave.file.write_case_data.set(
						path = '../cas/{}{}.cas'.format(work_name, slave_name))

					'''
					ending
					'''
					slave_name = 'cmd-{}{}.jou'.format(work_name, slave_name)
					slave_names += [slave_name]
					slave.save('../cls/{}'.format(slave_name))

		'''
		saving all in a master file
		'''
		master.file.read_journal.set(path = slave_names)
		master.save(self.folder + '/cmd.jou')


	def grind(self, prefixes, **kwargs):

		'''
		parsing kwargs
		'''
		iters = self._kwarg_parse(kwargs.get('iters'), 1e3)
		model = self._kwarg_parse(kwargs.get('model'), 'kw-sst')
		work_name = self._kwarg_parse(kwargs.get('work_name'), '')
		test_points = self._kwarg_parse(kwargs.get('test_points'), {})

		'''
		if cluster
		'''
		self.job = 'grind'
		if not self.local:
			self._cluster()

		'''
		main journal setup
		'''
		master = pj.root()
		slave_names = []

		'''
		main loop start
		'''
		for r_key in self.r_keys:
			for h_key in self.h_keys: 
				for p_key in self.p_keys:
					for prefix in prefixes:

						'''
						setup
						'''
						slave = pj.root()
						slave_name = '{}-{}-{}-{}'.format(h_key, p_key, r_key, prefix)

						slave.file.read_case.set(
							path = '../cas/start.cas')
						slave.file.mesh_replace.set(
							path = '../msh/{}{}.msh'.format(work_name, slave_name))
						
						'''
						defining models
						'''
						slave.define.models.viscous.set(
							model = model)
						slave.solve.monitors.residual.convergence_criteria.set(
							criteria = [1e-6, 1e-6, 1e-6, 1e-6, 1e-6, 1e-6])

						for name, (x, y) in test_points.items():
							slave.surface.point_surface.set(
								name = name, x = x, y = y)

						'''
						defining bc
						'''
						slave.define.boundary_conditions.velocity_inlet.set( 
							name = 'inlet', velocity = Helper.reynolds.get(r_key), temperature = 300)
						slave.define.boundary_conditions.pressure_outlet.set(
							name = 'outlet', temperature = 300)
						slave.define.boundary_conditions.wall.set(
							name = 'wall-fluid', temperature = 1000)
						slave.define.boundary_conditions.wall.set(
							name = 'wall-solid', temperature = 1000, fluid = False)

						'''
						solving
						'''
						slave.solve.initialize.compute_defaults.velocity_inlet.set(
							name = 'inlet')
						slave.solve.initialize.initialize_flow.set()
						slave.solve.iterate.set(
							iters = iters)

						'''
						reporting
						'''
						slave.report.fluxes.mass_flow.set(
							path = '../out/out-{}{}.txt'.format(work_name, slave_name),
							all_zones = False, list_zones = ['inlet', 'outlet'])
						slave.report.fluxes.heat_transfer.set(
							path = '../out/out-{}{}.txt'.format(work_name, slave_name),
							all_zones = False, list_zones = ['wall-fluid', 'wall-solid', 'inlet', 'outlet'])
						for item in list(test_points.keys()):
							slave.report.surface_integrals.facet_avg.set(
								path = '../out/out-{}{}.txt'.format(work_name, slave_name), value = 'temperature', list_zones = item)
						slave.report.surface_integrals.facet_avg.set(
							path = '../out/out-{}{}.txt'.format(work_name, slave_name), value = 'pressure', list_zones = ['inlet', 'outlet'])
						
						slave.file.write_case_data.set(
							path = '../cas/{}{}.cas'.format(work_name, slave_name))

						'''
						ending
						'''
						slave_name = 'cmd-{}{}.jou'.format(work_name, slave_name)
						slave_names += [slave_name]
						slave.save('../cls/{}'.format(slave_name))

		'''
		saving all in a master file
		'''
		master.file.read_journal.set(path = slave_names)
		master.save(self.folder + '/cmd.jou')

	@staticmethod
	def _file_eval(path):
		vals = []
		with open(path, 'r') as f:
			for line in f.readlines():
				for char in line.split():
					try:
						vals += [float(char)]
					except:
						continue
		return (vals[2], vals[5], vals[6], vals[7] - vals[8])
			

	@staticmethod
	def _name_constructor(*args, prefix = None, suffix = None):
		name = [str(x) for x in [prefix] + list(args) + [suffix] if x != None]
		return '-'.join(name)

	def evaluate(self, **kwargs):

		suffixes = self._kwarg_parse(kwargs.get('suffixes'), [None])
		work_name = self._kwarg_parse(kwargs.get('work_name'), None)
		flt = self._kwarg_parse(kwargs.get('flt'), True)

		with open('../out/out.txt', 'w') as f:
			for h_key in self.h_keys:
				for p_key in self.p_keys:
					for r_key in self.r_keys:
						for suffix in suffixes:
							name = self._name_constructor(h_key, p_key, r_key, prefix = work_name, suffix = suffix)
							vals = self._file_eval(f'../out/out-{name}.txt')
							vals = ['%.4f' % x for x in list(vals)]
							f.write(f'{name}:\t' + '\t'.join(vals) + '\n')
