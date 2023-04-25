import sys
import copy
import random

from tqdm.auto import tqdm
from compas.helper import compas
compas = compas()

rseed = int(sys.argv[1])
compas.setSeed(rseed)
print('Seed set to: ' + str(rseed))

model_path = sys.argv[2]
compas.load(model_path)
print('Test set size: ' + str(len(compas.inputs)))

budget = int(sys.argv[3])
compas.budget = budget
pbar = tqdm(desc='test loop', total=budget)
while budget > 0:
	try:
		x1 = compas.randInput() 
		v1 = compas.getFeat(x1,3)
		v2 = v1 - 1
		v3 = compas.randInt(0,v2)
		x2 = compas.setFeat(x1,3,v3)
		d1 = compas.predict(x1)
		d2 = compas.predict(x2)

		if d2 <= d1 :
			compas.passed += 1
		else:
			compas.postcond_violtn += 1
			compas.process_bug()
		compas.cur_rand = ()
		budget -= 1
		pbar.update(1)
	except:
		compas.exceptions += 1
		compas.cur_rand = ()

print('Test budget: ' + str(compas.budget))
print('Assertion violation: ' + str(compas.precond_violtn))
print('Succeeding tests: ' + str(compas.passed))
print('Bug inputs: ' + str(len(compas.bug_inps)))
print('Number of exceptions: ' + str(compas.exceptions))
print('Number of duplicate bugs:' + str(compas.num_dupl_bugs))