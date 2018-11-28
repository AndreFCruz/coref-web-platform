import os
import math
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from .semeval import MentionPair, Mention, Document
from .semeval_utils import IdxUtils
from .utils import bin_scalar


def process_mention_pairs_to_output(mention_pairs):
    """
    Processes the given mention pairs into a tensor, Y, with the expected output.
    """
    Y = np.empty(shape=(len(mention_pairs),), dtype='int32')
    for idx in range(len(mention_pairs)):
        Y[idx] = 1 if mention_pairs[idx].is_coreferent else 0

    return Y


def process_mention_pairs_to_distance_features(mention_pairs, num_features=2):
    """
    Processes the given mention pairs into a vector of scalar features (e.g.
     sentence distance, mention distance, one-hot encoded pos tags, ...).
    """
    bins = [0, 1, 2, 3, 4, 5, 8, 16, 32, 64, math.inf] # Following Clark and Manning (2016)
    bin_distance = lambda x: bin_scalar(x, bins)

    num_mention_pairs = len(mention_pairs)

    X_scalar = np.empty(shape=(num_mention_pairs, num_features), dtype='float32')
    for idx, mp in enumerate(mention_pairs):
        features = [bin_distance(mp.sent_dist)]
        if num_features >= 2:
            features.append(bin_distance(mp.token_dist))
        if num_features == 3:
            # features.append(bin_distance(mp.mention_dist))
            pass # TODO distance in mentions ?
        elif num_features > 3:
            raise RuntimeWarning('Invalid number of distance features: {}'.format(num_features))

        X_scalar[idx] = features

    return X_scalar


def process_mention_pairs_to_indices(mention_pairs, tokenizer, max_mention_length=50):
    """
    Processes the given mention pairs into an input dataset, parsing mention tokens
     into their indices in the embedding layer according to the given tokenizer.
    """
    num_mention_pairs = len(mention_pairs)
    X_m1 = np.empty(shape=(num_mention_pairs, max_mention_length), dtype='int32')
    X_m2 = np.empty(shape=(num_mention_pairs, max_mention_length), dtype='int32')

    for idx, mp in enumerate(mention_pairs):
        seq_m1, seq_m2 = tokenizer.texts_to_sequences([mp.m1.full_mention, mp.m2.full_mention])
        X_m1[idx], X_m2[idx] = pad_sequences([seq_m1, seq_m2], maxlen=max_mention_length)

    return X_m1, X_m2
