import copy
import numpy as np
from abc import ABC

class Mutator(ABC):
    def __init__(self, wrapper):
        self.wrapper = wrapper

class BipedalEasyOracleMutator(Mutator):
    def __init__(self, wrapper):
        super().__init__(wrapper)

    def mutate(self, state, rng, mode="relax"):
        VIEWPORT_H = 400
        SCALE = 30.0
        TERRAIN_STEP   = 14/SCALE
        TERRAIN_LENGTH = 200     # in steps
        TERRAIN_HEIGHT = VIEWPORT_H/SCALE/4
        TERRAIN_STARTPAD = 20    # in steps
        y = TERRAIN_HEIGHT
        velocity = 0.0

        if mode == "relax":
            vel_coeff = 0.7
            rough_coeff = 1
        else:
            vel_coeff = 0.9
            rough_coeff = 1

        hull_x = state[0][0]
        minx, maxx = hull_x, hull_x
        for legpos in state[4]:
            if legpos[0] < minx: minx = legpos[0]
            if legpos[0] > maxx: maxx = legpos[0]
        minx -= 3
        maxx += 3
        
        org_terrain_y = state[-2]

        mut_terrain_y = []
        for i in range(TERRAIN_LENGTH):
            x = i*TERRAIN_STEP
            if x > minx and x < maxx:
                mut_terrain_y.append(org_terrain_y[i])
            else:
                velocity = vel_coeff*velocity + 0.01*np.sign(TERRAIN_HEIGHT - y)
                if i > TERRAIN_STARTPAD: velocity += rng.uniform(-rough_coeff, rough_coeff)/SCALE   #1
                y += velocity
                mut_terrain_y.append(y)

        hi_lvl_state = copy.deepcopy(state)
        if len(hi_lvl_state) == 17:
            hi_lvl_state[-5] = mut_terrain_y
        elif len(hi_lvl_state) == 14:
            hi_lvl_state[-2] = mut_terrain_y


        return hi_lvl_state

