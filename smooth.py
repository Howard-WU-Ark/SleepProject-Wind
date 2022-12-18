import numpy as np


def moving(a, span):
    if span % 2 == 0:
        span -= 1
    length = len(a)
    assert span <= length, 'Span is bigger than data length'
    win = np.ones(span) / span
    c = np.convolve(a, win)[:len(a)]  # 这个更符合matlab里的函数
    cbegin = np.cumsum(a[:span - 2])
    cbegin = cbegin[::2] / np.arange(1, span - 1, 2)
    cend = np.cumsum(a[:-(span - 1):-1])
    cend = cend[::-2] / np.arange(span - 2, 0, -2)
    c = np.hstack((cbegin, c[span - 1:], cend))

    return c


def unifloess(a, span):
    a = a.reshape(-1)
    halfw = span // 2
    d = abs(np.arange(1 - halfw, halfw))
    dmax = halfw
    x1 = np.arange(1 - halfw, halfw).reshape(-1, 1)
    weight = (1 - (d / dmax) ** 3) ** 1.5
    v = np.hstack((np.ones(x1.shape), x1))
    V = v * weight.reshape(-1, 1).repeat(2, axis=1)
    Q, _ = np.linalg.qr(V)
    alpha = Q[halfw - 1, :].dot(Q.T)
    alpha = alpha * weight
    ys = np.convolve(a, alpha)[:len(a)]
    ys[halfw:-halfw] = ys[span - 2:-1]
    x1 = np.arange(1, span).reshape(-1, 1)
    v = np.hstack((np.ones(x1.shape), x1))
    for j in range(1, 1 + halfw):
        d = abs(np.arange(1, span) - j)
        weight = (1 - (d / (span - j)) ** 3) ** 1.5
        V = v * weight.reshape(-1, 1).repeat(2, axis=1)
        Q, _ = np.linalg.qr(V)
        alpha = Q[j - 1, :].dot(Q.T)
        alpha = alpha * weight
        ys[j - 1] = alpha.dot(a[:span - 1])
        ys[- j] = alpha.dot(a[:-span:-1])

    return ys


def lowess(a, span):
    span = 2 * span // 2 + 1
    length = len(a)
    assert span <= length, 'Span is bigger than data length'
    # 代码原理得知必定可走捷径
    return unifloess(a, span)


if __name__ == '__main__':
    a = np.arange(1, 101)
    # print(a[:-10:-1])
    # print(moving(a, 10))
    print(lowess(a, 10))
