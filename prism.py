import pickle
import random
import re
import sys
from collections import defaultdict

from nltk import pos_tag
from nltk.tokenize import word_tokenize


def common_prefix_length(str1, str2):
    common_length = 0

    for i in range(min(len(str1), len(str2))):
        if str1[i] == str2[i]:
            common_length += 1
        else:
            break
    return common_length


def normalize_quote(token):
    return token.replace("``", '"').replace("''", '"')


def reassemble(text, tokens, new_tokens):
    split_text = re.split(r"(\s|\n)", text)
    new_text = []
    j = 0
    for original_word in split_text:
        if original_word == "" or re.search(r"\s", original_word):
            new_text.append(original_word)
            continue
        reassembled_word = ""
        new_reassembled_word = ""
        while j < len(tokens) and len(reassembled_word) + len(normalize_quote(tokens[j])) <= len(
            normalize_quote(original_word)
        ):
            reassembled_word += normalize_quote(tokens[j])
            new_reassembled_word += new_tokens[j]
            j += 1
        new_text.append(new_reassembled_word)
        if len(normalize_quote(original_word)) != len(reassembled_word):
            print(text)
            print(original_word)
            print(reassembled_word)
            print(new_reassembled_word)
            print(tokens[j - 3 : j + 3])
            raise ValueError("Tokenization mismatch")

    new_text = "".join(new_text)
    return new_text


def replace_word_with_pos(text, pos, fr, to):
    tokens = word_tokenize(text)
    pos_tagged_words = pos_tag(tokens)

    # Replace fr in token sequence with to
    new_tokens = []
    ok = False
    for word, tag in pos_tagged_words:
        if word == fr and tag == pos and not ok:
            new_tokens.append(to)
            ok = True
        else:
            new_tokens.append(word)
    if not ok:
        return text, False

    # Reassemble text with spaces
    res = reassemble(text, tokens, new_tokens)

    return res, ok


def replace_token_in_text(text, fr, to):
    tokens = word_tokenize(text)

    # Replace fr in token sequence with to
    new_tokens = []
    cnt = 0
    for token in tokens:
        if token == (fr[0].lower() + fr[1:]):
            new_tokens.append(to[0].lower() + to[1:])
            cnt += 1
        elif token == (fr[0].upper() + fr[1:]):
            new_tokens.append(to[0].upper() + to[1:])
            cnt += 1
        else:
            new_tokens.append(token)

    if cnt == 0:
        return text, False

    # Reassemble text with spaces
    res = reassemble(text, tokens, new_tokens)

    return res, True


def replace_token_in_text_fuzzy(text, fr, to):
    tokens = word_tokenize(text)
    if len(tokens) == 0:
        return text, False

    prefix_length = [
        (common_prefix_length(fr.lower(), token.lower()), -len(token), token, i) for i, token in enumerate(tokens)
    ]
    d, _, token, i = sorted(prefix_length)[-1]
    new_tokens = tokens.copy()
    if d >= 5 or (d == 4 and max(len(fr), len(token)) <= 5):
        if token[0].isupper():
            new_tokens[i] = to[0].upper() + to[1:]
        else:
            new_tokens[i] = to[0].lower() + to[1:]
    else:
        return text, False

    # Reassemble text with spaces
    res = reassemble(text, tokens, new_tokens)

    return res, True


