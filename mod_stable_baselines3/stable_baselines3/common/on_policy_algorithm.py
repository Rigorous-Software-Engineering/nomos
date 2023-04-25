import time
import pickle
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import numpy as np
import torch as th


from mod_gym import gym

from mod_stable_baselines3.stable_baselines3.common.base_class import BaseAlgorithm
from mod_stable_baselines3.stable_baselines3.common.buffers import DictRolloutBuffer, RolloutBuffer
from mod_stable_baselines3.stable_baselines3.common.callbacks import BaseCallback
from mod_stable_baselines3.stable_baselines3.common.policies import ActorCriticPolicy, BasePolicy
from mod_stable_baselines3.stable_baselines3.common.type_aliases import GymEnv, MaybeCallback, Schedule
from mod_stable_baselines3.stable_baselines3.common.utils import obs_as_tensor, safe_mean
from mod_stable_baselines3.stable_baselines3.common.vec_env import VecEnv


class OnPolicyAlgorithm(BaseAlgorithm):
    """
    The base for On-Policy algorithms (ex: A2C/PPO).

    :param policy: The policy model to use (MlpPolicy, CnnPolicy, ...)
    :param env: The environment to learn from (if registered in Gym, can be str)
    :param learning_rate: The learning rate, it can be a function
        of the current progress remaining (from 1 to 0)
    :param n_steps: The number of steps to run for each environment per update
        (i.e. batch size is n_steps * n_env where n_env is number of environment copies running in parallel)
    :param gamma: Discount factor
    :param gae_lambda: Factor for trade-off of bias vs variance for Generalized Advantage Estimator.
        Equivalent to classic advantage when set to 1.
    :param ent_coef: Entropy coefficient for the loss calculation
    :param vf_coef: Value function coefficient for the loss calculation
    :param max_grad_norm: The maximum value for the gradient clipping
    :param use_sde: Whether to use generalized State Dependent Exploration (gSDE)
        instead of action noise exploration (default: False)
    :param sde_sample_freq: Sample a new noise matrix every n steps when using gSDE
        Default: -1 (only sample at the beginning of the rollout)
    :param policy_base: The base policy used by this method
    :param tensorboard_log: the log location for tensorboard (if None, no logging)
    :param create_eval_env: Whether to create a second environment that will be
        used for evaluating the agent periodically. (Only available when passing string for the environment)
    :param monitor_wrapper: When creating an environment, whether to wrap it
        or not in a Monitor wrapper.
    :param policy_kwargs: additional arguments to be passed to the policy on creation
    :param verbose: the verbosity level: 0 no output, 1 info, 2 debug
    :param seed: Seed for the pseudo random generators
    :param device: Device (cpu, cuda, ...) on which the code should be run.
        Setting it to auto, the code will be run on the GPU if possible.
    :param _init_setup_model: Whether or not to build the network at the creation of the instance
    :param supported_action_spaces: The action spaces supported by the algorithm.
    """

    def __init__(
        self,
        policy: Union[str, Type[ActorCriticPolicy]],
        env: Union[GymEnv, str],
        learning_rate: Union[float, Schedule],
        n_steps: int,
        gamma: float,
        gae_lambda: float,
        ent_coef: float,
        vf_coef: float,
        max_grad_norm: float,
        use_sde: bool,
        sde_sample_freq: int,
        policy_base: Type[BasePolicy] = ActorCriticPolicy,
        tensorboard_log: Optional[str] = None,
        create_eval_env: bool = False,
        monitor_wrapper: bool = True,
        policy_kwargs: Optional[Dict[str, Any]] = None,
        verbose: int = 0,
        seed: Optional[int] = None,
        device: Union[th.device, str] = "auto",
        _init_setup_model: bool = True,
        supported_action_spaces: Optional[Tuple[gym.spaces.Space, ...]] = None,
    ):

        super(OnPolicyAlgorithm, self).__init__(
            policy=policy,
            env=env,
            policy_base=policy_base,
            learning_rate=learning_rate,
            policy_kwargs=policy_kwargs,
            verbose=verbose,
            device=device,
            use_sde=use_sde,
            sde_sample_freq=sde_sample_freq,
            create_eval_env=create_eval_env,
            support_multi_env=True,
            seed=seed,
            tensorboard_log=tensorboard_log,
            supported_action_spaces=supported_action_spaces,
        )

        self.n_steps = n_steps
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.ent_coef = ent_coef
        self.vf_coef = vf_coef
        self.max_grad_norm = max_grad_norm
        self.rollout_buffer = None

        self.best_bugs = float('inf')
        self.best_rew_of_bb  = float('-inf')

        if _init_setup_model:
            self._setup_model()

    def _setup_model(self) -> None:
        self._setup_lr_schedule()
        self.set_random_seed(self.seed)

        buffer_cls = DictRolloutBuffer if isinstance(self.observation_space, gym.spaces.Dict) else RolloutBuffer

        self.rollout_buffer = buffer_cls(
            self.n_steps,
            self.observation_space,
            self.action_space,
            self.device,
            gamma=self.gamma,
            gae_lambda=self.gae_lambda,
            n_envs=self.n_envs,
        )
        self.policy = self.policy_class(  # pytype:disable=not-instantiable
            self.observation_space,
            self.action_space,
            self.lr_schedule,
            use_sde=self.use_sde,
            **self.policy_kwargs  # pytype:disable=not-instantiable
        )
        self.policy = self.policy.to(self.device)

    def collect_rollouts(
        self,
        env: VecEnv,
        callback: BaseCallback,
        rollout_buffer: RolloutBuffer,
        n_rollout_steps: int,
    ) -> bool:
        """
        Collect experiences using the current policy and fill a ``RolloutBuffer``.
        The term rollout here refers to the model-free notion and should not
        be used with the concept of rollout used in model-based RL or planning.

        :param env: The training environment
        :param callback: Callback that will be called at each step
            (and at the beginning and end of the rollout)
        :param rollout_buffer: Buffer to fill with rollouts
        :param n_steps: Number of experiences to collect per environment
        :return: True if function returned with at least `n_rollout_steps`
            collected, False if callback terminated rollout prematurely.
        """
        assert self._last_obs is not None, "No previous observation was provided"
        n_steps = 0
        rollout_buffer.reset()
        # Sample new weights for the state dependent exploration
        if self.use_sde:
            self.policy.reset_noise(env.num_envs)

        callback.on_rollout_start()

        while n_steps < n_rollout_steps:
            if self.use_sde and self.sde_sample_freq > 0 and n_steps % self.sde_sample_freq == 0:
                # Sample a new noise matrix
                self.policy.reset_noise(env.num_envs)

            with th.no_grad():
                # Convert to pytorch tensor or to TensorDict
                obs_tensor = obs_as_tensor(self._last_obs, self.device)
                actions, values, log_probs = self.policy.forward(obs_tensor)
            actions = actions.cpu().numpy()

            # Rescale and perform action
            clipped_actions = actions
            # Clip the actions to avoid out of bound error
            if isinstance(self.action_space, gym.spaces.Box):
                clipped_actions = np.clip(actions, self.action_space.low, self.action_space.high)

            new_obs, rewards, dones, infos = env.step(clipped_actions)

            self.num_timesteps += env.num_envs

            # Give access to local variables
            callback.update_locals(locals())
            if callback.on_step() is False:
                return False

            self._update_info_buffer(infos)
            n_steps += 1

            if isinstance(self.action_space, gym.spaces.Discrete):
                # Reshape in case of discrete action
                actions = actions.reshape(-1, 1)
            rollout_buffer.add(self._last_obs, actions, rewards, self._last_episode_starts, values, log_probs)
            self._last_obs = new_obs
            self._last_episode_starts = dones

        with th.no_grad():
            # Compute value for the last timestep
            obs_tensor = obs_as_tensor(new_obs, self.device)
            _, values, _ = self.policy.forward(obs_tensor)

        rollout_buffer.compute_returns_and_advantage(last_values=values, dones=dones)

        callback.on_rollout_end()

        return True

    def train(self) -> None:
        """
        Consume current rollout data and update policy parameters.
        Implemented by individual algorithms.
        """
        raise NotImplementedError

    def learn(
        self,
        total_timesteps: int,
        callback: MaybeCallback = None,
        log_interval: int = 1,
        eval_env: Optional[GymEnv] = None,
        eval_freq: int = -1,
        n_eval_episodes: int = 5,
        tb_log_name: str = "OnPolicyAlgorithm",
        eval_log_path: Optional[str] = None,
        reset_num_timesteps: bool = True,
    ) -> "OnPolicyAlgorithm":
        iteration = 0

        total_timesteps, callback = self._setup_learn(
            total_timesteps, eval_env, callback, eval_freq, n_eval_episodes, eval_log_path, reset_num_timesteps, tb_log_name
        )

        self.setup_test()
        
        callback.on_training_start(locals(), globals())

        while self.num_timesteps < total_timesteps:

            continue_training = self.collect_rollouts(self.env, callback, self.rollout_buffer, n_rollout_steps=self.n_steps)

            if continue_training is False:
                break

            iteration += 1
            self._update_current_progress_remaining(self.num_timesteps, total_timesteps)

            # Display training infos
            if log_interval is not None and iteration % log_interval == 0:
                fps = int(self.num_timesteps / (time.time() - self.start_time))
                self.logger.record("time/iterations", iteration, exclude="tensorboard")
                if len(self.ep_info_buffer) > 0 and len(self.ep_info_buffer[0]) > 0:
                    self.logger.record("rollout/ep_rew_mean", safe_mean([ep_info["r"] for ep_info in self.ep_info_buffer]))
                    self.logger.record("rollout/ep_len_mean", safe_mean([ep_info["l"] for ep_info in self.ep_info_buffer]))
                self.logger.record("time/fps", fps)
                self.logger.record("time/time_elapsed", int(time.time() - self.start_time), exclude="tensorboard")
                self.logger.record("time/total_timesteps", self.num_timesteps, exclude="tensorboard")
                self.logger.dump(step=self.num_timesteps)

            self.train()
            
            # if self.num_timesteps > self.guide_point and self.num_timesteps % (2048 * 50) == 0:
            #     curseed = self.num_timesteps
            #     self.test(curseed, self.test_budget, update_guide=True)
            
            if not self.train_type == "normal" and self.num_timesteps % (2048 * 50) == 0:
                self.env.guide_prob = min(self.env.guide_prob+0.15, 0.6)
                # fw = open(self.log_dir + "/bug_rew_RS%d.log" % self.seed, "a")
                fw = open(self.log_dir + "/info.log", "a")
                fw.write("Guide probability increased to %f.\n" % self.env.guide_prob)
                fw.close()

            if self.num_timesteps % (2048 * 5) == 0:
                self.test()

        callback.on_training_end()

        return self

    def _get_torch_save_params(self) -> Tuple[List[str], List[str]]:
        state_dicts = ["policy", "policy.optimizer"]

        return state_dicts, []


    def setup_test(self):
        from lunar import Mutator, EnvWrapper
        
        game = EnvWrapper.Wrapper("lunar")
        game.env = self.env
        game.model = self.policy
        self.game = game 

        mutator = Mutator.LunarOracleMoonHeightMutator(game)
        rng = np.random.default_rng(self.seed)

        poolfile= open("lunar/state_pool.p", 'rb')
        pool = pickle.load(poolfile)
        self.pool = rng.choice(pool, self.explr_budget)
        self.testsuite = defaultdict(list)
        for idx, org_state in enumerate(self.pool):
            org_state = org_state.hi_lvl_state
            for _ in range(self.mut_budget):
                rlx_state = mutator.mutate(org_state, rng, 'relax')
                self.testsuite[idx].append(rlx_state)


    def test(self):
        info_f = open(self.log_dir + "/info.log", "a")
        data_f = open(self.log_dir + "/bug_rew_%s_RS%d.log" % (self.train_type, self.seed), "a")

        # cur_all_b_size = len(self.env.all_guiding_states)
        self.env.locked = True
        self.env.guiding_states.clear()
        num_bugs = 0
        for org_idx, rlx_list in self.testsuite.items():
            org = self.pool[org_idx]
            for rlx in rlx_list:
                org_llvl = self.env.reset(org.hi_lvl_state)
                o_org = self.game.play(org_llvl)
                rlx_llvl = self.env.reset(rlx)
                o_rlx = self.game.play(rlx_llvl)

                if o_org <= o_rlx: continue

                org_llvl = self.env.reset(org.hi_lvl_state)
                o_org = self.game.play(org_llvl)
                rlx_llvl = self.env.reset(rlx)
                o_rlx = self.game.play(rlx_llvl)

                if o_org > o_rlx:
                    self.env.guiding_states.append((org, rlx))
                    if org_idx not in self.env.all_guiding_st_idx:
                        self.env.all_guiding_states.append((org, rlx))
                        self.env.all_guiding_st_idx.append(org_idx)
                    num_bugs += 1
        
        # if len(self.env.all_guiding_states) > cur_all_b_size:
        #     cur_all_b_size = len(self.env.all_guiding_states) 
        #     fw.write("Number of states found to be buggy so far is %d out of %d.\n" % (cur_all_b_size, self.explr_budget * self.mut_budget))

        self.game.env.seed(self.seed)
        avg_rew = self.game.eval(eval_budget=30)
        self.env.last_avg_rew = avg_rew
        alpha1, alpha2 = 10, 5
        utility1 = alpha1 * (self.explr_budget * self.mut_budget - num_bugs) + avg_rew
        utility2 = alpha2 * (self.explr_budget * self.mut_budget - num_bugs) + avg_rew

        data_f.write("%d,%d,%f,%f,%f\n" % (self.num_timesteps, num_bugs, avg_rew, utility1, utility2))

        # if cur_utility > self.utility:
        #     self.utility = cur_utility 
        #     fw.write("Better agent found with %d bugs and %f reward at %d timesteps.\n" % (num_bugs, avg_rew, self.num_timesteps))
        
        info_f.write("Current agent has %d bugs and %f reward at %d timesteps.\n" % (num_bugs, avg_rew, self.num_timesteps))

        info_f.close()
        data_f.close()
        
        self.env.locked = False

        # if num_bugs < self.best_bugs:
        #     self.best_bugs = num_bugs
        #     self.game.env.seed(self.seed)
        #     avg_rew = self.game.eval(eval_budget=30)

        #     fw.write("Better agent found with %d bugs and %f reward at %d timesteps.\n" % (num_bugs, avg_rew, self.num_timesteps))

        #     self.best_rew_of_bb = avg_rew
        # elif num_bugs == self.best_bugs:
        #     self.game.env.seed(self.seed)
        #     avg_rew = self.game.eval(eval_budget=30)

        #     if avg_rew > self.best_rew_of_bb:
        #         fw.write("Better agent found with %d bugs and %f reward at %d timesteps.\n" % (num_bugs, avg_rew, self.num_timesteps))

        #         self.best_rew_of_bb = avg_rew



    def explore(self):
        from lunar import Fuzzer, EnvWrapper

        game = EnvWrapper.Wrapper("lunar")
        game.env = self.env
        game.model = self.policy
        game.action_space = range(self.env.action_space.n)

        rand_seed = self.seed  # separate rng created in Fuzzer
        fuzz_type = 'inc'
        fuzz_game = game
        inf_prob  = 0.2
        coverage  = 'raw'
        coverage_thold = 0.4
        fuzz_mut_bdgt  = 25

        fuzzer = Fuzzer.Fuzzer(rand_seed=rand_seed, fuzz_type=fuzz_type, fuzz_game=fuzz_game, inf_prob=inf_prob, coverage=coverage, coverage_thold=coverage_thold, mut_budget=fuzz_mut_bdgt)
       
        poolfile= open("fuzzer_pool_1h_guide_train.p", 'rb')
        pool = pickle.load(poolfile)
        fuzzer.pool = pool
        poolfile.close()

        self.fuzzer = fuzzer
        #self.fuzzer.fuzz()
        #print("Pool size: %d" % len(self.fuzzer.pool))

        #fuzzer_summary = open("fuzzer_pool_1h_guide_train.p", "wb")
        #pickle.dump(self.fuzzer.pool, fuzzer_summary)

    def old_test(self):

        poolfile= open("fuzzer_pool_1h_guide_train.p", 'rb')
        pool = pickle.load(poolfile)
        
        from lunar import Mutator, EnvWrapper
        game = EnvWrapper.Wrapper("lunar")
        game.env = self.env
        game.model = self.policy

        mutator = Mutator.LunarOracleMoonHeightMutator(game)
        rng = np.random.default_rng(self.seed)

        confirmation_budget = 5

        test_budget = self.test_budget
        self.env.guiding_states.clear()

        fw = open("mylog_%d" % self.seed, "w")
        num_bugs = 0
        all_org, all_rlx = 0, 0
        while test_budget > 0:
            org_state = rng.choice(pool)
            org_state = org_state.hi_lvl_state
            rlx_state = mutator.mutate(org_state, rng, 'relax')

            o_org, o_rlx = 0, 0
            
            # dummy_vec_env reset is modified
            for _ in range(confirmation_budget):
                org_llvl_state = self.env.reset(org_state)
                o_org += game.rollout(org_llvl_state)

            # dummy_vec_env reset is modified
            for _ in range(confirmation_budget):
                rlx_llvl_state = self.env.reset(rlx_state)
                o_rlx += game.rollout(rlx_llvl_state)

            if o_org > o_rlx:
                # guided states declared in DummyVecEnv class where step (step_wait) is implemented
                self.env.guiding_states.append((org_state, rlx_state))
                print("BUG FOUND! O_ORG:%d, O_RLX:%d" % (o_org, o_rlx))
                #fw.write("BUG FOUND! O_ORG:%d, O_RLX:%d\n" % (o_org, o_rlx))

                all_org += o_org
                all_rlx += o_rlx

                num_bugs += 1

            if test_budget % 500 == 0:
                print("Remaining test budget: ", int(test_budget))
            
            test_budget -= 1

        fw.write("Total win org: %d, Total win rlx: %d\n" % (all_org, all_rlx))
        fw.write("%d bugs found.\n\n" % num_bugs)

        test_out = open("train_lunar/bug_states_GP%d_GPR%f_RS%d_TB%d_1H_fuzz.p" % (self.guide_point, self.env.guide_prob, self.seed, self.test_budget), "wb")
        pickle.dump(self.env.guiding_states, test_out)
