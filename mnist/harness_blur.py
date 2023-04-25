import sys
import copy
import random

from tqdm.auto import tqdm
from mnist.helper import mnist
mnist = mnist()

rseed = int(sys.argv[1])
mnist.setSeed(rseed)
print('Seed set to: ' + str(rseed))

model_path = sys.argv[2]
mnist.load(model_path)
print('Test set size: ' + str(len(mnist.inputs)))

budget = int(sys.argv[3])
mnist.budget = budget
pbar = tqdm(desc='test loop', total=budget)
while budget > 0:
	try:
		x1 = mnist.randInput() 
		x2 = mnist.blur(x1)
		v1 = mnist.label(x1)
		d1 = mnist.predict(x1)
		d2 = mnist.predict(x2)

		if not(d2 == v1) or d1 == v1 :
			mnist.passed += 1
		else:
			mnist.postcond_violtn += 1
			mnist.process_bug()
		mnist.cur_rand = ()
		budget -= 1
		pbar.update(1)
	except:
		mnist.exceptions += 1
		mnist.cur_rand = ()

print('Test budget: ' + str(mnist.budget))
print('Assertion violation: ' + str(mnist.precond_violtn))
print('Succeeding tests: ' + str(mnist.passed))
print('Bug inputs: ' + str(len(mnist.bug_inps)))
print('Number of exceptions: ' + str(mnist.exceptions))
print('Number of duplicate bugs:' + str(mnist.num_dupl_bugs))