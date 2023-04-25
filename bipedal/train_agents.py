import os
import sys
import matplotlib.pyplot as plt
from mod_gym import gym
from mod_stable_baselines3.stable_baselines3 import MyPPO
from mod_stable_baselines3.stable_baselines3.common import results_plotter
from mod_stable_baselines3.stable_baselines3.common.monitor import Monitor

# import pickle 
# import numpy as np
# poolfile= open("lunar/state_pool.p", 'rb')
# pool = pickle.load(poolfile)[1]
# mindist = np.inf
# for i in range(len(pool)):
#     sd1 = pool[i].data
#     for j in range(i+1, len(pool)):
#         sd2 = pool[j].data
#         dist = np.linalg.norm(np.array(sd1)-np.array(sd2))
#         if dist < mindist: 
#             mindist = dist
#             print(mindist)

#         # if mindist < 2.0: exit()

# exit()

time_steps  = int(sys.argv[1])
train_type  = sys.argv[2]
device      = int(sys.argv[3])
rand_seed   = int(sys.argv[4])
guide_rew   = float(sys.argv[5])
guide_prob_inc = float(sys.argv[6])
guide_prob_thold = float(sys.argv[7])
explr_bdgt  = int(sys.argv[8])

log_dir = "train_bipedal_mix/TS%d_RS%d_%s_GPI%f_GPT%f_EX%d/" % (time_steps, rand_seed, train_type, guide_prob_inc, guide_prob_thold, explr_bdgt)

os.makedirs(log_dir, exist_ok=True)

env = gym.make('BipedalWalker-v3')
env = Monitor(env, log_dir)
env.seed(rand_seed)

# Instantiate the agent
# test budget should be proportional to pool size
# model = MyPPO('MlpPolicy', env, seed=rand_seed, train_type=train_type, device="cuda:%d" % device, log_dir=log_dir, verbose=1)
model = MyPPO('MlpPolicy', env, seed=rand_seed, train_type=train_type, device="cuda:%d" % device, log_dir=log_dir, explr_budget=explr_bdgt, guide_rew=guide_rew, guide_prob_inc=guide_prob_inc, guide_prob_thold=guide_prob_thold, env_iden="bipedal", verbose=1)

model.learn(total_timesteps=time_steps)
model.save(log_dir + "model")
