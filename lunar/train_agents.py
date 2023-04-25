import os
import sys
import matplotlib.pyplot as plt
from mod_gym import gym
from mod_stable_baselines3.stable_baselines3 import PPO, MyPPO
from mod_stable_baselines3.stable_baselines3.common import results_plotter
from mod_stable_baselines3.stable_baselines3.common.monitor import Monitor
from mod_stable_baselines3.stable_baselines3.common.evaluation import evaluate_policy
from mod_stable_baselines3.stable_baselines3.common.callbacks import CheckpointCallback
# from stable_baselines3.common.env_util import make_vec_env

time_steps  = int(sys.argv[1])  # int(1e6)
#save_freq   = int(sys.argv[2])
#guide_point = int(sys.argv[2])
#guide_prob  = float(sys.argv[3])
train_type  = sys.argv[2]
device      = int(sys.argv[3])
rand_seed   = int(sys.argv[4])

# if guide_prob <= 0:
log_dir = "train_lunar/TS%d_RS%d_%s_GP0.15/" % (time_steps, rand_seed, train_type)
# else:
#     log_dir = "train_lunar/TS%d_GP%d_GPR%f_RS%d/" % (time_steps, guide_point, guide_prob, rand_seed)

os.makedirs(log_dir, exist_ok=True)

#env = gym.make('BipedalWalker-v3')
env = gym.make('LunarLander-v2')
env = Monitor(env, log_dir)
env.seed(rand_seed)  # deliberately fixed for now

#checkpoint_callback = CheckpointCallback(save_freq=save_freq, save_path=log_dir, name_prefix='lunar')

# Instantiate the agent
# test budget should be proportional to pool size
model = MyPPO('MlpPolicy', env, seed=rand_seed, train_type=train_type, device="cuda:%d" % device, log_dir=log_dir, verbose=1)

model.learn(total_timesteps=time_steps)   # , callback=checkpoint_callback)
model.save(log_dir + "model")

results_plotter.plot_results([log_dir], time_steps, results_plotter.X_TIMESTEPS, "PPO Lunar")
plt.savefig(log_dir + "LunarPPOTraining%d.pdf" % time_steps)

'''
# Load the trained agent
model = PPO.load(log_dir + "model", env=env)

# Evaluate the agent
mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=100)
print(mean_reward, std_reward)
'''
