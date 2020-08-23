import math
from glob import glob
import os
import shutil
import io
import pyjou as pj

# ============ [SETUP] ============
clean 			= True
clean_script	= True
job_type		= 'grind'

# BASH
local 			= False
hours_count		= 8
partition		= 'skylake'
cpus			= 'default'

# CYCLIC
cyclic			= False
h_keys			= ['10']
p_keys			= ['040']
Re_keys			= ['100']
wall_type		= 'ribbed'

# ============ [BUILD] ============
stab_name	= 'STAB'
test_name	= 'CUT'

# ============ [SOLVE] ============
turbulence_model		= 'kw_sst'
wall_function			= 'standard'
set_convergence			= True
convergence_criteria	= 1e-6
add_cuts				= True
iterations				= 1000

# ====== [GRID INDEPENDENCE] ======
prefixes	= ['0.1', '0.25', '0.5', '0.75', '1', '1.25', '1.5', '2', '5', '10']
test_points	= {
	'point-1': (0.05, .0047),
	'point-2': (0.10, .0047),
	'point-3': (0.15, .0047)
}

# =================================
# =================================
# =================================
# =================================
# =================================

'''
HELP FUNCTIONS
'''

def clean_folder(clean):
	path = '../cls'
	if clean:
		for file in glob(path + '/*'):
			try:
				os.remove(file)
			except:
				continue

def init_solve(hours, partition, cpus, script=False, root=''):
	if root == '':
		root = '../cls/'
	shutil.copy('passport.json', root + 'passport.json')
	shutil.copy('dispatcher.json', root + 'dispatcher.json')

	with open('cmd.txt', 'r') as file:
		cmd = file.read()

	cmd = cmd.replace('[hours]', str(hours))
	cmd = cmd.replace('[partition]', partition)
	cmd = cmd.replace('[cpus]', str(cpus))
	if script:
		shutil.copy('pycleaner.py', root + 'pycleaner.py')
		cmd = cmd.replace('[postscript]', 'python pycleaner.py')
	else:
		cmd = cmd.replace('[postscript]', '')

	with io.open(root + 'cmd.sh', 'w', newline='\n') as file:
		file.write(cmd)

