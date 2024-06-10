import argparse

import numpy as np

from chatgpt_translator import ChatGPTTranslator
from mctestutil import eval_chatGPT, load_mctest, parse
from prism import Prism
from pup import PUP
from t5translator import T5Translator


class T5Wrapper:
    def __init__(self, model_name="t5-base", device="cpu"):
        self.translator = T5Translator(model_name, device)

    def translate_text(self, input_text, target_lang="German"):
        res = []
        for text in input_text.split(". "):
            res.append(self.translator.translate_text(text + ".", target_lang))
        return " ".join(res)


parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=str, default="French")
parser.add_argument("--basedir", type=str, default="./cand_words_French")
parser.add_argument("--rates", type=int, default=20)
parser.add_argument(
    "--method",
    type=str,
    default="prismstar",
    choices=["pup", "prismr", "prismstar", "nodecode"],
)
parser.add_argument("--translator", type=str, default="chatgpt", choices=["chatgpt", "t5", "t5-gpu"])
args = parser.parse_args()

x = load_mctest()

if args.method == "pup":
    pri = PUP()
elif args.method == "prismstar":
    pri = Prism(args.basedir)
elif args.method == "prismr":
    pri = Prism(args.basedir, star=False)
elif args.method == "nodecode":
    pri = Prism(args.basedir, exec_decode=False)

if args.translator == "chatgpt":
    translator = ChatGPTTranslator()
elif args.translator == "t5":
    translator = T5Wrapper()
elif args.translator == "t5-gpu":
    translator = T5Wrapper(device="cuda")


if args.method == "pup":
    rates = np.linspace(1, 30, args.rates)
else:
    rates = [0] + [0.01 * 100 ** (i / (args.rates - 1)) for i in range(args.rates)]

for rate in rates:
    print(rate)
    correct = 0
    cnt = 0
    for story, questions, anss in map(parse, x):
        if args.method == "pup":
            story_transformed = pri.encode(story, eps=rate)
        else:
            story_transformed, states = pri.encode(story, rate=rate)
        cc, res = eval_chatGPT(story_transformed, questions, anss)
        correct += cc
        cnt += 4
    print(rate, correct, cnt, correct / cnt)

    correct = 0
    cnt = 0
    for story, questions, anss in map(parse, x):
        if args.method == "pup":
            text_encoded = pri.encode(story, eps=rate)
        else:
            text_encoded, states = pri.encode(story, rate=rate)
        text_translated = translator.translate_text(text_encoded, target_lang=args.lang)
        if args.method == "pup":
            translated_story = pri.decode(text_translated)
        else:
            translated_story = pri.decode(text_translated, states)
        cc, res = eval_chatGPT(translated_story, questions, anss)
        correct += cc
        cnt += 4
    print(rate, correct, cnt, correct / cnt)
