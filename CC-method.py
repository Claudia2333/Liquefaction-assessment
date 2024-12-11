import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pykrige.ok import OrdinaryKriging
from pykrige.ok3d import OrdinaryKriging3D
import math


def cal_sx1(df,dw):
    df['up']=0.0
    df['down']=0.0
    df['dw']=dw
    ds,h,up,down=df.loc[:,'ds'].copy(),df['h'],df['up'],df['down']
    # special solution for the first point
    # no (i-1)
    if ds[0]>dw:
        # point is below water level
        up[0]=dw
        if h[0]==h[1]:
            down[0]=(ds[0]+ds[1])/2
        else:
            down[0]=h[0]
    
    # j for each line 
    for j in range(1,len(ds)):
        # for other points
        if ds[j]<=20 and ds[j]>dw:
            # point is below water level
            
            # for upper border
            if h[j-1]==h[j]:
                # before point in same layer
                if ds[j-1]<=dw:
                    # before point above water level
                    up[j]=dw
                else:
                    # before point below water
                    up[j]=(ds[j-1]+ds[j])/2
            
            elif h[j-1]<=dw:
                # upper layer is above water
                up[j]=dw
            else:
                # upper layer is below water
                up[j]=h[j-1]
            
            # for lower border
            if j == len(ds)-1:
                if h[j]>20:
                    down[j]=20
                # the last point
                else:down[j] = h[j]
            else:
                if h[j+1]==h[j]:
                    down[j] = (ds[j] + ds[j+1] ) /2
                else:
                    down[j] = h[j]

    # for the last point

    df['up'] = up
    df['down'] = down
    return df


def cal_all1(df,dw,N0):
    df['middle']=''
    df['Ncr']=''
    df['Wi']=''
    df['di']=''
    df['ie']=''
    type,ie,pc,N,ds,ie,up,down,Ncr,di,middle,Wi=df['type'],df['ie'],df['pc'],df['N'],df['ds'],df['ie'],df['up'],df['down'],df['Ncr'],df['di'],df['middle'],df['Wi']
    for i in range(len(up)):
        if True:
            di[i]=(down[i]-up[i])
            middle[i]=(down[i]+up[i])/2
            if pc[i]==0 or ds[i]<dw:
                Ncr[i]=0
            else:
                Ncr[i]=N0*0.95*(math.log(0.6*ds[i]+1.5)-0.1*dw)*math.sqrt(3/pc[i])

            if middle[i]<=5:
                Wi[i]=10
            else:
                if middle[i]==20:Wi[i]=0
                else:Wi[i]=-2*middle[i]/3+40/3
            
            if type[i]==1 or ds[i]<=dw or ds[i]>20:
                ie[i]=0
            elif N[i] != 0 and N[i]<=Ncr[i]:
                ie[i]=(1-N[i]/Ncr[i])*di[i]*Wi[i]
            else: ie[i]=0
        else:
            if ds[i]<=dw[i]:
                ie[i] = 0
            else:
                Ncr[i]=N0*0.95*(math.log(0.6*ds[i]+1.5)-0.1*dw[i])
                if N[i] <= Ncr[i] and ie[i] != 0 :
                    ie[i]=(1-N[i]/Ncr[i])*di[i]*Wi[i]
                else : ie[i] = 0
            df.loc[:,'ie'] = ie
            df.loc[:,'Ncr'] = Ncr  
                
    df.loc[:,'ie'] = ie
    df.loc[:,'Ncr'] = Ncr
    df.loc[:,'di'] = di
    df.loc[:,'middle'] = middle
    df.loc[:,'Wi'] = Wi
    return df


def cal_ie1(df):
    s = df['ie'].sum()
    return s 


import math

df1 = pd.read_csv('soil-CC.txt',sep='\t')

df1 = df1.rename(columns={'new_x':'x','new_y':'y','new_z':'h','new_type':'type','new_ds':'ds','N_un':'N'})

years = ['2000']

df = pd.read_excel('groundwater.xlsx')

N0s = [12,19]

dff = pd.DataFrame()

print_num = 0

for year in years:
    z1=df[year]
    for m in range(len(N0s)):
        N0=N0s[m]
        xx=[]
        yy=[]
        ie_xy = []
        sh=0 
        name = ['x','y']
        ly = df1[name[1]].unique()
        for i in range(len(ly)):
            df_y = df1[df1[name[1]].isin([ly[i]])]
            lx = df_y[name[0]].unique()
            for j in range(len(lx)):
                df_x_y = df_y[df_y[name[0]].isin([lx[j]])].reset_index(drop=True)
                ie_x_y = cal_ie1(cal_all1(cal_sx1(df_x_y,z1[sh]),z1[sh],N0))
                sh=sh+1
                ie_xy.append(ie_x_y)

                print_num = print_num + 1
                print(str(print_num)+':'+str(ie_x_y))

        col_name = year + ',N0='+str(N0)
        dff[col_name]=ie_xy
        
dff.to_excel('LPI-CC.xlsx',index=False)