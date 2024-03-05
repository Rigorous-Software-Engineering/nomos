import pickle
import random
import numpy as np
from bipedal import EnvWrapper as EW
from bipedal import Mutator

import numpy as np

class bipedal():
    def __init__(self) -> None:
        self.budget = 0
        self.passed = 0
        self.exceptions = 0
        self.num_dupl_bugs   = 0
        self.precond_violtn  = 0
        self.postcond_violtn = 0

        self.bug_inps = set()
        self.cur_rand = ()
        self.rand_dict = {}

    def setSeed(self, seed):
        random.seed(seed)

    def load(self, model_path):
        r = random.randint(0, 2**32-1)

        self.game = EW.Wrapper("bipedal")
        self.game.create_environment(env_seed=r)
        self.game.create_model(model_path, r)

        poolf = open("bipedal/state_pool.p", "rb")
        pool = pickle.load(poolf)
        self.inputs = pool[1]

        self.mutator = Mutator.BipedalEasyOracleMutator(self.game)

    # create the dataset (pool of states) statically and pick random state
    def randState(self):
        r = random.randint(0, len(self.inputs))
        self.cur_rand += r,
        state_seed = self.inputs[r]

        return state_seed.hi_lvl_state

    def randInt(self, l, u):
        r = random.randint(l, u)
        self.cur_rand += r,
        return r

    def relax(self, state):
        r = random.randint(0, 2**32-1)
        self.cur_rand += r,
        rng = np.random.default_rng(r)
        mut_state = self.mutator.mutate(state, rng, mode='relax')

        return mut_state

    def unrelax(self, state):
        r = random.randint(0, 2**32-1)
        self.cur_rand += r,
        rng = np.random.default_rng(r)
        mut_state = self.mutator.mutate(state, rng, mode='unrelax')

        return mut_state

    def play(self, state, rand_seed):
        self.game.env.seed(rand_seed)
        self.game.set_state(state, None)
        llvl_state, _, _ = self.game.get_state()
        outcome = self.game.play(llvl_state)

        return outcome

    def process_bug(self):
        if self.cur_rand and self.cur_rand in self.rand_dict:
            self.num_dupl_bugs += 1
        else:
            self.rand_dict[self.cur_rand] = True

        self.bug_inps.add(self.cur_rand[0])


