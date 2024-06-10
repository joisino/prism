import argparse
import os
import pickle
import random
from collections import defaultdict

import sacrebleu
from nltk import pos_tag
from nltk.tokenize import word_tokenize

from t5translator import T5Translator

random.seed(0)

parser = argparse.ArgumentParser()
parser.add_argument("start", type=int)
parser.add_argument("end", type=int)
parser.add_argument("--trial", type=int, default=1000)
parser.add_argument("--target", type=str, default="French")
parser.add_argument("--threshold", type=float, default=2.0)
parser.add_argument("--device", type=str, default="cpu")
args = parser.parse_args()

with open("all_words.pickle", "rb") as f:
    all_words = pickle.load(f)
all_words = all_words[args.start - 1 : args.end]

source_sentences = []
with open(sacrebleu.get_source_file("wmt14", "en-fr"), "rb") as f:
    for r in f:
        source_sentences.append(r.decode().strip())

translator = T5Translator(device=args.device)

results = []

for i, (_, word, pos) in enumerate(all_words):
    cnt = 0
    pxc = defaultdict(int)
    px = defaultdict(int)

    while cnt < args.trial:
        print("\r{} / {} [{}, {}] {} / {}".format(i + 1, len(all_words), word, pos, cnt, args.trial), end="")
        ind = random.randint(0, len(source_sentences) - 1)
        text = source_sentences[ind]
        tokens = word_tokenize(text)
        poss = pos_tag(tokens)
        if pos not in [w[1] for w in poss]:
            continue
        text_translated = translator.translate_text(text, target_lang=args.target)
        tokens_translated = word_tokenize(text_translated)
        for r in tokens_translated:
            px[r] += 1
        word_replaced = poss[[w[1] for w in poss].index(pos)][0]
        text_replaced = text.replace(word_replaced, word)
        text_translated = translator.translate_text(text_replaced, target_lang=args.target)
        tokens_translated = word_tokenize(text_translated)
        for r in tokens_translated:
            pxc[r] += 1
        cnt += 1
    li = sorted([(c / (px[w] + 1), w) for w, c in pxc.items()])[::-1]
    pairs = [w for p, w in li if p > args.threshold]
    ps = [p for p, w in li if p > args.threshold]
    if len(pairs) == 0:
        pairs = [li[0][1]]
        ps = [li[0][0]]
    results.append((word, pos, ps, pairs))
print()

os.makedirs("cand_words_{}_{}".format(args.target, args.trial), exist_ok=True)
with open("cand_words_{}_{}/res_{}_{}.pickle".format(args.target, args.trial, args.start, args.end), "wb") as f:
    pickle.dump(results, f)
