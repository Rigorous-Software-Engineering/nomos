import sys
import copy
import random

from tqdm.auto import tqdm
from lunar.helper import lunar
lunar = lunar()

rseed = int(sys.argv[1])
lunar.setSeed(rseed)
print('Seed set to: ' + str(rseed))
lunar.load()
print('Test set size: ' + str(len(lunar.inputs)))

budget = int(sys.argv[2])
lunar.budget = budget
pbar = tqdm(desc='test loop', total=budget)
while budget > 0:
	try:
		s1 = lunar.randState()
		s2 = lunar.relax(s1)
		o1, o2 = 0, 0
		for _ in range(10):
			rs = lunar.randInt(0, 2**32-1)
			o1 += lunar.play(s1, rs)
			o2 += lunar.play(s2, rs)

		if o1 <= o2 :
			lunar.passed += 1
		else:
			lunar.postcond_violtn += 1
			lunar.process_bug()
		lunar.cur_rand = ()
		budget -= 1
		pbar.update(1)
	except:
		lunar.exceptions += 1
		lunar.cur_rand = ()

print('Test budget: ' + str(lunar.budget))
print('Assertion violation: ' + str(lunar.precond_violtn))
print('Succeeding tests: ' + str(lunar.passed))
print('Bug inputs: ' + str(len(lunar.bug_inps)))
print('Number of exceptions: ' + str(lunar.exceptions))
print('Number of duplicate bugs:' + str(lunar.num_dupl_bugs))