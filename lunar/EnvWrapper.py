import time

import numpy as np
import sys
# sys.path.append("..")
from mod_gym import gym
# sys.path.append("..")
from mod_stable_baselines3.stable_baselines3 import PPO
from mod_stable_baselines3.stable_baselines3.common.policies import ActorCriticPolicy


class Wrapper():
    def __init__(self, env_identifier):
        self.env_iden = env_identifier
        self.env = None
        self.model = None

    def create_lunar_model(self, load_path, r_seed):
        ppo = PPO(env=self.env, seed=r_seed, policy=ActorCriticPolicy)
        model = ppo.load(load_path, env=self.env, device="cuda:2")
        # model = PPO.load(load_path, env=self.env)
        # PPO.set_random_seed(r_seed)
        self.model = model

    def create_lunar_environment(self, seed):
        env = gym.make('LunarLander-v2')
        env.seed(seed)
        self.env = env
        self.action_space = range(env.action_space.n)  # Discrete(4)

    def create_environment(self, env_seed=None):
        if self.env_iden == "lunar":
            self.create_lunar_environment(env_seed)
        elif self.env_iden == "bipedal":
            self.create_bipedal_environment(env_seed)

    def create_model(self, load_path, r_seed=None):
        if self.env_iden == "lunar":
            self.create_lunar_model(load_path, r_seed)
        elif self.env_iden == "bipedal" or self.env_iden == "bipedal-hc":
            self.create_bipedal_model(load_path, r_seed)

    def get_state(self):
        nn_state, hi_lvl_state, rand_state = self.env.get_state()

        return nn_state, hi_lvl_state, rand_state

    def set_state(self, hi_lvl_state, rand_state):
        return self.env.reset(state=hi_lvl_state, rand_state=rand_state)

    def model_step(self, state, deterministic=True):
        act = None
        if self.env_iden == "lunar" or self.env_iden == "bipedal" or self.env_iden == "bipedal-hc":
            act, _ = self.model.predict(state, deterministic=deterministic)

        return act

    def env_step(self, action):
        reward, next_state, done = None, None, None
        if self.env_iden == "lunar" or self.env_iden == "bipedal"  or self.env_iden == "bipedal-hc":
            next_state, reward, done, info = self.env.step(action)

        return reward, next_state, done

    def play(self, init_state):
        next_state = init_state
        all_rews = []
        while True:            
            act = self.model_step(next_state)

            reward, next_state, done = self.env_step(act)

            all_rews.append(reward)

            if done:
                # walker fell before reaching end, lander crashed
                if -100 in all_rews:
                    outcome = 0 
                # walker reached end, lander didnt crash
                else:
                    outcome = 1
                return outcome

    def eval(self, eval_budget):
        tot_reward = 0
        for _ in range(eval_budget):
            next_state = self.env.reset()
            done = False
            while not done:
                act = self.model_step(next_state)
                reward, next_state, done = self.env_step(act)
                tot_reward += reward

        avg_reward = tot_reward / eval_budget
        return avg_reward
