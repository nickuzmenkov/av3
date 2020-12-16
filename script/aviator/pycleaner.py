from glob import glob
import os

for file in [x for x in glob('*') if x not in glob('*.out')]:
	try:
		os.remove(file)
	except:
		continue