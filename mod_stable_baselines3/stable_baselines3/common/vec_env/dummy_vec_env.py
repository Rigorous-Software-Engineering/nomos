from collections import OrderedDict
from copy import deepcopy
from typing import Any, Callable, List, Optional, Sequence, Type, Union

from mod_gym import gym
import numpy as np

from mod_stable_baselines3.stable_baselines3.common.vec_env.base_vec_env import VecEnv, VecEnvIndices, VecEnvObs, VecEnvStepReturn
from mod_stable_baselines3.stable_baselines3.common.vec_env.util import copy_obs_dict, dict_to_obs, obs_space_info


class DummyVecEnv(VecEnv):
    """
    Creates a simple vectorized wrapper for multiple environments, calling each environment in sequence on the current
    Python process. This is useful for computationally simple environment such as ``cartpole-v1``,
    as the overhead of multiprocess or multithread outweighs the environment computation time.
    This can also be used for RL methods that
    require a vectorized environment, but that you want a single environments to train with.

    :param env_fns: a list of functions
        that return environments to vectorize
    """

    def __init__(self, env_fns: List[Callable[[], gym.Env]]):
        self.envs = [fn() for fn in env_fns]
        env = self.envs[0]
        VecEnv.__init__(self, len(env_fns), env.observation_space, env.action_space)
        obs_space = env.observation_space
        self.keys, shapes, dtypes = obs_space_info(obs_space)

        self.buf_obs = OrderedDict([(k, np.zeros((self.num_envs,) + tuple(shapes[k]), dtype=dtypes[k])) for k in self.keys])
        self.buf_dones = np.zeros((self.num_envs,), dtype=bool)
        self.buf_rews = np.zeros((self.num_envs,), dtype=np.float32)
        self.buf_infos = [{} for _ in range(self.num_envs)]
        self.actions = None
        self.metadata = env.metadata
        self.guide_prob = 0  # updated
        self.guiding_states = list()  # filled in on_policy_algorithm.py
        self.all_guiding_states = list()  # filled in on_policy_algorithm.py
        self.all_guiding_st_idx = list()
        self.rng = None  # initialized in on_policy_algorithm.py
        self.locked = False
        self.last_avg_rew = 0

    def step_async(self, actions: np.ndarray) -> None:
        self.actions = actions

    def step_wait(self) -> VecEnvStepReturn:
        for env_idx in range(self.num_envs):
            obs, self.buf_rews[env_idx], self.buf_dones[env_idx], self.buf_infos[env_idx] = self.envs[env_idx].step(
                self.actions[env_idx]
            )
            if self.buf_dones[env_idx]:
                # save final observation where user can get it, then reset
                self.buf_infos[env_idx]["terminal_observation"] = obs
                
                # wait until guiding states filled
                if not self.locked and self.rng.random() < self.guide_prob and self.last_avg_rew > 0:  # guide_prob set in myppo. it is set to 0 for normal training
                    if self.guiding_states:
                        guide_s_idx = self.rng.choice(range(len(self.guiding_states)))
                        _, rlx_state = self.guiding_states.pop(guide_s_idx)
                        obs = self.envs[env_idx].reset(rlx_state)
                    elif self.all_guiding_states and self.rng.random() < self.guide_prob:
                        _, rlx_state = self.rng.choice(self.all_guiding_states)
                        obs = self.envs[env_idx].reset(rlx_state)
                    else:
                        obs = self.envs[env_idx].reset()
                else:
                    obs = self.envs[env_idx].reset()


            self._save_obs(env_idx, obs)
        return (self._obs_from_buf(), np.copy(self.buf_rews), np.copy(self.buf_dones), deepcopy(self.buf_infos))

    def seed(self, seed: Optional[int] = None) -> List[Union[None, int]]:
        seeds = list()
        for idx, env in enumerate(self.envs):
            seeds.append(env.seed(seed + idx))
        return seeds

    # works with mod_gym lunar and bipedal envs
    def reset(self, state=None) -> VecEnvObs:
        for env_idx in range(self.num_envs):
            obs = self.envs[env_idx].reset(state)
            self._save_obs(env_idx, obs)
        return self._obs_from_buf()

    def get_state(self):
        # should be fine for now as there is only one env in vecenv
        for env_idx in range(self.num_envs):
            nn_state, hi_lvl_state, rand_state = self.envs[env_idx].get_state()

        return nn_state, hi_lvl_state, rand_state

    def close(self) -> None:
        for env in self.envs:
            env.close()

    def get_images(self) -> Sequence[np.ndarray]:
        return [env.render(mode="rgb_array") for env in self.envs]

    def render(self, mode: str = "human") -> Optional[np.ndarray]:
        """
        Gym environment rendering. If there are multiple environments then
        they are tiled together in one image via ``BaseVecEnv.render()``.
        Otherwise (if ``self.num_envs == 1``), we pass the render call directly to the
        underlying environment.

        Therefore, some arguments such as ``mode`` will have values that are valid
        only when ``num_envs == 1``.

        :param mode: The rendering type.
        """
        if self.num_envs == 1:
            return self.envs[0].render(mode=mode)
        else:
            return super().render(mode=mode)

    def _save_obs(self, env_idx: int, obs: VecEnvObs) -> None:
        for key in self.keys:
            if key is None:
                self.buf_obs[key][env_idx] = obs
            else:
                self.buf_obs[key][env_idx] = obs[key]

    def _obs_from_buf(self) -> VecEnvObs:
        return dict_to_obs(self.observation_space, copy_obs_dict(self.buf_obs))

    def get_attr(self, attr_name: str, indices: VecEnvIndices = None) -> List[Any]:
        """Return attribute from vectorized environment (see base class)."""
        target_envs = self._get_target_envs(indices)
        return [getattr(env_i, attr_name) for env_i in target_envs]

    def set_attr(self, attr_name: str, value: Any, indices: VecEnvIndices = None) -> None:
        """Set attribute inside vectorized environments (see base class)."""
        target_envs = self._get_target_envs(indices)
        for env_i in target_envs:
            setattr(env_i, attr_name, value)

    def env_method(self, method_name: str, *method_args, indices: VecEnvIndices = None, **method_kwargs) -> List[Any]:
        """Call instance methods of vectorized environments."""
        target_envs = self._get_target_envs(indices)
        return [getattr(env_i, method_name)(*method_args, **method_kwargs) for env_i in target_envs]

    def env_is_wrapped(self, wrapper_class: Type[gym.Wrapper], indices: VecEnvIndices = None) -> List[bool]:
        """Check if worker environments are wrapped with a given wrapper"""
        target_envs = self._get_target_envs(indices)
        # Import here to avoid a circular import
        from mod_stable_baselines3.stable_baselines3.common import env_util

        return [env_util.is_wrapped(env_i, wrapper_class) for env_i in target_envs]

    def _get_target_envs(self, indices: VecEnvIndices) -> List[gym.Env]:
        indices = self._get_indices(indices)
        return [self.envs[i] for i in indices]
