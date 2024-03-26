import sys
import copy
import random

from tqdm.auto import tqdm
from transpiler.helper import transpiler
transpiler = transpiler()

rseed = int(sys.argv[1])
transpiler.setSeed(rseed)
print('Seed set to: ' + str(rseed))

model_path = sys.argv[2]
transpiler.load(model_path)
budget = int(sys.argv[3])
print('Test budget: ' + str(budget))

transpiler.beam_size = 1
transpiler.temperature = 0.100000
print('Beam size and temperature set to 1 and 0.100000.')

pbar = tqdm(desc='test loop', total=budget)
x1_path = sys.argv[4] 

fr = open(x1_path, 'r')
x1 = str(fr.read())
fr.close()

transpiler.prob_name = x1_path.split('/')[-1].split('.')[0] 
while budget > 0:
	x2 = transpiler.addLoop(x1,"java")
	d1 = transpiler.transpile(x1, "java", "py")
	d2 = transpiler.transpile(x2, "java", "py")

	if not(transpiler.numBranches(d2,"py") == transpiler.numBranches(x2,"java")) or transpiler.numBranches(d1,"py") == transpiler.numBranches(x1,"java") :
		transpiler.passed += 1
	else:
		transpiler.postcond_violtn += 1
		transpiler.process_bug()
	budget -= 1
	pbar.update(1)

transpiler.wrap_up()

print('Precondition violation: ' + str(transpiler.precond_violtn))
print('Postcondition violation: ' + str(transpiler.postcond_violtn))
print('Number of duplicate bugs: ' + str(transpiler.num_dupl_bugs))
print('Bug inputs: ' + str(len(transpiler.bug_inps)))
print('Prediction time: ' + str(transpiler.pred_time))