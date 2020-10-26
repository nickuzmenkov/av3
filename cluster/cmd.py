from helper import Helper

''' ======================== '''

dim = 3
cls_folder	= True
is_local	= False

''' ======================== '''

cls_script	= True
hours_count	= 2
partition	= 'aviator3'
num_cpus	= None

''' ======================== '''

is_cyclic	= False
h_keys		= ['10']
p_keys		= ['100']
r_keys		= ['010']

''' ======================== '''

stab_name	= 'STAB'
test_name	= 'REC'

''' ======================== '''

model	= 'spalart-allmaras'
wall_fcn = 'standard'
crit	= 1e-6
iters	= 1000

''' ======================== '''

prefixes = [None]
suffixes = [None]
test_points = { 
	'point-1': (0.008, .0047),
	'point-2': (0.009, .0047),
	'point-3': (0.010, .0047)
}

''' ======================== '''

helper = Helper(
	folder = '../../../cls', cls_folder = cls_folder, cls_script = cls_script,
	local = is_local, hours = hours_count, partition = partition, cpus = num_cpus,
	cyclic = is_cyclic, dim=dim,
	h_keys = h_keys, p_keys = p_keys, r_keys = r_keys)

# helper.evaluate(suffixes = suffixes)

# helper.evaluate_flat(suffixes = suffixes)

helper.build(test_name, stab_name, prefixes = prefixes, suffixes = suffixes)

# helper.solve(prefixes = prefixes, suffixes = suffixes, model = model, wall_function = wall_fcn, iters = iters, criteria = crit)

# helper.solve_flat(prefixes = prefixes, suffixes = suffixes, model = model, wall_function = wall_fcn, iters = iters, criteria = crit)

# helper.grind(prefixes = prefixes, suffixes = suffixes, model = model, wall_function = wall_fcn, iters = iters, criteria = crit)
