import feedparser


feeds = {
    'ard': 'http://www.tagesschau.de/xml/rss2',
    'zdf': 'http://www.heute.de/?view=rss',
    'spon': 'http://www.spiegel.de/schlagzeilen/index.rss',
    'sz': 'http://suche.sueddeutsche.de/rss/Topthemen',
    'zeit': 'http://newsfeed.zeit.de/index',
    'welt': 'http://www.welt.de/?config=feeds_startseite',
    'taz': 'http://taz.de/rss.xml'
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

    return titles
