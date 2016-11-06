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
headlines of several RSS newsfeeds of German newspaper websites. Then, it randomly selects two headlines and mixes them.
The mixing is done as follows: At first, [Part-of-Speech (POS) tagging](https://en.wikipedia.org/wiki/Part-of-speech_tagging)
is applied to the headlines in order to find out the nouns in the headlines. For accurate results, I use a
trained tagger for German language text like explained in
[this blog post](https://datascience.blog.wzb.eu/2016/07/13/accurate-part-of-speech-tagging-of-german-texts-with-nltk/).
The tagger is a trained using Philipp Nolte's
[ClassifierBasedGermanTagger](https://github.com/ptnplanet/NLTK-Contributions/tree/master/ClassifierBasedGermanTagger)
with the
[TIGER corpus from the University of Stuttgart](http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/download/start.html).
After POS tagging, a random number of nouns from one headline is selected and replaced with some nouns from the other
headline so that we get our mixed headline. If we are below the Twitter character limit, we have our final headline,
otherwise the whole process starts all over. Finally, the random headline is posted to the twitter account using
[tweepy](http://www.tweepy.org/).


## Requirements

The script has been tested with Python 2.7.

The following Python packages need to be installed -- all are available via PyPI:

* tweepy
* feedparser
* nltk

**NLTK needs additional data for the tokenizer. You should execute `nltk.download('punkt')` for that.**

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

N_MAX_TRIES = 10
```