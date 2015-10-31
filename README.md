# zweischlagzeilen Project -- ZwoSchlagzeilen Twitter-Bot

[@ZwoSchlagzeilen](https://twitter.com/ZwoSchlagzeilen) ist ein Twitter-Bot, der Schlagzeilen großer deutscher Nachrichtenportale verquirlt. Er generiert im besten Fall so etwas wie ["Fast Richtige Schlagzeilen" (Titanic)](http://www.titanic-magazin.de/newsticker/kategorie/fast-richtige-schlagzeilen/). Im Grunde genommen ist es die deutsche Variante für das amerikanische Vorbild [@TwoHeadlines](https://twitter.com/TwoHeadlines).

Der Quellcode ist ein in Python 2 geschriebenes Skript namens "zweischlagzeilen" und kann hier eingesehen werden.

--

[@ZwoSchlagzeilen](https://twitter.com/ZwoSchlagzeilen) is a Twitter-Bot that mixes recent headlines of leading German newspapers. It is basically the German variant for the American archetype [@TwoHeadlines](https://twitter.com/TwoHeadlines).

The source code is a Python 2 script named "zweischlagzeilen" and can be examined here.

## How does it work?

The script was written in two days and is not very sophisticated.

Basically, it uses *[feedparser](https://pythonhosted.org/feedparser/)* to fetch the headlines of several RSS newsfeeds of German newspaper websites. Then it parses them to cut the headlines into "headline parts" which are classified as *introductory* (like *Senator says: ...*, *quote* (*... "I have a dream"*) or *normal* (everything else).

Now a random new headline is constructed. A starting part is chosen randomly from the pool of headline parts. If it is a introductory part, a second part will be chosen randomly from another pool and both will be simply concatenated. If the overall string length does not exceed the Twitter limit of 140 characters, it is taken as the final generated headline. If not, try again.

If we the randomly chosen starting part is a *normal* (i.e. not quote or introductory) headline part, the random headline generation process is a bit more complicated. At first, we choose a random *stop word* from the starting part so that we use only the first *N* words of the starting part. For example we take only "Economy is recovering" ("recovering" is now the stop word) from the full headline part "Economy is recovering slowly from crisis". Then, we use *libleipzig* to get a list of *right neighbors* of our stop word. This list gives us the most significant words that usually occur *after* this word. (Note: *libleipzig* is a Python library to access this and other useful information about German language words from the [extensive "Wortschatz" database of the University of Leipzig](http://wortschatz.uni-leipzig.de/)). Now that we have a list of words that usually appear after our stop word, we search through all other headline parts and look if we find a candidate that might complete our sentence. So if *libleipzig* returns a list like "lost", *"damage"*, "losses", "a", "from", etc., we might find a second headline part that contains the substring "*damage* after car crash". Now we assume we have a match and concatenate these substrings: "Economy is recovering damage after car crash". (Nonsense, but this is what it is about.) If we are below the Twitter character limit, we have our final headline, otherwise the whole thing starts all over.

Finally, the random headline is posted to the twitter account using *[tweepy](http://www.tweepy.org/)*.


## Requirements

This project only runs with Python 2, because _libleipzig_ is not yet available for Python 3.
It has been tested with Python 2.7.

The following Python packages need to be installed -- all are available via PyPI:

* tweepy
* feedparser
* suds
* libleipzig

"conf.py" is not in the repository. You will need to create a file "conf.py" with the following content:

```
TWITTER_CONSUMER_KEY = '...'
TWITTER_CONSUMER_SECRET = '...'
TWITTER_ACCESS_KEY = '...'
TWITTER_ACCESS_SECRET = '...'

# don't use headlines that contain one of the following words:
WORD_BLACKLIST = (
    u'abuse',
    # ...
)

# cut out the following substrings from headlines:
CUT_SUBSTRINGS = (
    u'*** BREAKING NEWS ***',
)
```