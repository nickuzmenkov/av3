from glob import glob
import shutil
import os
import io

class Helper():

	def __init__(self, folder):
		self.folder = folder
		self.cmd = ''

	''' simple solver '''
	def add_solver(self, case, velocity, mesh=None, iters=1000):
		self.cmd += '\n'
		cmd = [
			f'/file/read-case "../cas/{case}.cas" ',
			f'/file/replace-mesh "../msh/{mesh}.msh"' if mesh else '',
			'/solve/initialize/compute-defaults/velocity-inlet inlet ',
			f'/define/bc/velocity-inlet inlet no no yes yes no {velocity} no 0 no 300 no no no yes 5 .01',
			'/solve/initialize initialize-flow yes ',
			f'/solve/iterate {iters} ',
			f'/file/write-case-data "../cas/{mesh if mesh else case}.cas" yes'
		]
		self.cmd += '\n'.join(cmd)

	''' simple reporter '''
	def add_reporter(self, name):
		self.cmd += '\n'
		cmd = [
			'/report/volume-integrals mass-avg fluid () viscosity-lam ',
			'/report/surface-integrals area wall-fluid wall-solid () ',
			'/report/surface-integrals area-weighted-avg wall-fluid sides sides-shadow () heat-transfer-coef ',
			'/report/surface-integrals area-weighted-avg cut-1 cut-2 () pressure '
		]
		saver = f'yes "../out/{name}.txt" yes '
		self.cmd += '\n'.join([x + saver for x in cmd])

	''' clear working folder + write journal '''
	def execute(self, **kwargs):
		''' clear working folder '''
		for file in glob(self.folder + '/*'):
			try:
				os.remove(file)
			except:
				print(f'failed deleting {file}\n')
				continue

		''' evaluate kwargs '''
		hours = kwargs.get('hours', 12)
		partition = kwargs.get('partition', 'cascadelake')
		cpus = kwargs.get('cpus', 32)
		dim = kwargs.get('dim', 3)

		''' mutate sh script '''
		with open('cmd.sh', 'r') as file:
			sh = file.read()

		sh = sh.replace('[hours]', str(hours)).\
				replace('[partition]', partition).\
				replace('[cpus]', str(cpus)).\
				replace('[dim]', str(dim)).\
				replace('[postscript]', 'python pycleaner.py')

		''' copy all necessary files '''
		shutil.copy('passport.json', self.folder + '/passport.json')
		shutil.copy('pycleaner.py', self.folder + '/pycleaner.py')

		with io.open(self.folder + '/cmd.sh', 'w', newline='\n') as file:
			file.write(sh)

		with open(self.folder + '/cmd.jou', 'w') as file:
			file.write(self.cmd)

	@staticmethod
	def values(path):
		data = []
		with open(path, 'r') as file:
			for line in file.readlines():
				for x in line.split():
					try:
						data.append(float(x))
					except ValueError:
						continue
		return data

	def evaluate(self):
		''' delete previous out file '''
		try:
			os.remove('..\\..\\..\\out\\out.txt')
		except FileNotFoundError:
			pass
		
		''' collect data '''
		data = [['Re\t', 'Nu', 'fr']]
		for path in glob('..\\..\\..\\out\\*.txt'):
			row = self.values(path)

			''' evaluate '''
			Re = 20 * 1.225 * .01 / row[0]
			Nu = (row[5] + max(row[6], row[7])) * .01 / .0242
			fr = 2 * (row[9] - row[10]) * .01 / .1 / 1.225 / 20 ** 2

			data.append(['%.2e' % Re, '%.2f' % Nu, '%.6f' % fr])

		data = '\n'.join(['\t'.join(x) for x in data])
		print(data)
		with open('../../../out/out.txt', 'w') as file:
			file.write(data)
				