from chatgpt_util import send_message


def load_mctest():
    with open("./MCTestAnswers/mc160.test.txt", "r") as f:
        x = f.read()
        x = x.split("***************************************************")[1:]
    return x


def parse_question(question):
    ans = None
    for i in range(ord("A"), ord("D") + 1):
        if question.count("*" + chr(i) + ")") == 1:
            assert ans is None
            ans = chr(i)
            question = question.replace("*" + chr(i) + ")", " " + chr(i) + ")")
    assert ans is not None
    assert question.count("multiple: ") + question.count("one: ") == 1
    question = question.replace("multiple: ", "")
    question = question.replace("one: ", "")
    return question, ans


def parse(problem):
    segments = problem.strip().split("\n\n")[1:]
    n = len(segments)
    story = "\n\n".join(segments[: n - 4])
    questions = ""
    anss = []
    for i in range(n - 4, n):
        question, ans = parse_question(segments[i])
        if questions == "":
            questions = question
        else:
            questions += "\n\n" + question
        anss.append(ans)
    return story, questions, anss


def eval_chatGPT(story, questions, anss):
    assert len(anss) == 4
    query = "Read the following message, solve the following four questions.\n\n"
    query += story + "\n\n" + questions
    query += "\n\nOutput only four characters representing the answers, e.g.,\n1. A\n2. B\n3. A\n4. D"
    i = 2
    while True:
        try:
            res = send_message(query)
            res = res.split("\n")
            ok = True
            for r in res:
                if len(r) == 0:
                    # empty line exists
                    ok = False
            if not ok:
                continue
            res = list(map(lambda z: z[-1], res))
            if len(res) == 4:
                break
        except BaseException:
            print(res)
            import sys
            import traceback

            traceback.print_exc()
            sys.exit(1)

    correct = 0
    for i in range(4):
        if res[i] == anss[i]:
            correct += 1
    return correct, res
