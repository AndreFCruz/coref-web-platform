"""
clustering_utils.py: utilitary functions for the clustering.py module.
"""

import numpy as np
from enum import IntEnum
from .utils import find_in_sequence


class Link(IntEnum):
    """
    Represents state of coreferring links.
    Must be negative integers to not interfere with the clustering process.
    """
    NO_ANTECEDENT   = -1
    PROCESSED       = -2


def cluster_labels_to_entity_clusters(cluster_labels):
    """
    @cluster_labels is the second return from the affinity_matrix computation,
     and cluster_labels[mention_idx] = mention's cluster
    """
    clusters = dict()
    for idx, label in enumerate(cluster_labels):
        if label not in clusters:
            clusters[label] = list()
        clusters[label].append(idx)

    return [clusters[key] for key in clusters.keys()]


def coreference_links_to_entity_clusters(links):
    """
    Transforms the given array of coreference links into a set of entities (mention clusters).
    Each entity/cluster is represented by the mentions' indices.
    """
    clusters = []
    for i in range(len(links) - 1, -1, -1):
        new_cluster = set()
        j = i

        while True:
            antecedent = links[j]
            links[j] = Link.PROCESSED
            new_cluster.add(j)

            # end of coreference link
            if antecedent == Link.NO_ANTECEDENT:
                clusters.append(new_cluster)
                break
            # linking to previously processed cluster
            elif antecedent == Link.PROCESSED:
                previous_cluster_idx = find_in_sequence(lambda s: j in s, clusters)
                clusters[previous_cluster_idx].update(new_cluster)
                break

            j = antecedent

    return clusters
    

def generate_affinity_matrix(document, mention_pair_predictions):
    """
    Generates an affinity/similarity matrix from the given mention-pair scores.
    @returns affinity_matrix[m1_idx, m2_idx] = affinity_score
    """
    num_mentions = len(document.mentions)
    affinity_matrix = np.ndarray(shape=(num_mentions, num_mentions), dtype=np.float32)
    affinity_matrix.fill(0)

    for idx in range(len(mention_pair_predictions)):
        i1, i2 = document.pairwise_combinations[idx]
        affinity_matrix[i1,i2] = mention_pair_predictions[idx]
        affinity_matrix[i2,i1] = mention_pair_predictions[idx]

    return affinity_matrix
