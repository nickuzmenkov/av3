''' SET FUNCTIONS '''
_yn = {True: 'yes', False: 'no'}

''' FILE SECTION '''
def read_case(path, **kwargs):
	overwrite = kwargs.get('overwrite', True)
	return f'/file/read-case "{path}.cas" {_yn.get(overwrite)} '

def read_journal(*args):
	return '/file/read-journal\n{}'.format('\n'.join(args))

def write_case(path, **kwargs):
	overwrite = kwargs.get('overwrite', True)
	return f'/file/write-case "{path}.cas" {overwrite} '

def write_case_data(path, **kwargs):
	overwrite = kwargs.get('overwrite', True)
	return f'/file/write-case-data "{path}.cas" {overwrite} '

def mesh_replace(path, **kwargs):
	discard = kwargs.get('discard', True)
	return f'/file/replace-mesh "{path}.msh" {_yn.get(discard)} '

''' DEFINE SECTION '''
def bc_velocity_inlet(zone, velocity, temperature, **kwargs):
	return f'/define/boundary-conditions velocity-inlet {zone} no yes yes no 0 no {velocity} no 0 no {temperature} no no no yes 5 0.01 '

def bc_pressure_outlet(zone, temperature, **kwargs):
	return f'/define/boundary-conditions/pressure-outlet {zone} yes no 0. no {temperature} no yes no no n yes 5. 0.01 yes no no no '

def bc_wall(zone, temperature, fluid=True, **kwargs):
	if fluid:
		return f'/define/boundary-conditions/wall {zone} 0. no 0. no yes temperature no {temperature} no no no 0. no 0. no 1 '
	else:
		return f'/define/boundary-conditions/wall {zone} 0. no 0. no yes temperature no {temperature} no 1 '

def viscous(model):
	return f'/define/models/viscous/{model} yes '

def near_wall_treatment(wall_fcn):
	return f'/define/models/viscous/near-wall-treatment {wall_fcn} yes '

''' SURFACE SECTION '''
def line_surface(name, x1, y1, x2, y2):
	return f'/surface/line-surface {name} {x1} {y1} {x2} {y2}'

def point_surface(name, x, y):
	return f'/surface/point-surface {name} {x} {y}'

''' MESH SECTION '''
def translate(x, y):
	return f'/mesh/translate {x} {y} '

def append_mesh(path):
	return f'/mesh/modify-zones/append-mesh "{path}" '

def merge_zones(*args):
	return f'/mesh/modify-zones/merge-zones {" ".join(args)} () '

def fuse_face_zones(*args, **kwargs):
	fused_name = kwargs.get('fused_name', 'delete-me')
	return f'/mesh/modify-zones/fuse-face-zones {" ".join(args)} () {fused_name} '

def zone_name(old_name, new_name):
	return f'/mesh/modify-zones/zone-name {old_name} {new_name} '

def check():
	return '/mesh/check '
	
def repair():
	return '/mesh/repair-improve/repair '

''' SOLVE SECTION '''
def convergence_criteria(crit):
	return f'/solve/monitors/residual convergence-criteria {(str(crit) + " ") * 6}'

def cd_velocity_inlet(zone):
	return f'/solve/initialize/compute-defaults/velocity-inlet {zone} '

def initialize_flow():
	return '/solve/initialize initialize-flow yes '

def iterate(iters):
	return f'/solve/iterate {iters} '

''' REPORT SECTION '''
def mass_flow(path, *args, all_zones = False):
	if all_zones:
		return f'/report/fluxes/mass-flow yes yes "{path}" yes '
	else:
		return f'/report/fluxes/mass-flow no {" ".join(args)} () yes "{path}" yes '

def heat_transfer(path, *args, all_zones = False):
	if all_zones:
		return f'/report/fluxes/heat-transfer yes yes "{path}" yes '
	else:
		return f'/report/fluxes/heat-transfer no {" ".join(args)} () yes "{path}" yes '

def area(path, *args):
	return f'/report/surface-integrals/area {" ".join(args)} () yes "{path}" yes '

def facet_avg(path, value, *args):
	return f'/report/surface-integrals/facet-avg {" ".join(args)} () {value} yes "{path}" y '

def area_weighted_avg(path, value, *args):
	return f'/report/surface-integrals/area-weighted-avg {" ".join(args)} () {value} yes "{path}" y '

def mass_avg(path, value, *args):
	return f'/report/volume-integrals/mass-avg {" ".join(args)} () {value} yes "{path}" y '