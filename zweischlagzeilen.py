# -*- coding: utf-8 -*-

from __future__ import print_function
from pprint import pprint
import random
import sys
from copy import deepcopy

import pickle
import nltk
from ClassifierBasedGermanTagger import ClassifierBasedGermanTagger

import datasources
import tweet
from conf import N_MAX_TRIES, CUT_SUBSTRINGS

TWEET_MAX_CHARS = 140
NO_SPACES_TOKENS = (':', "''", '?', '!', ',')
NO_SPACES_PREV_TOKENS = ("``", )


def prnt_utf8(s):
    print(s.encode('utf-8'))


def get_random_headline(headlines_per_src):
    """Return a random headline from a pool of headlines. Return the link, the headline text and the tokens"""
    provider = random.choice([k for k, v in headlines_per_src.items() if len(v) > 0])
    link, text = random.choice(headlines_per_src[provider])
    for cut_str in CUT_SUBSTRINGS:
        text = text.replace(cut_str, '').strip()
    tokens = nltk.tokenize.word_tokenize(text)
    return link, text, tokens


def indices_of_nouns(tokens):
    """Return indices of tokens that are nouns"""
    return [i for i, (_, pos) in enumerate(tokens) if pos.startswith('N')]


def mix(tok_a, tok_b):
    """Mix two lists of tokens"""
    if random.randint(0, 1) == 1:    # interchange randomly
        tmp = tok_a
        tok_a = tok_b
        tok_b = tmp

    # get the nouns list
    indices_nouns_a = indices_of_nouns(tok_a)
    n_nouns_a = len(indices_nouns_a)
    indices_nouns_b = indices_of_nouns(tok_b)
    n_nouns_b = len(indices_nouns_b)

    n_nouns_common = min(n_nouns_a, n_nouns_b)

    if n_nouns_common == 0:
        return None

    n_replace = random.randint(1, n_nouns_common)
    replace_indices_a = random.sample(indices_nouns_a, n_replace)   # sample w/o replacement
    replace_indices_b = random.sample(indices_nouns_b, n_replace)   # sample w/o replacement
    # now mix the tokens -> some nouns from a to b
    print(u'tok_a', tok_a)
    print(u'tok_b', tok_b)
    for a_idx, b_idx in zip(replace_indices_a, replace_indices_b):
        tok_b[b_idx] = tok_a[a_idx]

    # merge the tokens again to get a sentence
    res = u''
    prev_w = None
    for i, (w, pos )in enumerate(tok_b):
        delim = u'' if w in NO_SPACES_TOKENS or prev_w in NO_SPACES_PREV_TOKENS or i == 0 else u' '
        res += delim + w
        prev_w = w

    return res

# nltk.download('punkt')
simulate = len(sys.argv) > 1 and sys.argv[1] == 'simulate'

if not simulate:
    print('authenticating via twitter...')
    tweet.auth()
else:
    print('simulating. will not authenticate via twitter')

print('loading NLTK POS Tagger...')
with open('nltk_german_classifier_data.pickle', 'rb') as f:
    tagger = pickle.load(f)

print('fetching headlines...')
headlines_per_src = datasources.fetch_titles_from_all_sources()

n_tries = 1
while n_tries <= N_MAX_TRIES:
    print('generating random headline (try: %d)' % n_tries)
    _, h1_text, h1_tokens = get_random_headline(headlines_per_src)
    _, h2_text, h2_tokens = get_random_headline(headlines_per_src)

    h1_tagged = tagger.tag(h1_tokens)
    h2_tagged = tagger.tag(h2_tokens)

    headline = mix(deepcopy(h1_tagged), deepcopy(h2_tagged))

    if headline and len(headline) <= TWEET_MAX_CHARS:
        print('headline:')
        prnt_utf8(headline)
        print('h1:')
        prnt_utf8(h1_text)
        #pprint(h1_tagged)
        print('h2:')
        prnt_utf8(h2_text)
        #pprint(h2_tagged)
        break

    n_tries += 1
else:
    print('no headline could be generated')
    exit()

if simulate:
    print('simulating. would send tweet:')
else:
    print('sending tweet:')
    tweet.send(headline)

prnt_utf8(headline)
