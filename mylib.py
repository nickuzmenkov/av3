import math
from glob import glob
import os
import shutil
import io

def clean_folder(path=''):
	if path == '':
		path = '../cls'
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

class jou:
	
	# ---------------
	# CLASS VARIABLES
	# ---------------

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

	velos = {
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

	fr0 = {
		'010': 1,
		'020': 1,
		'040': 1,
		'100': 1,
		'200': 1,
		'400': 1
	}

	# -------------
	# CLASS METHODS
	# -------------

	def __init__(self, h_key, p_key, Re_key, prefix='', wall_type='ribbed'):
		self.case = '{}-{}-{}{}'.format(h_key, p_key, Re_key, prefix)

		self.stab_leng = .1
		self.test_leng = .8
		self.diam = 1e-2
		self.viscous = 1.7894e-5
		self.density = 1.225
		self.conduct = 0.0242
		self.dimensions = 2

		self.h_key = h_key
		self.p_key = p_key
		self.Re_key = Re_key
		self.wall_type = wall_type

		self.test_points = []
		self.cmd = []
	
	# ---------------
	# REGULAR METHODS
	# ---------------

	def read_case(self, case=''):
		if case == '':
			case = self.case
		self.cmd += ['/file/read-case "../cas/{}.cas" y '.format(case)]

	def mesh_replace(self, mesh=''):
		if mesh == '':
			mesh = self.case
		self.cmd += ['/file/replace-mesh ../msh/{}.msh y '.format(mesh)]

	def set_conv(self, crit):
		self.cmd += [
			'/solve/monitors/residual convergence-criteria {0} {0} {0} {0} {0} {0}'.format(crit)
		]

	def add_cuts(self):
		self.cmd += [
			'/surface/line-surface cut-1 {0} 0 {0} {1}'.format(self.stab_leng, self.diam/2), 
			'/surface/line-surface cut-2 {0} 0 {0} {1}'.format(self.stab_leng + self.test_leng, self.diam/2)
		]

	def set_bc(self):
		self.cmd += [
			# pressure based solver
			'/define/boundary-conditions velocity-inlet inlet no yes yes no 0 no {} no 0 no 300 no no no yes 5 0.01 '.format(jou.velos[self.Re_key]),
			# density based solver
			# '/define/boundary-conditions velocity-inlet inlet no yes yes no 0 no {} no 0 no 300 no no no yes 5 0.01 no 0 '.format(jou.velos[self.Re_key]),
			'/define/boundary-conditions/pressure-outlet outlet yes no 0. no 300. no yes no no n yes 5. 0.01 yes no no no ',
			'/define/boundary-conditions/wall wall-out 0. no 0. no y temperature no 1000 no no no 0. no 0. no 1 '
		]
		if self.wall_type == 'flat':
			self.cmd += [
				'/define/boundary-conditions/wall wall 0. no 0. no y temperature no 1000 no no no 0. no 0. no 1 '
			]
		if self.wall_type == 'ribbed':
			self.cmd += [
				'/define/boundary-conditions/wall wall-fluid 0. no 0. no y temperature no 1000 no no no 0. no 0. no 1 ',
				'/define/boundary-conditions/wall wall-solid 0. no 0. no yes temperature no 1000 no 1 '
			]

	def solve(self, model, iters):
		self.cmd += [
			'/define/models/viscous/{} yes '.format(model),
			# '/define/models/viscous/near-wall-treatment/menter-lechner yes ',
			'/solve/initialize/compute-defaults/velocity-inlet inlet',
			'/solve/initialize initialize-flow y ',
			'/solve/iterate {} '.format(iters)
		]

	def add_report(self):
		if self.wall_type == 'ribbed':
			self.cmd += [
				'/report/surface-integrals/area wall-fluid wall-solid () yes "../out/out-{}.txt" y '.format(self.case),
				'/report/fluxes/heat-transfer no wall-fluid wall-solid () yes "../out/out-{}.txt" y '.format(self.case)
			]
		if self.wall_type == 'flat':
			self.cmd += [
				'/report/surface-integrals/area wall () yes "../out/out-{}.txt" y '.format(self.case),
				'/report/fluxes/heat-transfer no wall () yes "../out/out-{}.txt" y '.format(self.case)
			]
		self.cmd += [
			'/report/surface-integrals/facet-avg axis () temperature yes "../out/out-{}.txt" y '.format(self.case),
			'/report/surface-integrals/mass-weighted-avg cut-1 cut-2 () pressure yes "../out/out-{}.txt" y '.format(self.case)
		]

	def write_case(self):
		self.cmd += ['/file/write-case/ "../cas/{}.cas" y '.format(self.case)]

	def write_case_data(self):
		self.cmd += ['/file/write-case-data/ "../cas/{}.cas" y '.format(self.case)]

	# -------------------------------
	# GRID INDEPENDENCY CHECK METHODS
	# -------------------------------

	def set_test_bc(self):
		self.cmd += [
			'/define/boundary-conditions velocity-inlet inlet no yes yes no 0 no {} no 0 no 300 no no no yes 5 0.01 '.format(jou.velos[self.Re_key]),
			'/define/boundary-conditions/pressure-outlet outlet yes no 0. no 300. no yes no no n yes 5. 0.01 yes no no no ',
			'/define/boundary-conditions/wall wall-fluid 0. no 0. no y temperature no 1000 no no no 0. no 0. no 1 ',
			'/define/boundary-conditions/wall wall-solid 0. no 0. no yes temperature no 1000 no 1 '
		]

	def add_test_point(self, name, x, y):
		self.test_points += [name]
		self.cmd += ['/surface/point-surface {} {} {}'.format(name, x, y)]

	def add_test_report(self):
		self.cmd += [
			'/report/fluxes/mass-flow no inlet outlet () yes "../out/out-{}.txt" y '.format(self.case),
			'/report/fluxes/heat-transfer yes yes "../out/out-{}.txt" y '.format(self.case)			
		]

		for point in self.test_points:
			self.cmd += ['/report/surface-integrals/facet-avg {} () temperature yes "../out/out-{}.txt" y '.format(point, self.case)]

	# -------------
	# BUILD METHODS
	# -------------

	def section_1st(self, mesh):
		self.cmd += [
			'/mesh/translate {} 0. '.format(jou.pitches[self.p_key]),
			'/mesh/modify-zones/append-mesh "../msh/{}.msh" '.format(mesh),
			'/mesh/modify-zones/merge-zones fluid fluid.1 () ',
			'/mesh/modify-zones/merge-zones axis axis.1 () ',
			'/mesh/modify-zones/merge-zones interior interior.1 () ',
			'/mesh/modify-zones/merge-zones interior-fluid interior-fluid.1 () ',
			'/mesh/modify-zones/zone-name wall wall-out ',
			'/mesh/modify-zones/fuse-face-zones inlet outlet.1 () delete-me ',
			'/mesh/modify-zones/merge-zones interior delete-me () ',
			'/mesh/modify-zones/zone-name inlet.1 inlet '
		]

	def section_nth(self, mesh):
		self.cmd += [
			'/mesh/translate {} 0 '.format(jou.pitches[self.p_key]),
			'/mesh/modify-zones/append-mesh "../msh/{}.msh" '.format(mesh),
			'/mesh/modify-zones/merge-zones fluid fluid.1 () ',
			'/mesh/modify-zones/merge-zones solid solid.1 () ',
			'/mesh/modify-zones/merge-zones axis axis.1 () ',
			'/mesh/modify-zones/merge-zones interior interior.1 () ',
			'/mesh/modify-zones/merge-zones interior-fluid interior-fluid.1 () ',
			'/mesh/modify-zones/merge-zones interior-solid interior-solid.1 () ',
			'/mesh/modify-zones/merge-zones sides sides.1 () ',
			'/mesh/modify-zones/merge-zones wall-fluid wall-fluid.1 () ',
			'/mesh/modify-zones/merge-zones wall-solid wall-solid.1 () ',
			'/mesh/modify-zones/fuse-face-zones inlet outlet.1 () delete-me ',
			'/mesh/modify-zones/merge-zones interior delete-me () ',
			'/mesh/modify-zones/zone-name inlet.1 inlet '
		]

	def section_last(self, mesh):
		self.cmd += [
			'/mesh/translate {} 0. '.format(self.stab_leng),
			'/mesh/modify-zones/append-mesh "../msh/{}.msh" '.format(mesh),
			'/mesh/modify-zones/merge-zones fluid fluid.1 () ',
			'/mesh/modify-zones/merge-zones axis axis.1 () ',
			'/mesh/modify-zones/merge-zones interior interior.1 () ',
			'/mesh/modify-zones/merge-zones interior-fluid interior-fluid.1 () ',
			'/mesh/modify-zones/merge-zones wall-out wall () ',
			'/mesh/modify-zones/fuse-face-zones outlet.1 inlet () delete-me ',
			'/mesh/modify-zones/merge-zones interior delete-me () ',
			'/mesh/modify-zones/zone-name inlet.1 inlet '
		]

	def mesh_repair(self):
		self.cmd += [
			'/mesh/check '
			'/mesh/repair-improve/repair ']

	def define_build(self, stab_name, test_name):
		self.stab = '{}-{}-{}-{}'.format(stab_name, self.h_key, int(self.stab_leng*1e3), self.Re_key)
		self.test = '{}-{}-{}-{}'.format(test_name, self.h_key, self.p_key, self.Re_key)

	def build(self):
		self.read_case('start')
		self.mesh_replace(self.stab)
		self.section_1st(self.test)

		numsec = int(8e-1/jou.pitches[self.p_key])
		for i in range(0, numsec - 1):
			self.section_nth(self.test)
		
		self.section_last(self.stab)
		self.mesh_repair()

	def savecmd(self, path=''):
		if path == '':
			path = '../cls/cmd-{}.jou'.format(self.case)
		with open(path, 'w') as f:
			for item in self.cmd:
				f.write('%s\n' % item)

	def get_out(self):
		with open('../out/out-{}.txt'.format(self.case)) as f:
			data = f.readlines()
		buf = []
		for line in data:
			for word in line.split():
				try:
					buf += [float(word)]
					break
				except:
					continue
		try:
			if self.wall_type == 'flat':
				return (buf[0], buf[1], buf[3], buf[4] - buf[5])
			if self.wall_type == 'ribbed':
				return (buf[2], buf[5], buf[6], buf[7] - buf[8])
		except:
			return (float('nan'), float('nan'), float('nan'), float('nan'))

	def evaluate(self):
		(area, heat, temp, pres) = self.get_out()

		leng = area/math.pi/self.diam

		self.Nu = heat/area/(1000 - temp)*self.diam/self.conduct/jou.Nu0[self.Re_key]
		self.fr = 2*pres*self.diam/leng/self.density/jou.velos[self.Re_key] ** 2/jou.fr0[self.Re_key]

class master:

	def __init__(self):
		self.cmd = ['/file/read-journal ']
		self.slaves = []
		self.Nu = []
		self.fr = []

	def add_slave(self, slave):
		self.slaves += [slave]
		self.cmd += ['cmd-{}.jou '.format(slave)]

	def add_slave_value(self, slave):
		self.slaves += [slave.case]
		self.Nu += [slave.Nu]
		self.fr += [slave.fr]

	def savecmd(self, path=''):
		if path == '':
			path = '../cls/cmd.jou'
		with open(path, 'w') as f:
			for item in self.cmd:
				f.write('%s\n' % item)

	def saveval(self, path=''):
		if path == '':
			path = '../out/out.txt'
		with open(path, 'w') as f:
			for slaves, Nu, fr in zip(self.slaves, self.Nu, self.fr):
				f.write('{}\t{}\t{}\n'.format(slaves, '%.4f' % Nu, '%.4f' % fr))
