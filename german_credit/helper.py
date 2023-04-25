import copy
import pickle
import random
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

class german_credit():
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

    def getFeat(self, x, i):
        if i == -1:  # credit history
            for c in range(5):
                if x[c+11] == 1:
                    break
            return c
        elif i == -2:  # empl since
            for c in range(5):
                if x[c+30] == 1:
                    break
            return c
        elif i == -3:  # job
            for c in range(4):
                if x[c+50] == 1:
                    break
            return c
        else:
            return x[i]

    def setFeat(self, x, i, val):
        new_x = copy.copy(x)
        if i == -1:  # credit history
            for c in range(5):
                new_x[c+11] = 0
            new_x[val+11] = 1
        elif i == -2:  # empl since
            for c in range(5):
                new_x[c+30] = 0
            new_x[val+30] = 1
        elif i == -3:
            for c in range(4):
                new_x[c+50] = 0
            new_x[val+50] = 1
        else:
            new_x[i] = val
        return new_x

    def load(self, model_path):
        # self.model = tf.keras.models.load_model('german_credit/german_credit_model/model')
        if "dt_model" in model_path or "nb_model" in model_path:
            model_file = open(model_path, "rb")
            self.model = pickle.load(model_file)
        else:
            self.model = tf.keras.models.load_model(model_path)
        
        data = pd.read_csv('german_credit/german.csv', delimiter=",")

        labels = np.array(data["label"])
        # transform 1s and 2s into 0s and 1s
        labels = labels - 1
        labels = tf.keras.utils.to_categorical(labels)
        data = data.drop(["label"], axis=1)

        categorical_columns = [
            "st_check_acc", "crdt_hist", "purpose",
            "saving_acc", "empl_since", "personal_st",
            "other_debt", "property", "other_instl",
            "housing", "job", "tel", "forgn_worker"
        ]

        for column in categorical_columns:
            y = pd.get_dummies(data[column], prefix=column)
            data = data.drop([column], axis=1)
            data = pd.concat([data, y], axis=1, sort=False)

        inputs = np.array(data)

        # use only test set
        _, inputs, _, labels = train_test_split(    
            inputs, labels, test_size=0.33, random_state=42
        )

        self.inputs = list(inputs)
        self.labels = list(labels)

        return inputs, labels

    def randInput(self):
        r = random.randint(0, len(self.inputs)-1)
        self.cur_rand += r,
        inp = self.inputs[r]

        return inp

    def randInt(self, l, u):
        r = random.randint(l, u)
        self.cur_rand += r,
        return r

    def predict(self, x):
        x = np.expand_dims(x, axis=0)
        d = self.model.predict(x)

        try:
            d = np.argmax(d, axis=1)[0]
        except:
            d = d[0]

        return d

    def process_bug(self):
        if self.cur_rand and self.cur_rand in self.rand_dict:
            self.num_dupl_bugs += 1
        else:
            self.rand_dict[self.cur_rand] = True

        self.bug_inps.add(self.cur_rand[0])
