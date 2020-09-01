from helper import Helper
''' ======================== '''
cls_folder	= True
is_local	= False
''' ======================== '''
cls_script	= True
hours_count	= 4
partition	= 'cascadelake'
num_cpus	= None
''' ======================== '''
is_cyclic	= False
h_keys		= ['10', '50']
p_keys		= ['100']
r_keys		= ['010', '100', '400']
''' ======================== '''
work_name 	= 'REC-'
stab_name	= 'STAB'
test_name	= 'REC'
''' ======================== '''
turbulence_model		= 'ke-rng'
wall_function			= 'standard'
set_convergence			= True
convergence_criteria	= 1e-6
add_cuts				= True
iterations				= 1000
''' ======================== '''
prefixes	= [10, 20, 30, 40, 50, 75, 100, 150]
test_points	= {
	'point-1': (0.008, .0047),
	'point-2': (0.009, .0047),
	'point-3': (0.010, .0047)
}
''' ======================== '''
helper = Helper(folder = '../cls', cls_folder = cls_folder, 
	local = is_local, hours = hours_count, partition = partition, cpus = num_cpus,
	cyclic = is_cyclic, h_keys = h_keys, p_keys = p_keys, r_keys = r_keys)
# helper.build(test_name, stab_name)
# helper.solve(model = turbulence_model, iters = iterations)
# helper.grind(prefixes, model = 'ke-realizible', 
	# iters = '1000', test_points = test_points, work_name = 'REC')
helper.evaluate()