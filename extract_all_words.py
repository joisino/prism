import pickle
from collections import defaultdict

from nltk import pos_tag
from nltk.tokenize import word_tokenize

from mctestutil import load_mctest, parse

x = load_mctest()

word_cnt = defaultdict(int)
for story, questions, anss in map(parse, x):
    tokens = word_tokenize(story.strip())
    poss = pos_tag(tokens)
    for word, pos in poss:
        word_cnt[(word, pos)] += 1

word_cnt = sorted([(cnt, word, pos) for (word, pos), cnt in word_cnt.items()])[::-1]

with open("all_words.pickle", "wb") as f:
    pickle.dump(word_cnt, f)
