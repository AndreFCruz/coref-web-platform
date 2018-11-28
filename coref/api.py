"""
API for coreference resolution services to be exposed by the web server.
"""

import numpy as np
from .semeval import Document, Mention, MentionPair, Token
from .data import process_mention_pairs_to_distance_features, process_mention_pairs_to_indices
from .clustering import cluster_by_closest_antecedent
from .utils import MemCache
import os

DATA_PATH = os.getenv('DATA_PATH', '../data')
POLYGLOT_DATA_PATH = os.getenv('POLYGLOT_DATA_PATH', DATA_PATH)
os.environ['POLYGLOT_DATA_PATH'] = POLYGLOT_DATA_PATH

from polyglot.downloader import Downloader
from polyglot.text import Text

def _download_polyglot_data():
    downloader = Downloader()

    # Download PT and ES embeddings for mention detection
    downloader.download('embeddings2.pt')
    downloader.download('embeddings2.es')

    # Download NER models
    downloader.download('ner2.pt')
    downloader.download('ner2.es')


cached_models = MemCache(DATA_PATH)
def set_up():
    # Download data for NER with polyglot
    _download_polyglot_data()

    # Load tokenizers to memory
    print('Loading tokenizers...')
    _, _ = cached_models.get_tokenizer('pt'), cached_models.get_tokenizer('es')

    # Load models to memory
    print('Loading models...')
    _, _, _ = cached_models.get_model('pt'), cached_models.get_model('es'), cached_models.get_model('pt-transferred')


def automatic_mention_detection(text, hint_language_code):
    """
    Returns a Document object whose mentions automatically detected.
    """
    doc = Document('user-defined-document')

    text_obj = Text(text, hint_language_code=hint_language_code)
    for sentence_idx, sentence in enumerate(text_obj.sentences):
        for token_idx, token in enumerate(sentence.tokens):
            t = Token([token_idx, token.string], sentence_idx)
            doc.add_token(t)

    for mention in text_obj.entities:
        toks = doc.tokens[mention.start: mention.end]
        doc.mentions.append(Mention(toks))

    return doc


def parse_manual_mentions(text):
    """
    Returns a Document object whose mentions were manually separated
     with a given character.
    """
    def get_mention_tokens(start_idx, tokens):
        mention_tokens = list()
        nested_mentions = 1
        tokens[start_idx].num_mention_starts -= 1
        print('Searching mention starting at {}: {}'.format(start_idx, tokens[start_idx].get_string()))
        for i in range(start_idx, len(tokens)):
            print('Token {}. Starts: {}. Ends: {}.'.format(tokens[i].get_string(), tokens[i].num_mention_starts, tokens[i].num_mention_ends))
            nested_mentions += tokens[i].num_mention_starts
            if tokens[i].num_mention_ends > 0:
                nested_mentions -= tokens[i].num_mention_ends
                if nested_mentions <= 0:
                    tokens[i].num_mention_ends -= 1
                    return tokens[start_idx: i+1]

        raise RuntimeWarning("Didn't find match for token at index {}: '{}'".format(start_idx, tokens[start_idx].get_string()))

    doc = Document('user-defined-document')

    text_obj = Text(text)

    # Extract tokens
    for sentence_idx, sentence in enumerate(text_obj.sentences):
        token_count = 0
        next_is_start = 0 # Counts the number of mentions starting at the next token
        for idx, token in enumerate(sentence.tokens):
            print(sentence_idx, token_count, token.string)
            if token.string == '[':
                next_is_start += 1
            elif token.string == ']':
                doc.tokens[-1].num_mention_ends += 1
            else:
                t = Token([token_count, token.string], sentence_idx)
                t.num_mention_starts = next_is_start
                next_is_start = 0

                doc.add_token(t)
                token_count += 1

    # Extract mentions
    for tok_idx, token in enumerate(doc.tokens):
        num_mention_starts = token.num_mention_starts
        for _ in range(num_mention_starts):
            mention_tokens = get_mention_tokens(tok_idx, doc.tokens)
            doc.mentions.append(Mention(mention_tokens))

    return doc


def cluster_mentions(doc, language):
    MAX_MENTION_LEN = 50
    def process_mention_pairs(mps, tokenizer):
        X_m1, X_m2 = process_mention_pairs_to_indices(mps, tokenizer, MAX_MENTION_LEN)
        X_scalar = process_mention_pairs_to_distance_features(mps)
        return [X_m1, X_m2, X_scalar]

    tokenizer = cached_models.get_tokenizer(language)

    mps = doc.generate_mention_pairs()
    X = process_mention_pairs(mps, tokenizer)
    predictions = cached_models.predict(language, X)

    print('\nPredictions:\n')
    for idx, mp in enumerate(mps):
        print('\nMP at index {}\n'.format(idx))
        print('\t{} : {}\n'.format(mp.m1.full_mention, mp.m2.full_mention))
        print('\tPRED: {}\n'.format(predictions[idx]))
        print(X[0][idx], X[1][idx], X[2][idx])
        print('\n')

    clusters = cluster_by_closest_antecedent(doc, predictions)
    
    return clusters