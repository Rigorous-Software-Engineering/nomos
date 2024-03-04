import sys
import copy
import random

from tqdm.auto import tqdm
from bipedal.helper import bipedal
bipedal = bipedal()

rseed = int(sys.argv[1])
bipedal.setSeed(rseed)
print('Seed set to: ' + str(rseed))

model_path = sys.argv[2]
bipedal.load(model_path)
print('Test set size: ' + str(len(bipedal.inputs)))

budget = int(sys.argv[3])
bipedal.budget = budget
pbar = tqdm(desc='test loop', total=budget)
while budget > 0:
	try:
		s1 = bipedal.randState()
		s2 = bipedal.unrelax(s1)
		o1, o2 = 0, 0
		for _ in range(10):
			rs = bipedal.randInt(0, 2**32-1)
			o1 += bipedal.play(s1, rs)
			o2 += bipedal.play(s2, rs)

		if o2 <= o1 :
			bipedal.passed += 1
		else:
			bipedal.postcond_violtn += 1
			bipedal.process_bug()
		bipedal.cur_rand = ()
		budget -= 1
		pbar.update(1)
	except:
		bipedal.exceptions += 1
		bipedal.cur_rand = ()

print('Test budget: ' + str(bipedal.budget))
print('Assertion violation: ' + str(bipedal.precond_violtn))
print('Succeeding tests: ' + str(bipedal.passed))
print('Bug inputs: ' + str(len(bipedal.bug_inps)))
print('Number of exceptions: ' + str(bipedal.exceptions))
print('Number of duplicate bugs:' + str(bipedal.num_dupl_bugs))