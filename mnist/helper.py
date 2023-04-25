import cv2 
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.datasets import mnist as mnist_ds

class mnist():
    def __init__(self) -> None:
        self.budget = 0
        self.passed = 0
        self.exceptions = 0
        self.num_dupl_bugs   = 0
        self.precond_violtn  = 0
        self.postcond_violtn = 0
        self.label_dict      = {}

        self.bug_inps = set()
        self.cur_rand = ()
        self.rand_dict = {}

    def setSeed(self, seed):
        random.seed(seed)
    
    def load(self, model_path):
        self.model = tf.keras.models.load_model(model_path)

        (_, _), (X_test, y_test) = mnist_ds.load_data()

        X_test = X_test.astype('float32')
        X_test /= 255

        X_test = np.expand_dims(X_test, axis=1)

        y_test = to_categorical(y_test, num_classes=10)

        self.inputs = X_test
        self.labels = y_test
    
    def randInput(self):
        r = random.randint(0, len(self.inputs)-1)
        self.cur_rand += r,
        inp, lbl = self.inputs[r], self.labels[r]
        inp = np.expand_dims(inp, axis=0)
        self.label_dict[str(inp)] = lbl
        return inp

    def randInt(self, l, u):
        r = random.randint(l, u)
        self.cur_rand += r,
        return r

    def label(self, x):
        lbl = self.label_dict[str(x)]
        lbl = np.argmax(lbl)
        return lbl

    def blur(self, inp, kernel=3):
        kernel_ = (kernel, kernel)
        blurred_inp = cv2.blur(inp[0], kernel_)
        blurred_inp = np.expand_dims(blurred_inp, axis=0)
        return blurred_inp

    def predict(self, x):
        try:
            d = self.model.predict(x)
        except:
            d = self.model.predict(x[0])

        d = np.argmax(d, axis=1)[0]
        return d
    
    def process_bug(self):
        if self.cur_rand and self.cur_rand in self.rand_dict:
            self.num_dupl_bugs += 1
        else:
            self.rand_dict[self.cur_rand] = True

        self.bug_inps.add(self.cur_rand[0])