class Prism:
    def __init__(self, basedir="./prism_setting", star=True, exec_decode=True, fuzzy=True):
        with open("{}/cands_all.pickle".format(basedir), "rb") as f:
            self.dic = pickle.load(f)

        self.star = star
        self.exec_decode = exec_decode
        self.fuzzy = fuzzy

        if self.star:
            self.replacer = {}
        else:
            self.replacer = []
        for pos, dic in self.dic.items():
            replacer = []
            for word, (ps, pairs) in dic.items():
                if len(ps) > 0:
                    replacer.append((ps[0], word, pairs))
            if self.star:
                self.replacer[pos] = sorted(replacer)[::-1]
            else:
                self.replacer += replacer

        unchanged_ps = []
        for pos, dic in self.dic.items():
            for word, (ps, _) in dic.items():
                if self.unchanged_word(pos, word) and len(ps) > 0:
                    unchanged_ps.append(ps[0])
        self.unchanged_average = sum(unchanged_ps) / len(unchanged_ps) if len(unchanged_ps) > 0 else 0

        self.prev_used = None

    def unchanged_word(self, pos, word):
        if pos in ["NNP", "NNPS"]:
            return True
        if pos == "CD" and word.isdigit():
            return True
        return False

    def create_cands(self, poss):
        cands = []
        for word, pos in poss:
            if pos not in self.dic:
                print(
                    'Warning: "{}" is not in the dictionary. This may degrade the performance.'.format(pos),
                    file=sys.stderr,
                )
                continue
            if word not in self.dic[pos] or len(self.dic[pos][word][0]) == 0:
                # dic does not know the translated word
                print(
                    'Warning: "({}, {})" is not in the dictionary. This may degrade the performance.'.format(
                        word, pos
                    ),
                    file=sys.stderr,
                )
                if self.unchanged_word(pos, word):
                    cands.append((self.unchanged_average, pos, word, word))
                else:
                    cands.append((0, pos, word, word))
                continue
            cands.append((self.dic[pos][word][0][0], pos, word, self.dic[pos][word][1][0]))
        cands = sorted(cands)[::-1]
        return cands

    def encode_simple(self, text, rate=0.2):
        tokens = word_tokenize(text)
        poss = pos_tag(tokens)
        assert len(tokens) == len(poss)
        states = []
        new_tokens = tokens.copy()
        for i in range(len(tokens)):
            word, pos = tokens[i], poss[i][1]
            if word in self.dic[pos] and random.random() < rate:
                _, replace_word, replace_translated_words = random.choice(self.replacer)
                new_tokens[i] = replace_word
                states.append(
                    (
                        replace_translated_words,
                        self.dic[pos][word][1][0],
                        pos,
                        word,
                        replace_word,
                    )
                )
            elif word not in self.dic[pos]:
                print(
                    'Warning: "({}, {})" is not in the dictionary. This may degrade the performance.'.format(
                        word, pos
                    ),
                    file=sys.stderr,
                )
        text = reassemble(text, tokens, new_tokens)
        return text, states

    def encode(self, text, rate=0.2):
        if not self.star:
            return self.encode_simple(text, rate)
        tokens = word_tokenize(text)
        poss = pos_tag(tokens)
        num_changes = int(len(poss) * rate)
        poss = set(poss)
        cands = self.create_cands(poss)
        its = defaultdict(int)
        words_to_be_translated = set()
        states = []
        self.prev_used = []
        ind = 0
        while ind < len(cands) and len(states) < num_changes:
            _, pos, word, translated_word = cands[ind]
            ind += 1
            self.prev_used.append((pos, word))
            while len(states) < num_changes:
                # skip duplicated words to be translated
                while (
                    its[pos] < len(self.replacer[pos]) and self.replacer[pos][its[pos]][2][0] in words_to_be_translated
                ):
                    its[pos] += 1
                if its[pos] >= len(self.replacer[pos]):
                    # We already exhaust this pos.
                    ind = random.randint(0, len(self.replacer[pos]) - 1)
                else:
                    ind = its[pos]
                    its[pos] += 1
                _, replace_word, replace_translated_words = self.replacer[pos][ind]
                text, ok = replace_word_with_pos(text, pos, word, replace_word)
                if not ok:
                    break

                words_to_be_translated.add(replace_translated_words[0])
                states.append(
                    (
                        replace_translated_words,
                        translated_word,
                        pos,
                        word,
                        replace_word,
                    )
                )
        return text, states

    def decode(self, text, states):
        if not self.exec_decode:
            return text
        for xs, y, _, _, _ in states:
            ok = False
            for x in xs:
                text, ok = replace_token_in_text(text, x, y)
                if ok:
                    break
            if not ok and self.fuzzy:
                for x in xs:
                    text, ok = replace_token_in_text_fuzzy(text, xs[0], y)
                    if ok:
                        break
        return text
