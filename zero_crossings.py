# -*- coding: utf-8 -*-


def zero_crossings(x, thr):
    count = 0
    assert len(x.reshape(-1)) != 1, 'ERROR: input signal must have more than one element'
    assert len(x.shape) == 1 or any(x.shape == 1), 'ERROR: Input must be one-dimensional'
    x = x.reshape(-1)
    num_samples = len(x)
    for i in range(1, num_samples):
        if ((x[i] * x[i - 1]) < 0) and (abs(x[i] - x[i - 1]) > thr):
            count = count + 1

    return count
