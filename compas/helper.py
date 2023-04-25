import copy
import pickle
import random
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

class compas():
    def __init__(self) -> None:
        self.budget = 0
        self.passed = 0
        self.exceptions = 0
        self.num_dupl_bugs   = 0
        self.precond_violtn  = 0
        self.postcond_violtn = 0

        self.bug_inps = set()
        self.dupl = False
        self.cur_rand = ()
        self.rand_dict = {}
        self.class_map = {0:3, 1:0, 2:1}

    def setSeed(self, seed):
        random.seed(seed)

    def getFeat(self, x, i):
        return x[i]

    def setFeat(self, x, i, val):
        new_x = copy.copy(x)
        new_x[i] = val
        return new_x

    def load(self, model_path):
        # "./compas/compas_model/model"
        if "dt_model" in model_path or "nb_model" in model_path:
            model_file = open(model_path, "rb")
            self.model = pickle.load(model_file)
        else:
            self.model = tf.keras.models.load_model(model_path)

        data = pd.read_csv("./compas/compas-scores.csv", delimiter=",")
        if "rv_model" in model_path:
            data = data[data['decile_score'].notna()]
            labels = np.array(data["decile_score"])
        else:
            data = data[data['score_text'].notna()]
            labels = np.array(data["score_text"])
            enc = OneHotEncoder(categories='auto')
            enc.fit(labels.reshape(-1, 1))
            labels = enc.transform(labels.reshape(-1, 1)).toarray()
        # data = data.drop(["score_text"], axis=1)

        columns_to_drop = [
            "id", "name", "first", "last",
            "compas_screening_date", "dob", "age_cat", "c_offense_date",
            "c_arrest_date", "c_case_number", "c_jail_in", "c_jail_out",
            "r_offense_date", "r_case_number",  "r_jail_in", "r_jail_out",
            "vr_offense_date", "vr_case_number", "v_type_of_assessment",
            "v_screening_date", "v_score_text", "type_of_assessment",
            "decile_score", "decile_score.1", "screening_date",
            "r_charge_desc", "c_charge_desc", "vr_charge_desc", "score_text"
        ]

        for column in columns_to_drop:
            data = data.drop([column], axis=1)

        categorical_columns = [
            "sex", "race", "c_charge_degree",
            "r_charge_degree", "vr_charge_degree"
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

        inputs = np.nan_to_num(inputs)
        self.inputs = list(inputs)
        self.labels = list(labels)
        # Features below:
        # ['age', 'juv_fel_count', 'juv_misd_count', 'juv_other_count', 'priors_count', 'days_b_screening_arrest', 'c_days_from_compas', 'is_recid', 'num_r_cases', 'r_days_from_arrest', 'is_violent_recid', 'num_vr_cases', 'v_decile_score', 'sex_Female', 'sex_Male', 'race_African-American', 'race_Asian', 'race_Caucasian', 'race_Hispanic', 'race_Native American', 'race_Other', 'c_charge_degree_F', 'c_charge_degree_M', 'c_charge_degree_O', 'r_charge_degree_F', 'r_charge_degree_M', 'r_charge_degree_O', 'vr_charge_degree_(F1)', 'vr_charge_degree_(F2)', 'vr_charge_degree_(F3)', 'vr_charge_degree_(F5)', 'vr_charge_degree_(F6)', 'vr_charge_degree_(F7)', 'vr_charge_degree_(M1)', 'vr_charge_degree_(M2)', 'vr_charge_degree_(MO3)']
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

        mapped_d = self.class_map[d]

        return mapped_d

    def process_bug(self):
        if self.cur_rand and self.cur_rand in self.rand_dict:
            self.num_dupl_bugs += 1
        else:
            self.rand_dict[self.cur_rand] = True

        self.bug_inps.add(self.cur_rand[0])