'''
DICTIONARIES
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

velos = {
	'010': 14.60735,
	'020': 29.21469,
	'040': 58.42939,
	'100': 146.07347,
	'200': 292.14694,
	'400': 584.29388
}

'''
PARSE CONFIGURATION
'''

clean_folder(clean)

if not local:
	if cpus == 'default':
		if job_type == 'build':
			cpus = 1
		else:
			cpus = 32
	init_solve(hours_count, partition, cpus, clean_script)
	
if cyclic:
	h_keys = list(heights.keys())
	p_keys = list(pitches.keys())
	Re_keys = list(velos.keys())

if h_keys == 'all':
	h_keys = list(heights.keys())
if p_keys == 'all':
	p_keys = list(pitches.keys())
if Re_keys == 'all':
	Re_keys = list(velos.keys())

def build():

	def section_first(h_key, p_key, Re_key):
		slave.mesh.translate.set(slave, pitches.get(p_key), 0)
		slave.mesh.modify_zones.append_mesh.set(slave, '../msh/{}-{}-{}-{}'.\
			format(test_name, h_key, p_key, Re_key))
		slave.mesh.modify_zones.merge_zones.set(slave, ['fluid', 'fluid.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['axis', 'axis.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['interior', 'interior.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['interior-fluid', 'interior-fluid.1'])
		slave.mesh.modify_zones.zone_name.set(slave, 'wall', 'wall-out')
		slave.mesh.modify_zones.fuse_face_zones.set(slave, ['inlet', 'outlet.1'], 'delete-me')
		slave.mesh.modify_zones.merge_zones.set(slave, ['interior', 'delete-me'])
		slave.mesh.modify_zones.zone_name.set(slave, 'inlet.1', 'inlet')

	def section_nth(h_key, p_key, Re_key):
		slave.mesh.translate.set(slave, pitches.get(p_key), 0)
		slave.mesh.modify_zones.append_mesh.set(slave, '../msh/{}-{}-{}-{}'.\
			format(test_name, h_key, p_key, Re_key))
		slave.mesh.modify_zones.merge_zones.set(slave, ['fluid', 'fluid.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['solid', 'solid.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['axis', 'axis.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['interior', 'interior.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['interior-fluid', 'interior-fluid.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['interior-solid', 'interior-solid.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['sides', 'sides.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['wall-fluid', 'wall-fluid.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['wall-solid', 'wall-solid.1'])
		slave.mesh.modify_zones.fuse_face_zones.set(slave, ['inlet', 'outlet.1'], 'delete-me')
		slave.mesh.modify_zones.merge_zones.set(slave, ['interior', 'delete-me'])
		slave.mesh.modify_zones.zone_name.set(slave, 'inlet.1', 'inlet')

	def section_last(h_key, p_key, Re_key):
		slave.mesh.translate.set(slave, .1, 0)
		slave.mesh.modify_zones.append_mesh.set(slave, '../msh/{}-{}-{}-{}'.\
			format(stab_name, h_key, p_key, Re_key))
		slave.mesh.modify_zones.merge_zones.set(slave, ['fluid', 'fluid.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['axis', 'axis.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['interior', 'interior.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['interior-fluid', 'interior-fluid.1'])
		slave.mesh.modify_zones.merge_zones.set(slave, ['wall-out', 'wall'])
		slave.mesh.modify_zones.fuse_face_zones.set(slave, ['inlet', 'outlet.1'], 'delete-me')
		slave.mesh.modify_zones.merge_zones.set(slave, ['interior', 'delete-me'])
		slave.mesh.modify_zones.zone_name.set(slave, 'inlet.1', 'inlet')

	master = pj.root()
	slave_names = []

	for Re_key in Re_keys:
		for h_key in h_keys: 
			for p_key in p_keys:

				slave = pj.root()
				slave_name = '{}-{}-{}'.format(h_key, p_key, Re_key)

				slave.file.read_case.set(slave, '../cas/start.cas')
				slave.file.mesh_replace.set(slave, '../msh/{}-{}-{}-{}.msh'.\
					format(stab_name, h_key, '100', Re_key))
				section_first(h_key, p_key, Re_key)
				numsec = int(8e-1/pitches[p_key])

				for i in range(0, numsec - 1):
					section_nth(h_key, p_key, Re_key)
				
				section_last(h_key, p_key, Re_key)

				slave.mesh.check.set(slave)
				slave.mesh.repair_improve.repair.set(slave)

				slave.define.boundary_conditions.velocity_inlet.set(slave, 
					'inlet', velos.get(Re_key), 300)
				slave.define.boundary_conditions.pressure_outlet.set(slave,
					'outlet', 300)
				slave.define.boundary_conditions.wall.set(slave,
					'wall-fluid', 1000)
				slave.define.boundary_conditions.wall.set(slave,
					'wall-solid', 1000, False)
				slave.define.boundary_conditions.wall.set(slave,
					'wall-out', 1000)
				slave.file.write_case.set(slave, '../cas/{}-{}'.\
					format(test_name, slave_name))

				slave_name = 'cmd-{}.jou'.format(slave_name)
				slave_names += [slave_name]
				slave.save('../cls/{}'.format(slave_name))

	master.file.read_journal.set(master, slave_names)
	master.save('../cls/cmd.jou')

def solve():
	master = pj.root()
	slave_names = []

	for Re_key in Re_keys:
		for h_key in h_keys: 
			for p_key in p_keys:

				slave = pj.root()
				slave_name = '{}-{}-{}'.format(h_key, p_key, Re_key)

				slave.file.read_case.set(slave, '{}-{}.cas'.\
					format(test_name, slave_name))

				slave.define.models.viscous.set(slave, turbulence_model)
				slave.solve.monitors.residual.convergence_criteria.set(slave, 1e-6)
				slave.surface.line_surface.set(slave, 'cut-1', .1, 0, .1, .005)
				slave.surface.line_surface.set(slave, 'cut-2', .9, 0, .9, .005)

				slave.define.boundary_conditions.velocity_inlet.set(slave, 
					'inlet', velos.get(Re_key), 300)
				slave.define.boundary_conditions.pressure_outlet.set(slave,
					'outlet', 300)
				slave.define.boundary_conditions.wall.set(slave,
					'wall-fluid', 1000)
				slave.define.boundary_conditions.wall.set(slave,
					'wall-solid', 1000, False)
				slave.define.boundary_conditions.wall.set(slave,
					'wall-out', 1000)

				slave.solve.initialize.compute_defaults.velocity_inlet.set(slave, 'inlet')
				slave.solve.initialize.initialize_flow.set(slave)
				slave.solve.iterate.set(slave, iterations)

				slave.report.surface_integrals.area.set(slave,
					'../out/out-{}.txt'.format(slave_name), ['wall-fluid', 'wall-solid'])
				slave.report.fluxes.heat_transfer.set(slave, 
					'../out/out-{}.txt'.format(slave_name), all_zones = False, 
					list_zones=['wall-fluid', 'wall-solid'])
				slave.report.surface_integrals.facet_avg.set(slave,
					'../out/out-{}.txt'.format(slave_name), 'temperature', 'axis')
				slave.report.surface_integrals.facet_avg.set(slave,
					'../out/out-{}.txt'.format(slave_name), 'pressure', ['cut-1', 'cut-2'])
				
				slave.file.write_case_data.set(slave, 
					'../cas/{}-{}.cas'.format(test_name, slave_name))

				slave_name = 'cmd-{}.jou'.format(slave_name)
				slave_names += [slave_name]
				slave.save('../cls/{}'.format(slave_name))

	master.file.read_journal.set(master, slave_names)
	master.save('../cls/cmd.jou')

def grind():
	master = pj.root()
	slave_names = []

	for Re_key in Re_keys:
		for h_key in h_keys: 
			for p_key in p_keys:
				for prefix in prefixes:

					slave = pj.root()
					slave_name = '{}-{}-{}-{}'.format(h_key, p_key, Re_key, prefix)

					slave.file.read_case.set(slave, '../cas/start.cas')
					slave.file.mesh_replace.set(slave, 
						'../msh/{}-{}'.format(test_name, slave_name))

					slave.define.models.viscous.set(slave, turbulence_model)
					slave.solve.monitors.residual.convergence_criteria.set(slave, 1e-6)
					slave.surface.line_surface.set(slave, 'cut-1', .1, 0, .1, .005)
					slave.surface.line_surface.set(slave, 'cut-2', .9, 0, .9, .005)

					for name, (x, y) in test_points.items():
						slave.surface.point_surface.set(slave, name, x, y)

					slave.define.boundary_conditions.velocity_inlet.set(slave, 
						'inlet', velos.get(Re_key), 300)
					slave.define.boundary_conditions.pressure_outlet.set(slave,
						'outlet', 300)
					slave.define.boundary_conditions.wall.set(slave,
						'wall-fluid', 1000)
					slave.define.boundary_conditions.wall.set(slave,
						'wall-solid', 1000, False)
					slave.define.boundary_conditions.wall.set(slave,
						'wall-out', 1000)

					slave.solve.initialize.compute_defaults.velocity_inlet.set(slave, 'inlet')
					slave.solve.initialize.initialize_flow.set(slave)
					slave.solve.iterate.set(slave, iterations)

					slave.report.fluxes.mass_flow.set(slave,
						'../out/out-{}.txt'.format(slave_name))
					slave.report.fluxes.heat_transfer.set(slave, 
						'../out/out-{}.txt'.format(slave_name))

					for item in list(test_points.keys()):
						slave.report.surface_integrals.facet_avg.set(slave,
							'../out/out-{}.txt'.format(slave_name), 'temperature', item)
					
					slave.report.surface_integrals.facet_avg.set(slave,
						'../out/out-{}.txt'.format(slave_name), 'pressure', ['cut-1', 'cut-2'])
					
					slave.file.write_case_data.set(slave, 
						'../cas/{}-{}.cas'.format(test_name, slave_name))

					slave_name = 'cmd-{}.jou'.format(slave_name)
					slave_names += [slave_name]
					slave.save('../cls/{}'.format(slave_name))

	master.file.read_journal.set(master, slave_names)
	master.save('../cls/cmd.jou')

def evaluate():
	cmd_master = master()
	for Re_key in Re_keys:
		for h_key in h_keys:
			for p_key in p_keys:
				cmd = jou(h_key, p_key, Re_key, prefix, wall_type)
				cmd.evaluate()
				cmd_master.add_slave_value(cmd)
	cmd_master.saveval()

jobs = {
	'build': build,
	'solve': solve,
	'grind': grind,
	'evaluate': evaluate
}

job = jobs.get(job_type, lambda: 'Error 404: Invalid job name')
job()
