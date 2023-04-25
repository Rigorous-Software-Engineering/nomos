import sys
import copy
import random

from tqdm.auto import tqdm
from speech_command.helper import speech_command
speech_command = speech_command()

rseed = int(sys.argv[1])
speech_command.setSeed(rseed)
print('Seed set to: ' + str(rseed))

model_path = sys.argv[2]
speech_command.load(model_path)
print('Test set size: ' + str(len(speech_command.inputs)))

budget = int(sys.argv[3])
speech_command.budget = budget
pbar = tqdm(desc='test loop', total=budget)
while budget > 0:
	try:
		x1 = speech_command.randInput() 
		x2 = speech_command.wNoise(x1)
		v1 = speech_command.label(x1)
		d1 = speech_command.predict(x1)
		d2 = speech_command.predict(x2)

		if not(d2 == v1) or d1 == v1 :
			speech_command.passed += 1
		else:
			speech_command.postcond_violtn += 1
			speech_command.process_bug()
		speech_command.cur_rand = ()
		budget -= 1
		pbar.update(1)
	except:
		speech_command.exceptions += 1
		speech_command.cur_rand = ()

print('Test budget: ' + str(speech_command.budget))
print('Assertion violation: ' + str(speech_command.precond_violtn))
print('Succeeding tests: ' + str(speech_command.passed))
print('Bug inputs: ' + str(len(speech_command.bug_inps)))
print('Number of exceptions: ' + str(speech_command.exceptions))
print('Number of duplicate bugs:' + str(speech_command.num_dupl_bugs))