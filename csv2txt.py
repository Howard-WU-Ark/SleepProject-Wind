# -*- coding: utf-8 -*-
import os
import pandas as pd
from datetime import datetime as dt

def datenum(d):#因为只有日期设计to/from oridinal,后半部分靠统计sec再除以一天秒数得到天数
    return 366 + d.toordinal() + (d - dt.fromordinal(d.toordinal())).total_seconds()/(24*60*60)

fileSavePath='C:/Users/How/Desktop/毕业设计/改写/sleepproj/txtdata'
if not os.path.exists(fileSavePath):
    os.mkdir(fileSavePath)
srcsuffix='.txt'
srcsuffixSave='.txt'
csvfile='C:/Users/How/Desktop/毕业设计/改写/sleepproj/2022-12-07-21-45-52_EXPORT_CSV_7593735_972_193685094402_raw_0.csv'
M=pd.read_csv(csvfile)
times=M['timestamp']
i_channels=M['i_channel']
q_channels=M['q_channel']

tmp=[t.split() for t in times]
tmp1=[t[1].split(':') for t in tmp]
tmp2=['-'.join(t) for t in tmp1]
timename=[a[0]+'-'+b for (a,b) in zip(tmp,tmp2)]
times_sec=[datenum(dt.strptime(t, '%Y-%m-%d %H:%M:%S')) for t in times]

doDispOrSave = True
fs=50
motionRecord=0
Timestamp=0
ind=2


I=[int(c) for c in i_channels[0].split(',')]
Q=[int(s) for s in q_channels[0].split(',')]
fileSavePath0=fileSavePath+'/'+tmp[0][0]
if not os.path.exists(fileSavePath0):
    os.mkdir(fileSavePath0)
for i in range(1,len(times)):
    if int(tmp1[i][0])==19 and tmp1[i][0]!=tmp[0][0]:
        fileSavePath0=fileSavePath+'/'+tmp[i][0]
        if not os.path.exists(fileSavePath0):
            os.mkdir(fileSavePath0)
    if int(tmp1[i][0])>=10 and int(tmp1[i][0])<19:
        continue
    savetxtName=fileSavePath0+'/'+timename[i]+'.txt'
    VI=[int(c) for c in i_channels[i].split(',')]
    VQ=[int(s) for s in q_channels[i].split(',')]
    minlen=min(len(VI),len(VQ))
    VI=VI[:minlen]
    VQ=VQ[:minlen]
    if ind>=2 and ind<15:
        I.extend(VI)
        Q.extend(VQ)
        if ind==len(times):
            with open(savetxtName,'w') as f:
                for k in range(len(Q)):
                    f.write('%d %d\n'%(I[k],Q[k]))
                    
            f.close()
    elif ind==15:
        ind=1
        with open(savetxtName,'w') as f:
            for k in range(len(Q)):
                f.write('%d %d\n'%(I[k],Q[k]))
        f.close()
        I=VI
        Q=VQ
    ind+=1
    
    
    
    
    
    
    
    
    