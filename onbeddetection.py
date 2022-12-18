# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
from Calculate_motion import Calculate_motion
from zero_crossings import zero_crossings
from smooth import moving, lowess
from scipy.signal import find_peaks
from scipy import interpolate
from math import floor
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import multiprocessing

srcFace = 'C:/Users/How/Desktop/毕业设计/改写/sleepproj/txtdata/2022-12-06'
src = srcFace
srcsuffix = '.txt'
srcsuffixSave = '.txt'
files = os.listdir(srcFace)
doDispOrSave = True

motionRecord = 0
MCRRecord1 = [0]
MCRRecord2 = [0]
RMSRecord = [0]
MCR1 = []
MCR2 = []
RMS1 = []

fs = 50


def findpeaks(a, distance=None):
    ids, _ = find_peaks(a, distance=distance)  # 巨大变动，强制加入首尾下标
    ids = np.array([0] + ids.tolist() + [len(a) - 1])
    pks = a[ids]
    return pks, ids


def smooth(a, span=5, method='moving'):  # 搞不好要自创别的平滑方法
    if not isinstance(a, np.ndarray):
        a = np.array(a)
    if method == 'moving':
        return moving(a, span)
    # 有不小差别，时间效率也难以确定；实在不行naive手写或者调scipy/statsmodels.api的报再或者抄matlab里的moving函数
    elif method == 'lowess':
        return lowess(a, span)
    else:
        raise ValueError('Method passed illegal')


def rms(a):
    return np.sqrt((a * a).mean())


def paraPro(i):
    # global RMS1,MCR1
    print('Ready to process %d-th file' % (i + 1))
    srcName = files[i]
    noSuffixName = srcName[:-4]
    srcName1 = files[i]
    pathImgName = src + '/' + srcName1
    data = pd.read_table(pathImgName, sep=' ', header=None)
    win_len = 10 * fs
    moving_len = fs
    VI = np.array(data[0])
    VQ = np.array(data[1])
    VI = (VI - VI.mean()) / 32768 * 3.3
    VQ = (VQ - VQ.mean()) / 32768 * 3.3

    VI=smooth(VI, 10, 'lowess')
    VQ=smooth(VQ, 10, 'lowess')
    VI = smooth(VI, 15, 'moving')
    VQ = smooth(VQ, 15, 'moving')

    highrate, lowrate, BR, flag = Calculate_motion(VI, VQ, fs)

    # pks_up,locs_up = findpeaks(smooth(VI,50),distance=fs/BR-50)#区别应该很大，出了问题看matlab源码去
    # pks_down,locs_down = findpeaks(-smooth(VI,50),distance=fs/BR-50)

    # fI_up=interpolate.interp1d(locs_up,pks_up,kind='cubic')
    # yI_up=fI_up(np.arange(len(VI)))#特点，没法在原始数据上下限外插值
    # fI_down=interpolate.interp1d(locs_down,pks_down,kind='cubic')
    # yI_down=fI_down(np.arange(len(VI)))
    # yI_down_temp=yI_down-np.mean(yI_down)

    # pks_up,locs_up = findpeaks(smooth(VQ,50),distance=fs/BR-50)#区别应该很大，出了问题看matlab源码去
    # pks_down,locs_down = findpeaks(-smooth(VQ,50),distance=fs/BR-50)
    #
    # fQ_up=interpolate.interp1d(locs_up,pks_up,kind='cubic')
    # yQ_up=fQ_up(np.arange(len(VQ)))
    # fQ_down=interpolate.interp1d(locs_down,pks_down,kind='cubic')
    # yQ_down=fQ_down(np.arange(len(VQ)))
    # yQ_down_temp=yQ_down-np.mean(yQ_down)

    leng = floor((len(VI) - win_len) / moving_len)

    for m in range(leng):
        VI24G = VI[moving_len * m:win_len + moving_len * m]
        VQ24G = VQ[moving_len * m:win_len + moving_len * m]
        # yI_up24G=yI_up[moving_len*(m):win_len+moving_len*(m)]
        # yI_down24G=yI_down[moving_len*(m):win_len+moving_len*(m)]
        # yQ_up24G=yQ_up[moving_len*(m):win_len+moving_len*(m)]
        # yQ_down24G=yQ_down[moving_len*(m):win_len+moving_len*(m)]
        count1 = zero_crossings(VI24G, 0.0003)
        count2 = zero_crossings(VQ24G, 0.0003)

        # MCR=(min([np.var(yI_up24G),np.var(yI_down24G),np.var(yQ_up24G),np.var(yQ_down24G)]))
        RMS = rms(VI24G) + rms(VQ24G)

        MCR1.append(count1 + count2)
        # MCR2.append(MCR)
        RMS1.append(RMS)

    return MCR1, RMS1


# 预留给平行处理;maltab里6worker就比这边快了大概几十倍；本身不是完全没用
# python的并行无法同步内存的样子，内部的append操作全都无效,干脆返回再拼了
def process1():
    # global RMS1, MCR1
    num_cores = min(multiprocessing.cpu_count(), 6)
    results = Parallel(n_jobs=num_cores)(delayed(paraPro)(i) for i in range(len(files)))
    for ret in results:
        MCR1.extend(ret[0])
        # MCRRecord2.extend(ret[1])
        RMS1.extend(ret[1])
    # for i in range(len(files)):
    #     paraPro(i)


def process2():
    # global RMS1, MCR1
    total_recordtime = len(RMS1) / 60 / 60
    total_reftime = 13
    ratio_time = total_reftime / total_recordtime

    y = smooth(MCR1, 5) / 50
    flag_motion = np.zeros(len(y))
    fanshen = 0
    othermotion = 0

    for i in range(1, len(y)):
        if y[i] > 1.3:
            flag_motion[i] = 2;
            if flag_motion[i - 1] != 2:
                fanshen += 1
        elif y[i] > 0.5:
            flag_motion[i] = 1
            if flag_motion[i - 1] != 1:
                othermotion += 1
    num_motion = fanshen + othermotion
    RMSRecord = RMS1[1:]
    win_len = 5 * 60
    move_len = 1
    leng1 = floor((len(RMSRecord) - win_len) / move_len)
    x1 = np.zeros(leng1)
    for m in range(leng1):
        temp1 = RMSRecord[move_len * (m):win_len + move_len * (m)]
        x1[m] = np.sum(temp1)
    t = np.arange(len(x1)) / 60 / 60 * ratio_time
    flag_existbed = np.array(x1 < 3, dtype=np.int32)

    plt.figure(1)
    plt.plot(t, x1, color='r', label='dist deteded')
    plt.plot(t, flag_existbed, color='b', label='On bed flag')
    plt.legend()
    plt.show()

    onbed = np.where(x1 > max(x1) / 5)[0]
    temp = np.diff(onbed)
    ind_onbed = np.where(temp != 1)[0]

    gobedtime = onbed[0] * ratio_time / 60 / 60 + 19
    getuptime = onbed[ind_onbed[-1]] * ratio_time / 60 / 60 + 19 - 24

    print('Number of motion: %f' % (num_motion))
    print('Go to bed time: %f' % (gobedtime))
    print('Getup time: %f' % (getuptime))


if __name__ == '__main__':
    process1()
    process2()
