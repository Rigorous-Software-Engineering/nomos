import copy
import random
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_text  # needed to laod uSE from hub
import tensorflow_hub as hub
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

class hotel_review():

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
        return x[i]

    def setFeat(self, x, i, val):
        new_x = copy.copy(x)
        new_x[i] = val
        return new_x

    def strConcat(self, x1, x2):
        return x1 + " " + x2

    def load(self, model_path):
        r = random.randint(0, 2**32-1)

        self.USE = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")
        self.model = tf.keras.models.load_model(model_path)
        # self.model = tf.keras.models.load_model('hotel_review/model')
        
        df = pd.read_csv("hotel_review/Hotel_Reviews.csv", parse_dates=['Review_Date'])
        all_positive_reviews = df["Positive_Review"]
        all_negative_reviews = df["Negative_Review"]
        df["review"] = df["Negative_Review"] + df["Positive_Review"]
        # merged_reviews = df["Negative_Review"] + df["Positive_Review"]
        df["review_type"] = df["Reviewer_Score"].apply(
            lambda x: "bad" if x < 7 else "good"
        )
        df = df[["review", "review_type"]]
        good_reviews = df[df.review_type == "good"]
        bad_reviews = df[df.review_type == "bad"]
        good_df = good_reviews.sample(n=len(bad_reviews), random_state=r)
        bad_df = bad_reviews
        review_df = good_df.append(bad_df)

        type_one_hot = OneHotEncoder(sparse=False).fit_transform(
            review_df.review_type.to_numpy().reshape(-1, 1)
        )
        _, test_reviews, _, labels = train_test_split(
            review_df.review,
            type_one_hot,
            test_size=.2,
            random_state=r
        )

        positive_reviews = all_positive_reviews.iloc[list(test_reviews.index)]
        negative_reviews = all_negative_reviews.iloc[list(test_reviews.index)]
        reviews = []  # list(merged_reviews.iloc[list(test_reviews.index)])
        for prew, nrew in zip(positive_reviews, negative_reviews):
            rew_inp = [prew, nrew]
            reviews.append(rew_inp)

        '''
        x = test_reviews.iloc[0]
        emb = self.USE(x)
        x = tf.reshape(emb, [-1]).numpy()
        x = np.array(x)
        print(x.shape)
        x = np.expand_dims(x, axis=0)
        print(x.shape)
        p = self.model.predict(x)
        print(p)
        print("======")
        print(reviews[0][0] + reviews[0][1])
        x = reviews[0][0] + reviews[0][1]
        emb = self.USE(x)
        x = tf.reshape(emb, [-1]).numpy()
        x = np.array(x)
        print(x.shape)
        x = np.expand_dims(x, axis=0)
        print(x.shape)
        p = self.model.predict(x)
        exit()
        '''

        self.inputs = reviews
    
    def randInput(self):
        r = random.randint(0, len(self.inputs)-1)
        self.cur_rand += r,
        inp = self.inputs[r]
        # inp = np.expand_dims(inp, axis=0)
        return inp

    def randInt(self, l, u):
        r = random.randint(l, u)
        self.cur_rand += r,
        return r

    def predict(self, x):
        x = x[0] + x[1]
        emb = self.USE(x)
        emb = tf.reshape(emb, [-1]).numpy()
        emb = np.array(emb)
        emb = np.expand_dims(emb, axis=0)
        d = self.model.predict(emb)
        d = np.argmax(d, axis=1)[0]

        return d
    
    def process_bug(self):
        if self.cur_rand and self.cur_rand in self.rand_dict:
            self.num_dupl_bugs += 1
        else:
            self.rand_dict[self.cur_rand] = True

        self.bug_inps.add(self.cur_rand[0])
