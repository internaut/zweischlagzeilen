# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import random
from math import ceil
from functools import reduce

import libleipzig
from suds import WebFault

import datasources
import tweet
from headline_parser import Headline
from conf import WORD_BLACKLIST, CUT_SUBSTRINGS

SEND_TWEET = True

NUM_WORD_NEIGHBOURS_LOOKUP = 20
MAX_RAND_HEADLINE_GENERATION_RETRIES = 100
MAX_RAND_HEADLINE_OVERALL_RETRIES = 10
MAX_NUM_WEBFAULT_ERR = 5

num_webfault_err = 0
num_rand_headline_retries = 0

headlines = []
headline_parts = []
headline_parts_per_type = {}


def prnt_utf8(s):
    print(s.encode('utf-8'))


def ucfirst(s):
    return s[0].upper() + s[1:]


def rand_item_and_index_from_second_half(seq):
    l = len(seq)
    n = int(ceil(l / 2.0))
    r = random.randint(n, l) - 1

    return seq[r], r


def len_of_headline_parts(*parts):
    return reduce(lambda total, part: total + len(part.part_text_complete), parts, 0)


def len_of_headline_words(words):
    chars_words = reduce(lambda total, w: total + len(w), words, 0)
    return chars_words + len(words) - 1     # num. chars of words + spaces in between


def find_part_with_word(parts, word):
    for p in parts:
        try:
            i = p.words.index(word)
            return p, i
        except ValueError:
            pass
    return None, None


def random_headline_parts():
    global num_webfault_err

    # chose random item from "normal" or "introductory" headline parts ("quote" parts should not
    # be used at the beginning)
    start_parts_pool = headline_parts_per_type['NORMAL'] + headline_parts_per_type['INTRO']
    start_part = random.choice(start_parts_pool)

    prnt_utf8(u"> using start part of type '%s'" % start_part.classif)

    # don't use "introductory" again for 2nd part
    following_parts_pool = headline_parts_per_type['NORMAL'] + headline_parts_per_type['QUOTE']

    num_tries = 0
    second_part = None

    if start_part.classif == 'INTRO':
        while not second_part and num_tries < MAX_RAND_HEADLINE_GENERATION_RETRIES:
            p = random.choice(following_parts_pool)
            prnt_utf8(u"> second part: random choice '%s'" % unicode(p))
            if len_of_headline_parts(start_part, p) <= tweet.MAX_CHARS:
                second_part = p
                print(">> ok")
            else:
                print(">> dismissed")

            num_tries += 1
    elif start_part.classif == 'NORMAL':
        while not second_part and num_tries < MAX_RAND_HEADLINE_GENERATION_RETRIES:
            rand_word, rand_word_idx = rand_item_and_index_from_second_half(start_part.words)
            first_words = start_part.words[:rand_word_idx + 1]
            try:
                prnt_utf8(u"> will lookup neighbours of word '%s' from start part via libleipzig..." % rand_word)
                neighbours = libleipzig.RightNeighbours(rand_word, NUM_WORD_NEIGHBOURS_LOOKUP)
            except WebFault as e:
                print((u'error in libleipzig: %s (%d)' % (str(e), num_webfault_err)).encode('utf-8'), file=sys.stderr)
                num_webfault_err += 1
                if num_webfault_err >= MAX_NUM_WEBFAULT_ERR:
                    return None
                else:
                    break

            for neighbour in neighbours:
                neighbour_words = neighbour.Nachbar.split(' ')
                for neighbour_word in neighbour_words:
                    prnt_utf8(u">> trying neighbourhood word '%s'..." % neighbour_word)
                    p_candidate, candidate_idx = find_part_with_word(following_parts_pool, neighbour_word)

                    if p_candidate and p_candidate != start_part:
                        prnt_utf8(u">>> found matching candidate %s" % unicode(p_candidate))
                        last_words = p_candidate.words[candidate_idx:]

                        # we should have at least 2 additional words and we should not exceed the twitter limit
                        if len(last_words) >= 2 and len_of_headline_words(first_words + last_words) <= tweet.MAX_CHARS:
                            start_part.chosen_word_range = (0, rand_word_idx)
                            second_part = p_candidate
                            second_part.chosen_word_range = (candidate_idx,)
                            print(">>>> ok")
                            break
                        else:
                            print(">>>> dismissed")

                if second_part:
                    break

            num_tries += 1

    return [start_part, second_part] if second_part else None


def main():
    global headlines
    global headline_parts
    global headline_parts_per_type
    global num_rand_headline_retries

    print('authenticating via twitter...')
    tweet.auth()

    print('fetching headlines...')
    raw_headlines = datasources.fetch_titles_from_all_sources()

    print('parsing headlines...')
    for source, headlines_per_source in raw_headlines.items():
        for h_link, h_text in headlines_per_source:
            h_text_lc = h_text.lower()
            if any((w.lower() in h_text_lc for w in WORD_BLACKLIST)):
                prnt_utf8(u"> headline dismissed: '%s'" % h_text)
                continue

            for cut_str in CUT_SUBSTRINGS:
                h_text = h_text.replace(cut_str, '')

            h = Headline(h_text, source, h_link)
            headlines.append(h)
            headline_parts.extend(h.parts)
            for p in h.parts:
                if p.classif not in headline_parts_per_type:
                    headline_parts_per_type[p.classif] = []
                headline_parts_per_type[p.classif].append(p)

    print('generating random headline...')
    rand_headline_parts = None
    while not rand_headline_parts and num_rand_headline_retries < MAX_RAND_HEADLINE_OVERALL_RETRIES:
        rand_headline_parts = random_headline_parts()
        if not rand_headline_parts:
            print('failed to generate a random headline (%d)' % num_rand_headline_retries, file=sys.stderr)
        num_rand_headline_retries += 1

    if rand_headline_parts:
        final_headline = ''
        prev_part_was_intro = False
        for p in rand_headline_parts:
            prnt_utf8(u'>> random headline part object: %s' % unicode(p))
            prnt_utf8(u'>>> taken from original headline: %s' % unicode(p.headline))
            add_part = p.part_text_consider_chosen_word_range
            if prev_part_was_intro:
                add_part = ucfirst(add_part)
            final_headline += add_part
            if final_headline[-1] != ' ':
                final_headline += ' '
            prev_part_was_intro = p.classif == 'INTRO'
        final_headline = ucfirst(final_headline.strip())
        prnt_utf8(u'> final generated headline: %s' % final_headline)

        if SEND_TWEET:
            print('sending tweet...')
            tweet.send(final_headline)
        else:
            print('sending tweet disabled.')
    else:
        print('maximum number of random headline generation retries exceeded' % num_rand_headline_retries,
              file=sys.stderr)

    print('done.')


if __name__ == '__main__':
    main()
