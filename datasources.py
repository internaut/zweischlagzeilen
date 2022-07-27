import os
import json
from datetime import datetime
from time import mktime
import logging

import feedparser

from conf import HEADLINES_COLLECTION, KEEP_DAYS


logger = logging.getLogger(__name__)


feeds = {
    'ard': 'http://www.tagesschau.de/xml/rss2',
    'zdf': 'https://www.zdf.de/rss/zdf/nachrichten',
    'spon': 'http://www.spiegel.de/schlagzeilen/index.rss',
    'sz': 'http://rss.sueddeutsche.de/app/service/rss/alles/index.rss?output=rss',
    'zeit': 'http://newsfeed.zeit.de/index',
    'welt': 'https://www.welt.de/feeds/latest.rss',
    'taz': 'http://taz.de/rss.xml',
    'bild': 'http://www.bild.de/rss-feeds/rss-16725492,feed=home.bild.html',
    'heise': 'http://www.heise.de/newsticker/heise-atom.xml',
    'tagesspiegel': 'http://www.tagesspiegel.de/contentexport/feed/home',
}


def fetch_titles(feed_id):
    feed_url = feeds[feed_id]
    feed = feedparser.parse(feed_url)
    data = [(e['link'], e['title'], datetime.fromtimestamp(mktime(e['published_parsed'])).isoformat())
            for e in feed['entries']
            if 'link' in e and e['link'] and 'title' in e and e['title']
            and 'published_parsed' in e and e['published_parsed']]

    logger.info('%s feed: fetched %d entries', feed_id, len(data))

    return data


def item_is_uptodate(item):
    return (datetime.now() - datetime.fromisoformat(item['date'])).days <= KEEP_DAYS


def collect():
    if os.path.exists(HEADLINES_COLLECTION):
        with open(HEADLINES_COLLECTION) as f:
            collection = json.load(f)
        logger.info('loaded %d collected items from disk', len(collection))
    else:
        logger.info('collection file does not exist, creating empty collection')
        collection = {}

    new_collection = {}
    for item in collection.values():
        if item_is_uptodate(item):
            new_collection[item['link']] = item

    logger.info('removed %d old items from collection', len(collection) - len(new_collection))
    del collection

    for feed_id in feeds:
        for link, title, date in fetch_titles(feed_id):
            if link not in new_collection:
                item = {
                    'source': feed_id,
                    'date': date,
                    'link': link,
                    'title': title
                }

                if item_is_uptodate(item):
                    new_collection[item['link']] = item

    logger.info('storing collection with %d items to disk', len(new_collection))
    with open(HEADLINES_COLLECTION, 'w') as f:
        json.dump(new_collection, f)

    return new_collection
