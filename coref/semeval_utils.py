from enum import IntEnum, unique

@unique
class MentionUtils(IntEnum):
    START   = 1     # auto()
    END     = 2     # auto()
    START_END = 3   # auto()


class IdxUtils(IntEnum):
    """
    Helper class for SemEval dataset utilities, namely column indices.
    """

    ## Indices for Token Columns
    # Column 0 : word index/identifier
    ID      = 0 # word identifiers in the sentence

    # Columns 1--7: words and morphosyntactic information
    TOKEN   = 1 # word forms
    LEMMA   = 2 # word lemmas (gold standard manual annotation)
    PLEMMA  = 3 # word lemmas predicted by an automatic analyzer
    POS     = 4 # coarse part of speech
    PPOS    = 5 # same as POS but predicted by an automatic analyzer
    FEAT    = 6 # morphological features
    # (part of speech type, number, gender, case, tense, aspect, degree of comparison, etc., separated by the character "|")
    PFEAT   = 7 # same as 7 but predicted by an automatic analyzer

    # Columns 8--11: syntactic dependency tree
    HEAD    = 8 # for each word, the ID of the syntactic head ('0' if the word is the root of the tree)
    PHEAD   = 9 # same as 9 but predicted by an automatic analyzer
    DEPREL  = 10 # dependency relation labels corresponding to the dependencies  described in 9
    PDEPREL = 11 # same as 11 but predicted by an automatic analyzer

    # Columns 12--13
    NE      = 12 # named entities
    PNE     = 13 # same as 13 but predicted by a named entity recognizer

    # Columns 14--15+N+M: semantic role labeling
    PRED    = 14 # predicates are marked and annotated with a semantic class label
    PPRED   = 15 # same as 13 but predicted by an automatic analyzer
    # APREDs: N columns, one for each predicate in 15, containing the semantic roles/dependencies of each particular predicate
    # PAPREDs: M columns, one for each predicate in 16, with the same information as APREDs but predicted with an automatic analyzer

    # Last column: output to be predicted
    COREF   = -1


class PoSTags:
    ## Constants for Token Part of Speech Tags
    ADJECTIVE   = 'a'
    CONJUNCTION = 'c'
    DETERMINER  = 'd'
    PUNCTUATION = 'f'
    INTERJECTION = 'i'
    NOUN        = 'n'
    PRONOUN     = 'p'
    ADVERB      = 'r'
    PREPOSITION = 's'
    VERB        = 'v'
    DATE        = 'w'   # behaves as noun
    NUMBER      = 'z'   # behaves either as a determiner, pronoun, or noun


class Gender:
    masculine   = 'm'
    feminine    = 'f'
    common      = 'c'


class Number:
    singular    = 's'
    plural      = 'p'
    common      = 'c'
