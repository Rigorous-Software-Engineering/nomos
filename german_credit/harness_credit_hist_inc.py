import sys
import copy
import random

from tqdm.auto import tqdm
from german_credit.helper import german_credit
german_credit = german_credit()

rseed = int(sys.argv[1])
german_credit.setSeed(rseed)
print('Seed set to: ' + str(rseed))

model_path = sys.argv[2]
german_credit.load(model_path)
print('Test set size: ' + str(len(german_credit.inputs)))

budget = int(sys.argv[3])
german_credit.budget = budget
pbar = tqdm(desc='test loop', total=budget)
while budget > 0:
	try:
		x1 = german_credit.randInput() 
		v1 = german_credit.getFeat(x1,-1)
		v2 = v1 + 1
		v3 = german_credit.randInt(v2,5)
		x2 = german_credit.setFeat(x1,-1,v3)
		d1 = german_credit.predict(x1)
		d2 = german_credit.predict(x2)

		if d1 <= d2 :
			german_credit.passed += 1
		else:
			german_credit.postcond_violtn += 1
			german_credit.process_bug()
		german_credit.cur_rand = ()
		budget -= 1
		pbar.update(1)
	except:
		german_credit.exceptions += 1
		german_credit.cur_rand = ()

print('Test budget: ' + str(german_credit.budget))
print('Assertion violation: ' + str(german_credit.precond_violtn))
print('Succeeding tests: ' + str(german_credit.passed))
print('Bug inputs: ' + str(len(german_credit.bug_inps)))
print('Number of exceptions: ' + str(german_credit.exceptions))
print('Number of duplicate bugs:' + str(german_credit.num_dupl_bugs))