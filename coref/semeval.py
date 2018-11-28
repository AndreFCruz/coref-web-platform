import io
import numpy as np
from sklearn.utils.extmath import cartesian
from random import random
from .semeval_utils import MentionUtils, IdxUtils, PoSTags


class Document:
    """
    Class representing a SemEval-style Document.
    """
    document_count = 0

    def __init__(self, name, tokens = None):
        self.name = name
        self.tokens = list() if tokens is None else tokens
        self.mentions = list()  # list of mentions, in order of appearance
        self.sentences = dict()

        self.id = Document.document_count
        Document.document_count += 1

        self._closed = False

    def get_text(self):
        return ' '.join([tok[IdxUtils.TOKEN] for tok in self.tokens])

    def add_token(self, token):
        self.tokens.append(token)
        token.set_document(self)

        if token.sentence_idx not in self.sentences:
            self.sentences[token.sentence_idx] = list()
        self.sentences[token.sentence_idx].append(token)

    def generate_mention_pairs(self):
        return self.generate_mps_all_antecedents()

    def generate_mps_all_antecedents(self):
        self.mention_pairs = []

        num_mentions = len(self.mentions)
        self.pairwise_combinations = [
           [i1, i2] for i1, i2 in cartesian(((range(num_mentions), range(num_mentions)))) if i1 < i2
        ]
        # NOTE # i1 < i2 condition ensures different mentions and breaks symmetric pairs

        for i1, i2 in self.pairwise_combinations:
            assert i1 != i2, "mention-pair must have different mentions"

            m1, m2 = self.mentions[i1], self.mentions[i2]
            self.mention_pairs.append(MentionPair(m1, m2))

        return self.mention_pairs


class Token:
    """
    Class representing a SemEval2010 Token.
    """

    def __init__(self, features, sentence_idx):
        self.features = features
        self.sentence_idx = sentence_idx

        self.num_mention_starts = 0   # The number of mentions that start at this Token
        self.num_mention_ends = 0     # The number of mentions that end at this Token

        self.classified_corefs = {} # automatically classified corefs

        self.document = None
        self.pos_tag = None
        self.morph_features = None

    def __getitem__(self, idx):
        return self.features[idx]

    def __len__(self):
        return len(self.features)

    def key(self):
        """
        Used for comparing tokens' chronological orders.
        If t1.key() < t2.key() then t1 appears before t2.
        """
        return self.sentence_idx * (10 ** 6) + self.get_id()

    def get_string(self):
        return self[IdxUtils.TOKEN]

    def get_id(self):
        return int(self[IdxUtils.ID])

    def set_document(self, document):
        self.document = document

    def add_classified_coref(self, entity_id, coref_type):
        """
        Adds the given classified coreference link to this token.
        Uses sets for the edge case in which two mentions start/end on the
         same token and refer to the same entity.
        """
        if entity_id not in self.classified_corefs:
            self.classified_corefs[entity_id] = list()
        self.classified_corefs[entity_id].append(coref_type)


class Mention:
    """
    A class representing a Mention in a document.
    May comprise several word tokens.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.sentence_idx = tokens[0].sentence_idx

        self.full_mention = ' '.join([tok[IdxUtils.TOKEN] for tok in self.tokens])
        self.document = tokens[0].document

        # assert all tokens in the same document
        assert (len(set([tok.document.id for tok in tokens])) == 1),\
                "mention's tokens belong to different documents"


class MentionPair:
    """
    A class representing a coreferring mention-pair, and its features.
    """

    def __init__(self, m1, m2):
        self.m1 = m1
        self.m2 = m2

        self.document_id = m1.document.id

        assert (m1.document.id == m2.document.id),\
                "mentions in mention-pair belong to different documents"

        self.sent_dist = abs(m2.sentence_idx - m1.sentence_idx)
        self.token_dist = token_distance_between_tokens(m1.tokens[0], m2.tokens[0])


def token_distance_between_tokens(t1, t2):
    """
    Distance in tokens between the two given tokens.
    """
    assert t1.document.id == t2.document.id
    # If t1 comes after t2, flip variables
    if t1.key() > t2.key():
        temp = t1
        t1 = t2
        t2 = temp

    assert t1.sentence_idx <= t2.sentence_idx,\
            "wrong order for tokens, t1 should appear before t2"

    document = t1.document
    distance = 0
    for i in range(t1.sentence_idx, t2.sentence_idx + 1):
        distance += len(document.sentences[i])
        if i == t1.sentence_idx:
            distance -= t1.get_id()
        if i == t2.sentence_idx:
            distance -= len(document.sentences[i]) - t2.get_id()

    return distance
