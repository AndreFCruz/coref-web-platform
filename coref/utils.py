import sys, os, io
import numpy as np
import warnings
import pickle
from keras.models import load_model
import tensorflow as tf


def split_train_dataset(X_list, Y, test_ratio = 0.2):
    """
    Randomly splits the given dataset in train/test datasets according to the given ratio.
    [X_train, Y_train], [X_test, Y_test] = split_train_dataset(X, Y)
    """
    assert(len(X_list) > 0)

    num_samples = len(Y)
    shuffled_indices = np.random.permutation(num_samples)
    cut_point_idx = int(num_samples * (1 - test_ratio))
    train_indices, test_indices = shuffled_indices[:cut_point_idx], shuffled_indices[cut_point_idx:]

    X_train, X_test, Y_train, Y_test = [], [], [], []
    for feature_array in X_list:
        X_train.append(feature_array[train_indices])
        X_test.append(feature_array[test_indices])

    Y_train, Y_test = Y[train_indices], Y[test_indices]
    return [X_train, Y_train], [X_test, Y_test]


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc


def find_in_sequence(predicate, seq):
    """
    Returns the index of the first element that matches the given condition, or -1 if none found.
    """
    idx = 0
    for elem in seq:
        if predicate(elem):
            return idx
        idx += 1
    return -1


def bin_scalar(dist, bins):
    for i in range(0, len(bins) - 1):
        if bins[i] <= dist < bins[i+1]:
            return i
    raise RuntimeWarning("Coudln't bin scalar '{}'.".format(dist))


def load_tokenizer(path):
    with open(path, 'rb') as f:
        tokenizer = pickle.load(f)
    return tokenizer


class MemCache(object):
    """
    Keeps an index/cache of the used tokenizers and models,
     preventing repeated loads.
    """

    def __init__(self, data_path):
        self.data_path = data_path
        self.tokenizers = dict()
        self.models = dict()
        self.model_graphs = dict()

    def get_tokenizer(self, key):
        if key not in self.tokenizers:
            self.tokenizers[key] = load_tokenizer(self.data_path + '/tokenizer.{}.pkl'.format(key))
        return self.tokenizers[key]

    def get_model(self, key):
        if key not in self.models:
            model = load_model(self.data_path + '/models/{}.h5'.format(key))
            model._make_predict_function()  # Initialize predict function in sync environment
            self.models[key] = model
            self.model_graphs[key] = tf.get_default_graph()
        return self.models[key]

    def predict(self, model_key, X):
        """
        See Keras' issue #2397.
        https://github.com/keras-team/keras/issues/2397
        """
        with self.model_graphs[model_key].as_default():
            return self.models[model_key].predict(X)


class Logger(object):
    def __init__(self, path):
        self.file = open(path, 'w')
        self.stdout = sys.stdout
        sys.stdout = self
    def __del__(self):
        self.close()
    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
    def flush(self):
        self.file.flush()
    def close(self):
        sys.stdout = self.stdout
        self.file.close()