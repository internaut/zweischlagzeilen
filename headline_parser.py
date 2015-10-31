# -*- coding: utf-8 -*-

import re

CLASSIFICATIONS = (
    (('INTRO', 'NORMAL'), u':'),
    (('NORMAL', 'NORMAL'), u','),
    (('NORMAL', 'NORMAL'), u'.'),
    (('NORMAL', 'NORMAL'), u'!'),
    (('NORMAL', 'NORMAL'), u'?'),
    (('NORMAL', 'NORMAL'), u' - '),
    (('NORMAL', 'NORMAL'), u' – '),
    (('QUOTE',), u'"'),
    (('QUOTE',), (u'„', u'“')),
)


class HeadlinePart(object):
    _split_pttrn = re.compile('\s+')
    _clean_front_pttrn = re.compile('^\W+', re.UNICODE)
    _clean_back_pttrn = re.compile('\W+$', re.UNICODE)

    def __init__(self, headline, part_text, classif, classif_char=None):
        self._part_text = None
        self._words = []
        self.chosen_word_range = None

        self.headline = headline  # Headline object
        self.part_text = part_text
        self.classif = classif
        self.classif_char = classif_char

    def __eq__(self, other):
        return (self.headline == other.headline
                and self.part_text == other.part_text
                and self.classif == other.classif)

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def part_text(self):
        return self._part_text

    @part_text.setter
    def part_text(self, value):
        value = self._clean_front_pttrn.sub('', value)
        value = self._clean_back_pttrn.sub('', value)
        self._part_text = value
        self._words = self._split_pttrn.split(value)

    @property
    def part_text_complete(self):
        if self.classif == 'QUOTE':
            return self.classif_char[0] + self.part_text + self.classif_char[1]
        if self.classif == 'INTRO':
            return self.part_text + self.classif_char + ' '
        return self.part_text

    @property
    def part_text_consider_chosen_word_range(self):
        if self.classif == 'NORMAL':
            return self.joined_words
        else:
            return self.part_text_complete

    @property
    def joined_words(self):
        if not self.chosen_word_range:
            w = self.words
        else:
            w_start = self.chosen_word_range[0]
            if len(self.chosen_word_range) == 1:
                w = self.words[w_start:]
            elif len(self.chosen_word_range) == 2:
                w = self.words[w_start:self.chosen_word_range[1]]
            else:
                w = self.words

        return ' '.join(w)

    @property
    def words(self):
        return self._words

    def __unicode__(self):
        word_range = ','.join((str(i) for i in self.chosen_word_range)) if self.chosen_word_range else 'None'
        return u"classif=%s, part_text='%s', chosen_word_range=%s" \
               % (self.classif, self.part_text, word_range)


class Headline(object):
    def __init__(self, headline, source, url):
        self._full_headline = None
        self._parts = []

        self.source = source
        self.url = url
        self.full_headline = headline

    def __unicode__(self):
        return u"full_headline='%s', source='%s', url='%s'" % (self.full_headline, self.source, self.url)

    @property
    def full_headline(self):
        return self._full_headline

    @full_headline.setter
    def full_headline(self, value):
        self._full_headline = value
        parts = self._parse_headline(value)

        for part in parts:
            b = [added_p != part for added_p in self._parts]

            if all(b):
                self._parts.append(part)

        if not self._parts:  # none of the above classifications worked, so assume that this is a "normal" headline
            headline_part = HeadlinePart(self, value, 'NORMAL')
            self._parts.append(headline_part)

    @property
    def parts(self):
        return self._parts

    def _parse_headline(self, headline, prev_part=None):
        res = []

        for classif, char in CLASSIFICATIONS:
            parts = self._parse_headline_part(headline, classif, char)

            for p in parts:
                if not prev_part or p.part_text_complete != prev_part.part_text_complete:
                    more_parts = self._parse_headline(p.part_text_complete, p)
                else:
                    more_parts = []
                for new_p in more_parts or [p]:
                    res.append(new_p)

        return res

    def _parse_headline_part(self, headline, classif, char):
        res = []

        if classif[0] == 'QUOTE':
            if type(char) == tuple:
                count_char = char[0]
            else:
                count_char = char
                char = (char, char)

            if headline.count(count_char) > 0:
                pttrn = r'%s([\w\d -.!/]+)%s' % (char[0], char[1])
                m = re.search(pttrn, headline)
                try:
                    if m:
                        part_text = m.group(1)
                        # print('> part %s (classif %s)' % (part_text, classif[0]))
                        headline_part = HeadlinePart(self, part_text, classif[0], char)

                        res.append(headline_part)
                except IndexError:
                    pass
        else:
            if char in headline:
                char_idx = headline.index(char)
                parts = (headline[:char_idx], headline[char_idx + 1:])

                for i, part_text in enumerate(parts):
                    part_text = part_text.strip()
                    if not part_text:
                        continue
                    # print('> part %s (classif %s)' % (part_text, classif[i]))
                    headline_part = HeadlinePart(self, part_text, classif[i], char)
                    res.append(headline_part)

        return res
