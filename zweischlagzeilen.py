import random
import libleipzig

import datasources


def get_random_headline_from_sources(sources):
    src_id = random.choice(sources.keys())
    return src_id, random.choice(sources[src_id])


def main():
    print('fetching headlines...')
    sources = datasources.fetch_titles_from_all_sources()
    rand_headline = get_random_headline_from_sources(sources)
    print(rand_headline)


if __name__ == '__main__':
    main()
