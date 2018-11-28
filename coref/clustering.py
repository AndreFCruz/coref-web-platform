import numpy as np
import random
from scipy.stats import geom
from sklearn.cluster import affinity_propagation
from .clustering_utils import *


def cluster_by_affinity_propagation(document, predictions, percentile_preference=99):
    def mention_contains_proper_noun(mention):
        for token in mention.tokens:
            if token.is_proper_noun():
                return True
        return False

    affinity_matrix = generate_affinity_matrix(document, predictions)
    # preference = [1 if mention_contains_proper_noun(mention) else 0.5 for mention in document.mentions]
    preference = [np.percentile(predictions, percentile_preference) for _ in range(len(document.mentions))]

    _, cluster_labels = affinity_propagation(affinity_matrix, preference=preference)
    return cluster_labels_to_entity_clusters(cluster_labels)


def cluster_randomly(document, prob_coref=0.03):
    """
    Randomly creates coreferring links, or selects NO_ANTECEDENT with a given
    probability.
    """
    links = np.ndarray(shape=(len(document.mentions),), dtype=int)
    links.fill(Link.NO_ANTECEDENT)
    for idx in range(1, len(document.mentions)):
        if random.random() < prob_coref:
            links[idx] = random.randint(0, idx - 1)
    return coreference_links_to_entity_clusters(links)


def cluster_randomly_weigthed(document, prob_coref=0.03):
    """
    Randomly creates a coreferring link between a mention, m2, and any preceding
     mention, m1.
    Probability of selecting a closer antecedent is higher, according to a
     geometric distribution
    Probability of selecting an antecedent is prob_coref, else selects
     NO_ANTECEDENT for that given mention.
    @prob_coref defaults to 0.03 which is the approximate percentage of positive
     coreferring links.
    """
    links = np.ndarray(shape=(len(document.mentions),), dtype=int)
    links.fill(Link.NO_ANTECEDENT)
    for idx in range(1, len(document.mentions)):
        if random.random() < prob_coref:
            random_antecedent = idx - geom.rvs(0.3)
            links[idx] = random_antecedent if random_antecedent >= 0 else Link.NO_ANTECEDENT

    return coreference_links_to_entity_clusters(links)


def cluster_all_mentions_separately(document):
    """
    Clusters all mentions as separate clusters, all non-coreferring.
    """
    return [{i} for i in range(len(document.mentions))]


def cluster_by_closest_antecedent(document, predictions, threshold=0.5):
    """
    Clusters the document's mentions by matching each with its closest antecedent.
    @arg document The document containing the mentions.
    @arg predictions Mention-pair predictions.
    @arg threshold The classification threshold, above this value mentions are
     considered coreferent.
    """
    affinity_matrix = generate_affinity_matrix(document, predictions)
    
    print("\n** Cluster by Closest Antecedent **\n")
    print(predictions)
    print(affinity_matrix)

    num_mentions = len(document.mentions)
    links = np.ndarray(shape=(num_mentions,), dtype=int)
    links.fill(Link.NO_ANTECEDENT)
    for current_idx in range(1, num_mentions):
        for antecedent_idx in range(current_idx - 1, -1, -1):
            if affinity_matrix[current_idx, antecedent_idx] > threshold:
                links[current_idx] = antecedent_idx
                break # break from the inner loop

    print(links)
    return coreference_links_to_entity_clusters(links)


def cluster_by_best_antecedent(document, predictions, threshold=0.5):
    """
    Clusters the document's mentions by matching each with its best antecedent
     with a score above the 0.5 threshold.
    @arg predictions Mention-pair predictions.
    @arg threshold The classification threshold, above this value mentions are
     considered coreferent.
    """
    affinity_matrix = generate_affinity_matrix(document, predictions)

    num_mentions = len(document.mentions)
    links = np.ndarray(shape=(num_mentions,), dtype=int)
    links.fill(Link.NO_ANTECEDENT)
    for current_idx in range(1, num_mentions):
        mention_scores = [score if score > threshold else 0 for score in affinity_matrix[current_idx]]
        best_antecedent = np.argmax(mention_scores)
        if best_antecedent < current_idx:
            links[current_idx] = best_antecedent

    return coreference_links_to_entity_clusters(links)
