def secs_flat(mesh_test, mesh_stab):
	return [
	'/file/read-case "../cas/start.cas" y',
	'/mesh/translate 0. 0. 0.5 ',
	'/mesh/modify-zones/append-mesh "../msh/{}.msh" '.format(mesh_test),
	'/mesh/modify-zones/merge-zones fluid fluid.1 () ',
	'/mesh/modify-zones/merge-zones interior interior.1 () ',
	'/mesh/modify-zones/merge-zones interior-fluid interior-fluid.1 () ',
	'/mesh/modify-zones/zone-name wall-solid wall-out ',
	'/mesh/modify-zones/fuse-face-zones inlet outlet.1 () delete-me ',
	'/mesh/modify-zones/merge-zones interior delete-me () ',
	'/mesh/modify-zones/zone-name inlet.1 inlet ',
	'/mesh/translate 0. 0. 0.1 ',
	'/mesh/modify-zones/append-mesh "../msh/{}.msh" '.format(mesh_stab),
	'/mesh/modify-zones/merge-zones fluid fluid.1 ()',
	'/mesh/modify-zones/merge-zones interior interior.1 () ',
	'/mesh/modify-zones/merge-zones interior-fluid interior-fluid.1 ()',
	'/mesh/modify-zones/zone-name wall-solid wall-outlet',
	'/mesh/modify-zones/merge-zones wall-out wall-outlet () ',
	'/mesh/modify-zones/fuse-face-zones inlet outlet.1 () delete-me ',
	'/mesh/modify-zones/merge-zones interior delete-me () ',
	'/mesh/modify-zones/zone-name inlet.1 inlet '
	]

def sec_first(mesh):
	return [
	'/file/read-case "../cas/start.cas"',
	'/mesh/translate 0. 0. 0.005 ',
	'/mesh/modify-zones/append-mesh "../msh/{}.msh" '.format(mesh),
	'/mesh/modify-zones/merge-zones fluid fluid.1 () ',
	'/mesh/modify-zones/merge-zones interior interior.1 () ',
	'/mesh/modify-zones/merge-zones interior-fluid interior-fluid.1 () ',
	'/mesh/modify-zones/zone-name wall-solid wall-out ',
	'/mesh/modify-zones/zone-name wall-solid.1 wall-solid ',
	'/mesh/modify-zones/fuse-face-zones inlet outlet.1 () delete-me ',
	'/mesh/modify-zones/merge-zones interior delete-me () ',
	'/mesh/modify-zones/zone-name inlet.1 inlet '
	]

def sec_nth(number, mesh):
	return [
	';====={}====='.format(number + 1), 
	'/mesh/translate 0. 0. 0.005 ',
	'/mesh/modify-zones/append-mesh "../msh/{}.msh" '.format(mesh),
	'/mesh/modify-zones/merge-zones fluid fluid.1 () ',
	'/mesh/modify-zones/merge-zones solid solid.1 () ',
	'/mesh/modify-zones/merge-zones interior interior.1 () ',
	'/mesh/modify-zones/merge-zones interior-fluid interior-fluid.1 () ',
	'/mesh/modify-zones/merge-zones interior-solid interior-solid.1 () ',
	'/mesh/modify-zones/merge-zones wall-fluid wall-fluid.1 () ',
	'/mesh/modify-zones/merge-zones wall-solid wall-solid.1 () ',
	'/mesh/modify-zones/merge-zones wall-fluid-solid wall-fluid-solid.1 () ',
	'/mesh/modify-zones/fuse-face-zones inlet outlet.1 () delete-me ',
	'/mesh/modify-zones/merge-zones interior delete-me () ',
	'/mesh/modify-zones/zone-name inlet.1 inlet '
	]

def sec_last(mesh):
	return [
	'/mesh/translate 0. 0. 0.1 ',
	'/mesh/modify-zones/append-mesh "../msh/{}.msh" '.format(mesh),
	'/mesh/modify-zones/merge-zones fluid fluid.1 ()',
	'/mesh/modify-zones/merge-zones interior interior.1 () ',
	'/mesh/modify-zones/merge-zones interior-fluid interior-fluid.1 ()',
	'/mesh/modify-zones/zone-name wall-solid.1 wall-outlet',
	'/mesh/modify-zones/merge-zones wall-out wall-outlet () ',
	'/mesh/modify-zones/fuse-face-zones inlet outlet.1 () delete-me ',
	'/mesh/modify-zones/merge-zones interior delete-me () ',
	'/mesh/modify-zones/zone-name inlet.1 inlet '
	]

def bcr():
	return [
	'/define/boundary-conditions/velocity-inlet inlet no no yes yes no 14.607 no 0 no 300. no no no yes 5. 0.01 ',
	'/define/boundary-conditions/pressure-outlet outlet yes no 0. no 300. no yes no no n yes 5. 0.01 yes no no no ',
	'/define/boundary-conditions/wall wall-fluid 0. no 0. no y temperature no 1000 no no no no no 0. no 0.5 no 1 ',
	'/define/boundary-conditions/wall wall-solid 0. no 0. no yes temperature no 1000 no no 1 ',
	'/define/boundary-conditions/wall wall-out 0. no 0. no yes temperature no 1000 no no no no no 0. no 0.5 no 1 ',
	'/file/write-case "../cas/bld.cas" y '
	]

def bcf():
	return [
	'/define/boundary-conditions/velocity-inlet inlet no no yes yes no 14.607 no 0 no 300. no no no yes 5. 0.01 ',
	'/define/boundary-conditions/pressure-outlet outlet yes no 0. no 300. no yes no no n yes 5. 0.01 yes no no no ',
	'/define/boundary-conditions/wall wall 0. no 0. no y temperature no 1000 no no no no no 0. no 0.5 no 1 ',
	'/define/boundary-conditions/wall wall-out 0. no 0. no yes temperature no 1000 no no no no no 0. no 0.5 no 1 ',
	'/file/write-case "../cas/bld.cas" y '
	]

def solver():
	return [
	'file/read-journal "cmd.jou"'
	]

def to_txt(path, journal):
	with open(path, 'w') as f:
		for item in journal:
			f.write("%s\n" % item)

# =========================================

# n = 100
# mesh_stab = 'STAB-100'
# mesh_test = 'TEST-5-050'

# journal = sec_first(mesh_test)

# for i in range(0, n):
# 	journal += sec_nth(i, mesh_test)

# journal = journal + sec_last(mesh_stab) + bcr()
# to_txt('../cls/build.jou', journal)

# =========================================

mesh_stab = 'STAB-100'
mesh_test = 'TEST-0-500'

journal = secs_flat(mesh_test, mesh_stab) + bcf()

to_txt('../cls/build.jou', journal)

# =========================================