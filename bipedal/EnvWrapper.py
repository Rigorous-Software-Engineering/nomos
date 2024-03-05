import time
from mod_gym import gym
from mod_stable_baselines3.stable_baselines3 import PPO
from mod_stable_baselines3.stable_baselines3.common.policies import ActorCriticPolicy


class Wrapper():
    def __init__(self, env_identifier):
        self.env_iden = env_identifier
        self.env = None
        self.model = None

    def create_environment(self, env_seed=None):
        env = gym.make('BipedalWalker-v3')
        env.seed(env_seed)
        self.env = env

    def create_model(self, load_path, r_seed=None):
        ppo = PPO(env=self.env, seed=r_seed, policy=ActorCriticPolicy)
        model = ppo.load(load_path, env=self.env, device="cuda:0")
        self.model = model

    def get_state(self):
        nn_state, hi_lvl_state = self.env.get_state()
        return nn_state, hi_lvl_state, None

    def set_state(self, hi_lvl_state, rand_state=None):
        return self.env.reset(hi_lvl_state=hi_lvl_state)

    def model_step(self, state, deterministic=True):
        act, _ = self.model.predict(state, deterministic=deterministic)
        return act

    def env_step(self, action):
        next_state, reward, done, _ = self.env.step(action)

        return reward, next_state, done

    def play(self, init_state):
        next_state = init_state
        all_rews = []
        while True:
            act = self.model_step(next_state)

            reward, next_state, done = self.env_step(act)

            all_rews.append(reward)

            if done:
                # lander crashed
                if -100 in all_rews:
                    outcome = 0
                # lander didn't crash
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
