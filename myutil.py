def parse(x, reverse=False):
    priv = [1 - float(r.split()[3]) for r in x.split("\n")[1::3]]
    acc = [float(r.split()[3]) for r in x.split("\n")[2::3]]
    if reverse:
        priv = priv[::-1]
        acc = acc[::-1]
    return priv, acc


def aupqc(priv, acc):
    assert len(priv) == len(acc)
    assert priv[0] < priv[-1]
    s = 0
    pp, pq = None, None
    for p, q in zip(priv, acc):
        if pp is None:
            s += p * q
        else:
            s += (p - pp) * (q + pq) / 2
        pp, pq = p, q
    return s


def accat(priv, acc, threshold):
    assert len(priv) == len(acc)
    assert priv[0] < priv[-1]
    pp, pq = None, None
    for p, q in zip(priv, acc):
        if p > threshold:
            # interpolate
            if pp is None:
                return q
            else:
                return pq + (q - pq) * (threshold - pp) / (p - pp)
        pp, pq = p, q
    assert False
