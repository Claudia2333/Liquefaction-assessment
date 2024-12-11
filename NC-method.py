import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from pykrige.ok import OrdinaryKriging


def cal_FS(df,dw,feng,MSF):
    p,ds,z,fc,psat,N,type=df['p'],df['ds'],df['z'],df['fc'],df['psat'],df['N'],df['type']

    j=-1

    if dw<=z[0]:
        j=0
    else:
        for m in range(len(ds)):
            if dw>z[m]:
                j=j+1


    y=[0]
    sigma=[0]
    sigma_p=[0]
    i=0
    for zz in z:
        if(i<j): 
            if i == 0:
                s = zz*p[i]
                se = s
            else:
                s = (z[i]-z[i-1])*p[i] + sigma[i]
                se = (z[i]-z[i-1])*p[i] + sigma_p[i]
        elif(i==j):
            if i == 0:
                s = sigma[i] + (dw-0)*p[i]
                se = sigma_p[i] + (dw-0)*p[i] 
            else:
                s = sigma[i] + (dw-z[i-1])*p[i]
                se = sigma_p[i] + (dw-z[i-1])*p[i] 
            y.append(dw)
            sigma.append(s)
            sigma_p.append(se)
            s = sigma[i+1] + (z[i]-dw)*psat[i]
            se = sigma_p[i+1] + (z[i]-dw)*(psat[i]-10)
        else:
            s = sigma[i+1] + (z[i]-z[i-1])*psat[i]
            se = sigma_p[i+1] + (z[i]-z[i-1])*(psat[i]-10)
        i = i + 1
        y.append(zz)
        sigma.append(s)
        sigma_p.append(se)

    df1 = pd.DataFrame()
    df1['y'] = y
    df1['sigma']=sigma
    df1['sigma_p']=sigma_p
    df1 = df1.drop_duplicates()
    y = df1['y'].to_list()
    sigma=df1['sigma'].to_list()
    sigma_p=df1['sigma_p'].to_list()


    x_test = ds.to_list()
    sigma_test = [np.interp(x_i,y, sigma) for x_i in x_test]
    sigma_p_test = [np.interp(x_i,y, sigma_p) for x_i in x_test]


    rd = [cal_rd1(x_i) for x_i in x_test]


    CN = [cal_cn1(s_pi) for s_pi in sigma_p_test]


    CR = [cal_CR1(x_i) for x_i in x_test]


    CSR = [(0.65*feng*sigma_test[i]*rd[i]/sigma_p_test[i]) for i in range(len(ds)) ]
    

    N160=[(N[i]*CN[i]*CR[i]) for i in range(len(ds))]


    alpha=[]
    beta=[]
    for fcc in fc:
        if fcc<=5: 
            al=0
            be=1
        elif fcc<35:
            al=math.exp(1.76-(190/fcc**2))
            be=0.99+(fcc**1.5/1000)
        else:
            al=5
            be=1.2
        alpha.append(al)
        beta.append(be)


    N160cs = [(alpha[i]+beta[i]*N160[i]) for i in range(len(ds))]


    CRR = [(1/(34-n)+n/135+50/((10*n+45)**2)-1/200) for n in N160cs]

    
    FS = [(CRR[i]/CSR[i]*MSF) for i in range(len(ds))]
    

    FWH=[]
    zz=[]
    hh=[]
    for i in range(len(ds)):
        if type[i] == 1 or ds[i] <= dw or ds[i]>20 or N160cs[i] >= 30:
            FWH.append(0)
            zz.append(0)
            hh.append(0)
        else:
            if i == 0:
                zn = ds[i]/2
                H = ds[i]    
            else:
                if ds[i-1]==0 and i == 1: 
                    zn = ds[i]/2
                    H = ds[i]  
                else:
                    if ds[i-1] == 0 and ds[i-2] ==0:
                        zn = 0.5*(ds[i-3]+ds[i])
                        H = ds[i]-ds[i-3]
                    else:
                        if ds[i-1] == 0:
                            zn = 0.5*(ds[i-2]+ds[i])
                            H = ds[i]-ds[i-2]
                        else:
                            zn = 0.5*(ds[i-1]+ds[i])
                            H = ds[i]-ds[i-1]

            w = 10-0.5*zn
            if FS[i] >1:
                F=0
            else:
                F=1-FS[i]
            FWH.append(w*F*H)
            zz.append(zn)
            hh.append(H)
    

    df['sigma'] = sigma_test
    df['sigma_p'] = sigma_p_test
    df['rd'] = rd
    df['CN'] = CN
    df['CR'] = CR
    df['N160'] = N160
    df['alpha']=alpha
    df['beta']=beta
    df['N160CS']=N160cs
    df['CSR'] = CSR
    df['CRR'] = CRR
    df['FS'] = FS
    df['z_cal']=zz
    df['H']=hh
    df['FWH'] = FWH
    df['LPI'] = sum(FWH)
    df['dw']=dw
    return df,sum(FWH)



def cal_rd1(ds):
    if ds<=9.15:return 1-0.00765*ds
    else: return 1.174-0.0267*ds


def cal_cn1(sigma_p_test):
    if sigma_p_test<=200: 
        cn=(100/sigma_p_test)**0.5
    else:
        cn=2.2/(1.2+sigma_p_test/100)
    if cn>1.7:
        cn=1.7
    return cn

def cal_CR1(ds):
    if ds+2 <3:
        cr = 0.75
    elif ds+2<4:
        cr = 0.8
    elif ds+2 < 6:
        cr = 0.85
    elif ds+2 < 10:
        cr = 0.95
    else:
        cr = 1
    return cr


df1 = pd.read_csv('soil-NC.txt',sep='\t')

df1 = df1.rename(columns={'new_x':'x','new_y':'y','new_z':'z','new_type':'type','new_ds':'ds','N_un':'N'})

years = ['2000']

df=pd.read_excel('groundwater.xlsx')


ffeng = [0.2,0.4]
MMSF=[1.6686582273731845,1.3243814379331034]

dff = pd.DataFrame()

print_num = 0

for year in years:

    z1=df[year]
    
    for m in range(len(ffeng)):
        feng=ffeng[m]
        MSF=MMSF[m]

        xx=[]
        yy=[]
        ie_xy = []
        LPI=[]
        sh=0

        name = ['x','y']
        ly = df1[name[1]].unique()
        for i in range(len(ly)):
            df_y = df1[df1[name[1]].isin([ly[i]])]
            lx = df_y[name[0]].unique()
            for j in range(len(lx)):
                df_x_y = df_y[df_y[name[0]].isin([lx[j]])].reset_index(drop=True)

                ie_x_y,lpi = cal_FS(df_x_y,z1[sh],feng,MSF)
                sh=sh+1
                LPI.append(lpi)

                print_num = print_num + 1 
                print(str(print_num)+':'+str(lpi))

        col_name = year + ',a='+str(feng)
        dff[col_name]=LPI 

dff.to_excel('LPI-NC.xlsx',index=False)