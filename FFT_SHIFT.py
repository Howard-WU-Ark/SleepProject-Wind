# -*- coding: utf-8 -*-
import numpy as np
def FFT_SHIFT(t, st):
    n=1
    dt=t[1]-t[0]
    T=t[-1]-t[0]
    df=1/T
    N=len(t)*n
    df_new=df/n
    f=np.arange(-N/2,N/2,1)*df_new
    sf=np.fft.fft(st,N)
    sf=T/N*np.fft.fftshift(sf)
    return f,sf
