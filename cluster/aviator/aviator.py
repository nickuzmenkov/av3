from pyjou import Journal
from glob import glob
import shutil
import os
import io


class Aviator():


	def __init__(self, folder, starter_case):
		self.folder = folder
		self.jou = Journal()
		self.jou.file.read_case.add('../cas/' + starter_case)


	def clear_folder(self):
		for file in glob(self.folder + '/*'):
			try:
				os.remove(file)
			except:
				print(f'failed deleting {file}\n')
				continue
	

	@property
	def shell(self):
		with open('aviator/cmd.sh', 'r') as f:
			shell = f.read()
			return shell


	@shell.setter
	def shell(self, cmd):
		with io.open(self.folder + '/cmd.sh', 'w', newline='\n') as f:
			f.write(cmd)


	def shell_mutator(self, cmd, **kwargs):
		hours = kwargs.get('hours', 12)
		partition = kwargs.get('partition', 'cascadelake')
		dim = kwargs.get('dim', 3)
		nodes = kwargs.get('nodes', 1)

		cmd = cmd.replace('[hours]', str(hours)).\
			      replace('[nodes]', str(nodes)).\
			      replace('[partition]', partition).\
			      replace('[dim]', str(dim)).\
			      replace('[postscript]', 'python pycleaner.py')
		return cmd


	def execute(self, **kwargs):
		self.clear_folder()		

		shell = self.shell
		self.shell = self.shell_mutator(shell, **kwargs)
		
		shutil.copy('aviator/passport.json', self.folder + '/passport.json')
		shutil.copy('aviator/pycleaner.py', self.folder + '/pycleaner.py')

		self.jou.save(self.folder + '/cmd.jou')


	def job(self, job, msh, vel):
		''' comment the beginning '''
		self.jou.comment(' %s START' % job)
		''' solver section '''
		self.jou.file.mesh_replace.add('../msh/' + msh)
		self.jou.define.bc.velocity_inlet.add('inlet', vel, 300)
		self.jou.solve.initialize.compute_defaults.velocity_inlet.add('inlet')
		self.jou.solve.initialize.initialize_flow.add()
		self.jou.solve.iterate.add(500)
		''' reporter section '''
		self.jou.report.si.area.add(f'../out/{job}.txt', 'wall-fluid', 'wall-solid')
		# self.jou.report.si.area.add(f'../out/{job}.txt', 'wall-fluid') # flat
		self.jou.report.si.area_weighted_avg.add(f'../out/{job}.txt', 'velocity', 'inlet')
		self.jou.report.vi.mass_avg.add(f'../out/{job}.txt', 'viscosity-lam', 'fluid')
		self.jou.report.vi.mass_avg.add(f'../out/{job}.txt', 'temperature', 'fluid')
		self.jou.report.fluxes.heat_transfer.add(f'../out/{job}.txt', 'wall-fluid', 'wall-solid')
		# self.jou.report.fluxes.heat_transfer.add(f'../out/{job}.txt', 'wall-fluid') # flat
		self.jou.report.si.area_weighted_avg.add(f'../out/{job}.txt', 'pressure', 'cut-1', 'cut-2')
		''' comment the ending '''
		self.jou.comment(' %s END' % job)
