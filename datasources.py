import feedparser


feeds = {
    'ard': 'http://www.tagesschau.de/xml/rss2',
    'zdf': 'http://www.heute.de/?view=rss',
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
    return [(e['link'], e['title']) for e in feed['entries']
            if 'link' in e and e['link'] and 'title' in e and e['title']]


def fetch_titles_from_all_sources():
    titles = {}
    for feed_id in feeds:
        # print(feed_id)
        titles[feed_id] = fetch_titles(feed_id)
        print('> %s: %d entries' % (feed_id, len(titles[feed_id])))

    return titles
