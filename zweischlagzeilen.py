import random
import sys

import datasources
import tweet
from tmtoolkit.corpus import Corpus, doc_labels_sample, doc_tokens

from ngrammodels import NGramModel, SPECIAL_TOKENS
from conf import CUT_SUBSTRINGS, NGRAMS_N

TWEET_MAX_CHARS = 140


#%%


def preproc(s):
    for cut_str in CUT_SUBSTRINGS:
        s = s.replace(cut_str, '')
    return s.strip()


def token_seq_to_str(tok, nlp):
    s = ''

    for t in tok:
        if t not in SPECIAL_TOKENS:
            lex = nlp.vocab[t]
            if not lex.is_space:
                if lex.is_punct:
                    s += lex.text
                else:
                    s += ' ' + lex.text

    return s.strip()


#%%

simulate = len(sys.argv) > 1 and (sys.argv[1] == 'simulate' or sys.argv[1].startswith('--'))

if not simulate:
    print('authenticating via twitter...')
    tweet.auth()
else:
    print('simulating. will not authenticate via twitter')


#%%

print('fetching headlines...')
headlines = datasources.collect()

#%%

corp = Corpus({link: preproc(item['title']) for link, item in headlines.items()}, language='de')
print(f'created corpus: {corp}')

# select a random document that will provide the "seed text" (first part of headline)

random_doc = next(iter(doc_labels_sample(corp, 1)))
seed_tokens = doc_tokens(corp, select=random_doc, tokens_as_hashes=True)

print(f'selected random document {random_doc} with text:')
print(token_seq_to_str(seed_tokens, corp.nlp))

last_token_ind = round(len(seed_tokens) * 0.75)

if last_token_ind < NGRAMS_N:
    # seed is too short; in this case a headline is generated "from scratch"
    seed_tokens = None
    print('no seed text')
else:
    # make a seed text: randomly cut the list of tokens up to half the number of tokens
    slice_until = random.randint(NGRAMS_N-1, last_token_ind)
    seed_tokens = seed_tokens[:slice_until]
    print(f'seed text: {token_seq_to_str(seed_tokens, corp.nlp)}')

# now remove randomly selected document so that the NGramModel will be trained without it
del corp[random_doc]

#%%

print(f'building {NGRAMS_N}-gram model')
ngmodel = NGramModel(NGRAMS_N)
ngmodel.fit(corp)

print('generating token sequence')
generated_tokens = ngmodel.generate_sequence(seed_tokens)

if seed_tokens:
    generated_text = token_seq_to_str(seed_tokens + list(generated_tokens), corp.nlp)
else:
    generated_text = token_seq_to_str(generated_tokens, corp.nlp)

#%%

# truncate tweet if necessary; could be done in a better way

if len(generated_text) > TWEET_MAX_CHARS:
    generated_text = generated_text[:-3] + '...'

#%%


if simulate:
    print('simulating. would send tweet:')
else:
    print('sending tweet:')
    tweet.send(generated_text)

print(generated_text)

print('\ndone.')
