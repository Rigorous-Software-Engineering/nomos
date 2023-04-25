import sys
import pickle
import numpy as np

from mod_gym import gym
from lunar import Mutator, EnvWrapper
from mod_stable_baselines3.stable_baselines3 import PPO, MyPPO
from mod_stable_baselines3.stable_baselines3.common.evaluation import evaluate_policy
from mod_stable_baselines3.stable_baselines3.common.monitor import Monitor

def normal_test(path):
    game = EnvWrapper.Wrapper("lunar")
    game.create_environment(123)
    game.create_model(path + "/model.zip")

    rew = game.test()

    print(rew)


def eval_test():
    model_dir = "train_lunar_guide/"
    model_name = "lunar_250000_steps"

    #env = gym.make('BipedalWalker-v3')
    env = gym.make('LunarLander-v2')
    env.seed(123)

    # Load the trained agent
    model = PPO.load(model_dir + model_name, env=env)

    # Evaluate the agent
    #mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=100)
    #print(mean_reward, std_reward)


def bug_test(path):
    game = EnvWrapper.Wrapper("lunar")
    game.create_environment()
    game.create_model(path + "/model.zip")

    poolfile= open("fuzzer_pool_1h_guide_train.p", 'rb')
    pool = pickle.load(poolfile)

    seed = 42
    test_budget = 40000

    mutator = Mutator.LunarOracleMoonHeightMutator(game)
    rng = np.random.default_rng(seed)

    confirmation_budget = 10

    bug_states = []
    while test_budget > 0:
        org_state = rng.choice(pool)
        org_state = org_state.hi_lvl_state
        rlx_state = mutator.mutate(org_state, rng, 'relax')

        o_org, o_rlx = 0, 0
        
        # dummy_vec_env reset is modified
        for _ in range(confirmation_budget):
            org_llvl_state = game.set_state(org_state)
            o_org += game.rollout(org_llvl_state)

        # dummy_vec_env reset is modified
        for _ in range(confirmation_budget):
            rlx_llvl_state = game.set_state(rlx_state)
            o_rlx += game.rollout(rlx_llvl_state)

        if o_org > o_rlx:
            bug_states.append((org_state, rlx_state))
            print("BUG FOUND!", len(bug_states))
        
        if test_budget % 100 == 0:
            print("Remaining test budget: ", int(test_budget))

        test_budget -= 1
    
    test_out = open(path + "/bug_states_TB%d_RS%d.p" % (test_budget, seed), "wb")
    pickle.dump(bug_states, test_out)


path = sys.argv[1]


#bug_test(path)

normal_test(path)

