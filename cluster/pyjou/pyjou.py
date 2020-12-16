''' MAIN JOURNALING UNIT '''

''' SET FUNCTIONS '''
from pyjou.functions import *

''' AN EMPTY BRANCH CLASS '''
class branch:

	def __init__(self):
		pass

''' A BRANCH-ENDING CLASS '''
class executable:

	def __init__(self, parent, function):
		self.parent = parent
		self.function = function

	def add(self, *args, **kwargs):
		self.parent._cmd += [self.function(*args, **kwargs)]

''' MAIN JOURNALING CLASS '''
class Journal:

	''' DUNDER METHODS '''
	
	def __init__(self):
		self._cmd = []

		''' FILE SECTION '''
		self.file = branch()
		self.file.read_case = executable(self, read_case)
		self.file.read_journal = executable(self, read_journal)
		self.file.mesh_replace = executable(self, mesh_replace)
		self.file.write_case = executable(self, write_case)
		self.file.write_case_data = executable(self, write_case_data)
		
		''' DEFINE SECTION '''
		self.define = branch()
		self.define.bc = branch()
		self.define.bc.velocity_inlet = executable(self, bc_velocity_inlet)
		self.define.bc.pressure_outlet = executable(self, bc_pressure_outlet)
		self.define.bc.wall = executable(self, bc_wall)

		self.define.models = branch()
		self.define.models.viscous = executable(self, viscous)
		self.define.models.viscous.near_wall_treatment = executable(self, near_wall_treatment)

		''' SURFACE SECTION '''
		self.surface = branch()
		self.surface.line_surface = executable(self, line_surface)
		self.surface.point_surface = executable(self, point_surface)

		''' MESH SECTION '''
		self.mesh = branch()
		self.mesh.translate = executable(self, translate)

		self.mesh.modify_zones = branch()
		self.mesh.modify_zones.append_mesh = executable(self, append_mesh)
		self.mesh.modify_zones.merge_zones = executable(self, merge_zones)
		self.mesh.modify_zones.fuse_face_zones = executable(self, fuse_face_zones)
		self.mesh.modify_zones.zone_name = executable(self, zone_name)

		self.mesh.check = executable(self, check)

		self.mesh.repair_improve = branch()
		self.mesh.repair_improve.repair = executable(self, repair)

		''' SOLVE SECTION '''
		self.solve = branch()

		self.solve.monitors = branch()
		self.solve.monitors.residual = branch()
		self.solve.monitors.residual.convergence_criteria = executable(self, convergence_criteria)

		self.solve.initialize = branch()
		self.solve.initialize.initialize_flow = executable(self, initialize_flow)

		self.solve.initialize.compute_defaults = branch()
		self.solve.initialize.compute_defaults.velocity_inlet = executable(self, cd_velocity_inlet)

		self.solve.iterate = executable(self, iterate)

		''' REPORT SECTION '''
		self.report = branch()
		self.report.fluxes = branch()
		self.report.fluxes.mass_flow = executable(self, mass_flow)
		self.report.fluxes.heat_transfer = executable(self, heat_transfer)

		self.report.si = branch()
		self.report.si.area = executable(self, area)
		self.report.si.facet_avg = executable(self, facet_avg)
		self.report.si.area_weighted_avg = executable(self, area_weighted_avg)

		self.report.vi = branch()
		self.report.vi.mass_avg = executable(self, mass_avg)

	def __repr__(self):
		return f'<Journal Object( {len(self._cmd)} command line(s) )>'

	def __add__(self, other):
		self._cmd += other._cmd
		return self

	def __getitem__(self, index):
		return self._cmd[index]

	''' METHODS '''

	def comment(self, text):
		self._cmd.append(';%s' % text)

	def save(self, path):
			with open(path, 'w') as f:
				for item in self._cmd:
					f.write('%s\n' % item)
