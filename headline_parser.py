import re


CLASSIFICATIONS = (
    (('INTRODUCTIONAL', 'NORMAL'), ':'),
    (('NORMAL', 'NORMAL'), ','),
    (('NORMAL', 'NORMAL'), '.'),
    (('QUOTE', ), '"')
)


class HeadlinePart:
    def __init__(self, headline, part_text, classif):
        self.headline = headline    # Headline object
        self.part_text = part_text
        self.classif = classif

    def __str__(self):
        return self.part_text


class Headline:
    def __init__(self, headline, source, url):
        self.full = headline
        self.source = source
        self.url = url
        self.parts = []     # HeadlinePart objects

        self._parse(headline)

    def __str__(self):
        return self.full

    def _parse(self, headline):
        for classif, char in CLASSIFICATIONS:
            if classif[0] == 'QUOTE':
                if headline.count(char) == 2:    # must occur exactly twice
                    pttrn = r'(%s[\w\d -.!/]+%s)' % (char, char)
                    m = re.search(pttrn, headline)
                    try:
                        if m:
                            part_text = m.group(1)
                            headline_part = HeadlinePart(self, part_text, classif[0])
                            self.parts.append(headline_part)
                    except IndexError:
                        continue
            else:
                if headline.count(char) == 1:   # must occur exactly once
                    parts = [sub.strip() for sub in headline.split(char)]
                    if len(parts) != 2 or any([len(p) == 0 for p in parts]):
                        continue

                    for i, part_text in enumerate(parts):
                        headline_part = HeadlinePart(self, part_text, classif[i])
                        self.parts.append(headline_part)

                        self._parse(part_text)  # recurse into the headline part
