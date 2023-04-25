import sys
import copy
import random

from tqdm.auto import tqdm
from hotel_review.helper import hotel_review
hotel_review = hotel_review()

rseed = int(sys.argv[1])
hotel_review.setSeed(rseed)
print('Seed set to: ' + str(rseed))

model_path = sys.argv[2]
hotel_review.load(model_path)
print('Test set size: ' + str(len(hotel_review.inputs)))

budget = int(sys.argv[3])
hotel_review.budget = budget
pbar = tqdm(desc='test loop', total=budget)
while budget > 0:
	try:
		x1 = hotel_review.randInput() 
		x2 = hotel_review.randInput() 
		v1 = hotel_review.getFeat(x1,0)
		v2 = hotel_review.getFeat(x2,0)
		v3 = hotel_review.strConcat(v1,v2)
		x3 = hotel_review.setFeat(x1,0,v3)
		d1 = hotel_review.predict(x1)
		d3 = hotel_review.predict(x3)

		if d3 <= d1 :
			hotel_review.passed += 1
		else:
			hotel_review.postcond_violtn += 1
			hotel_review.process_bug()
		hotel_review.cur_rand = ()
		budget -= 1
		pbar.update(1)
	except:
		hotel_review.exceptions += 1
		hotel_review.cur_rand = ()

print('Test budget: ' + str(hotel_review.budget))
print('Assertion violation: ' + str(hotel_review.precond_violtn))
print('Succeeding tests: ' + str(hotel_review.passed))
print('Bug inputs: ' + str(len(hotel_review.bug_inps)))
print('Number of exceptions: ' + str(hotel_review.exceptions))
print('Number of duplicate bugs:' + str(hotel_review.num_dupl_bugs))