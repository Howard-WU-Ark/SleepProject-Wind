# -*- coding: utf-8 -*-
import numpy as np
from FFT_SHIFT import FFT_SHIFT
def trapz(a):
    return np.sum(a)-(a[0]+a[-1])/2

def Calculate_motion(VI,VQ,fs):
    if not isinstance(VI,np.ndarray):
        VI=np.array(VI)
    if not isinstance(VQ,np.ndarray):
        VQ=np.array(VQ)
    VI-=VI.mean()
    VQ-=VQ.mean()
    ori=VI+VQ*1j
    f1,C1=FFT_SHIFT(np.arange(1,len(ori)+1,1)/fs, ori)#可能有问题
    C1=C1.conjugate()
    
    scale1=0.6
    scale2=1.2
    row=np.where((f1>scale1) & (f1<=scale2))[0]#matlab里默认两维，这边麻烦死了
    motion=np.zeros(len(row),dtype=np.complex)
    for i in range(len(row)):
        motion[i]=C1[row[i]]
    alpha_highrate=trapz(abs(motion))/trapz(abs(C1))
    
    
    
    scale1=0.2
    scale2=0.5
    row=np.where((f1>scale1) & (f1<=scale2))[0]#matlab里默认两维，这边麻烦死了
    motion=np.zeros(len(row),dtype=np.complex)
    for i in range(len(row)):
        motion[i]=C1[row[i]]
    alpha_lowrate=trapz(abs(motion))/trapz(abs(C1))
    
    #find BR
    scale1=0.1
    scale2=0.5
    row=np.where((f1>=scale1) & (f1<=scale2))[0]
    
    temp=abs(C1[row[0]])
    ind=1
    for i in range(1,len(row)):
        if abs(C1[row[i]])>temp:
            temp=abs(C1[row[i]])
            ind=i
    BR=f1[row[ind]]
    
    #find 2-nd BR   可优化
    scale1=0.1+BR
    scale2=0.7
    row=np.where((f1>scale1) & (f1<scale2))[0]
    
    temp=abs(C1[row[0]])
    ind=1
    for i in range(1,len(row)):
        if abs(C1[row[i]])>temp:
            temp=abs(C1[row[i]])
            ind=i
    BR2=f1[row[ind]]
    flag=(BR2/BR/2)
    if flag>=0.9 and flag<=1.1:
        flag=1
    else:
        flag=0
        
    if alpha_highrate>0.1:
        flag_motion=1
    else:
        flag_motion=0  
    
    
    return alpha_highrate,alpha_lowrate,BR,flag

    