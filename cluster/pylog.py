import glob

for path in glob.glob('../*out'):
	with open(path, encoding='UTF8') as f:
		log = f.read().splitlines()

matchers = [' solution is converged',' cells marked for refinement, ']
splitlog = [s for s in log if any(xs in s for xs in matchers)]

for line in splitlog:
	print(line)
