from mylib import clean_folder, init_solve, jou, master

# ============ [SETUP] ============
clean_root		= True
clean_script	= True
job_type		= 'solve'

# BASH
local 			= False
hours_count		= 8
partition		= 'skylake'
cpus			= 'default'

# CYCLIC
cyclic			= True
h_keys			= 'all'
p_keys			= 'all'
Re_keys			= 'all'
wall_type		= 'ribbed'
prefix 			= ''

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
prefixes	= ['-0.1', '-0.25', '-0.5', '-0.75', '-1', '-1.25', '-1.5', '-2', '-5', '-10']
test_points	= True

# =================================

if clean_root:
	clean_folder()

if not local:
	if cpus == 'default':
		if job_type == 'build':
			cpus = 1
		else:
			cpus = 32
	init_solve(hours_count, partition, cpus, clean_script)
	
if cyclic:
	h_keys = list(jou.heights.keys())
	p_keys = list(jou.pitches.keys())
	Re_keys = list(jou.velos.keys())

if h_keys == 'all':
	h_keys = list(jou.heights.keys())
if p_keys == 'all':
	p_keys = list(jou.pitches.keys())
if Re_keys == 'all':
	Re_keys = list(jou.velos.keys())

def build():
	cmd_master = master()
	for Re_key in Re_keys:
		for h_key in h_keys: 
			for p_key in p_keys:
				cmd = jou(h_key, p_key, Re_key)
				cmd.define_build(stab_name, test_name)
				cmd.build()
				cmd.set_bc()
				cmd.write_case()
				cmd.savecmd()
				cmd_master.add_slave(cmd.case)
	cmd_master.savecmd()

def solve():
	cmd_master = master()
	for Re_key in Re_keys:
		for h_key in h_keys:
			for p_key in p_keys:
				cmd = jou(h_key, p_key, Re_key, prefix, wall_type)
				cmd.read_case()
				cmd.set_conv(1e-6)
				cmd.add_cuts()
				cmd.set_bc()
				cmd.solve(turbulence_model, iterations)
				cmd.add_report()
				cmd.write_case_data()
				cmd.savecmd()
				cmd_master.add_slave(cmd.case)
	cmd_master.savecmd()

def grind():
	cmd_master = master()
	for Re_key in Re_keys:
		for h_key in h_keys:
			for p_key in p_keys:
				for prefix in prefixes:
					cmd = jou(h_key, p_key, Re_key, prefix, wall_type)
					cmd.read_case('start')
					cmd.mesh_replace('FLAT-' + cmd.case)
					cmd.set_conv(1e-6)
					cmd.set_bc()
					# cmd.add_test_point('point-1', jou.pitches[p_key]*.3, cmd.diam*.95)
					# cmd.add_test_point('point-2', jou.pitches[p_key]*.6, cmd.diam*.97)
					# cmd.add_test_point('point-3', jou.pitches[p_key]*.9, cmd.diam*.95)
					cmd.add_test_point('point-1', .9, cmd.diam/2*.93)
					cmd.add_test_point('point-2', .9, cmd.diam/2*.95)
					cmd.add_test_point('point-3', .9, cmd.diam/2*.97)
					cmd.solve(turbulence_model, iterations)
					cmd.add_test_report()
					cmd.savecmd()
					cmd_master.add_slave(cmd.case)
	cmd_master.savecmd()

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
