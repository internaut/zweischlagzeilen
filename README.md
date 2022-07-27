# zweischlagzeilen Project -- ZwoSchlagzeilen Twitter-Bot

[@ZwoSchlagzeilen](https://twitter.com/ZwoSchlagzeilen) ist ein Twitter-Bot, der Schlagzeilen großer deutscher
Nachrichtenportale verquirlt und stündlich postet. Er generiert im besten Fall so etwas wie
["Fast Richtige Schlagzeilen" (Titanic)](http://www.titanic-magazin.de/newsticker/kategorie/fast-richtige-schlagzeilen/).
Im Grunde genommen ist es die deutsche Variante für das amerikanische Vorbild
[@TwoHeadlines](https://twitter.com/TwoHeadlines).

--

[@ZwoSchlagzeilen](https://twitter.com/ZwoSchlagzeilen) is a Twitter-Bot that mixes recent headlines of leading German
newspapers and posts one of them each hour. Sometimes it produces funny results. It is basically the German variant for
the American archetype [@TwoHeadlines](https://twitter.com/TwoHeadlines).

## How does it work?

The script works quite simple. Basically, it uses *[feedparser](https://pythonhosted.org/feedparser/)* to fetch the
headlines of several RSS newsfeeds of German newspaper websites. Then, it randomly selects one headline as
"seed headline". An [trigram language model] is built from all but the seed headline. The seed headline is cut at a
random point so that only up to the first half of it is used as seed input for generating a random sequence of words
from the trigram model. This sequence of words is the randomly generated headline that is posted to the Twitter account
using [tweepy](http://www.tweepy.org/).


## Requirements

The script has been tested with Python 3.8 to 3.10.

The following Python packages need to be installed -- all are available via PyPI:

* tweepy
* feedparser
* [tmtoolkit](https://tmtoolkit.readthedocs.io/en/latest/)

"conf.py" is not in the repository. You will need to create a file "conf.py" with the following content:

```
TWITTER_CONSUMER_KEY = '...'
TWITTER_CONSUMER_SECRET = '...'
TWITTER_ACCESS_KEY = '...'
TWITTER_ACCESS_SECRET = '...'

# cut out the following substrings from headlines:
CUT_SUBSTRINGS = (
    u'*** BREAKING NEWS ***',
)

# location where to store previously fetched headlines
HEADLINES_COLLECTION = os.path.join('data', 'headlines.json')

# how long to keep headlines
KEEP_DAYS = 28

# which ngram model to use
NGRAMS_N = 3
```