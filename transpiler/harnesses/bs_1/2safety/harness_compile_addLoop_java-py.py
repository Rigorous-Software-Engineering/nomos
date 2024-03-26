import sys
import copy
import time
import random

from tqdm.auto import tqdm
from transpiler.helper import transpiler
transpiler = transpiler()

rseed = int(sys.argv[1])
transpiler.setSeed(rseed)
print('Seed set to: ' + str(rseed))

model_path = sys.argv[2]
transpiler.load(model_path)
print('Test set size: ' + str(len(transpiler.inputs)))

budget = int(sys.argv[3])
print('Test budget: ' + str(budget))

transpiler.beam_size = 1
print('Beam size set to 1')

pbar = tqdm(desc='test loop', total=budget)
stime = time.time()
while budget > 0:
	x1 = transpiler.randInput() 
	x2 = transpiler.addLoop(x1,"java")
	d1 = transpiler.transpile(x1, "java", "py")
	d2 = transpiler.transpile(x2, "java", "py")

	if transpiler.compiles(d1,"py") == transpiler.compiles(d2,"py") :
		transpiler.passed += 1
	else:
		transpiler.postcond_violtn += 1
		transpiler.process_bug()
	budget -= 1
	pbar.update(1)

transpiler.wrap_up()
etime = time.time()

print('Precondition violation: ' + str(transpiler.precond_violtn))
print('Postcondition violation: ' + str(transpiler.postcond_violtn))
print('Number of duplicate bugs: ' + str(transpiler.num_dupl_bugs))
print('Bug inputs: ' + str(len(transpiler.bug_inps)))
print('Prediction time: ' + str(transpiler.pred_time))
print('Total time: ', etime-stime)