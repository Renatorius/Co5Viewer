# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 19:27:59 2015

@author: René
"""

import numexpr as ne
import numpy as np

def S(rho, ei, eosfile):
    lnx11d = np.log(eosfile.block[0]["x1"].data +\
                     eosfile.block[0]["x1shift"].data).squeeze()
    lnx21d = np.log(eosfile.block[0]["x2"].data +\
                     eosfile.block[0]["x2shift"].data).squeeze()
    C = eosfile.block[0]["c1"].data.T
    x2_shift = eosfile.block[0]["x2shift"].data

    n1 = lnx11d.size-1
    n2 = lnx21d.size-1

    x1fac = float(n1) / (lnx11d.max() - lnx11d.min())
    x2fac = float(n2) / (lnx21d.max() - lnx21d.min())

    nx1 = rho.size-1
    nx2 = rho.size-2

    x1ta,x2ta,x1t,x2t,lnx1off,lnx2off,s = (np.zeros((rho.shape)) for i
                                                    in range(7))
    lnx1off = lnx11d[0]*np.ones(rho.shape)
    lnx2off = lnx21d[0]*np.ones(rho.shape)
    lnx1 = ne.evaluate('log(rho)')
    lnx2 = ne.evaluate('log(ei+x2_shift)')
    i1 = ne.evaluate('(lnx1-lnx1off)*x1fac').astype(int)
    i2 = ne.evaluate('(lnx2-lnx2off)*x2fac').astype(int)
    i1[i1<0] = 0
    i2[i2<0] = 0
    i1[i1>nx1] = nx1
    i2[i2>nx2] = nx2
    lnx11d = lnx11d[i1]
    lnx21d = lnx21d[i2]
    C = C[:,i1,i2]
    C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16 = C
    x1ta = lnx1 - lnx11d
    x2ta = lnx2 - lnx21d
    return ne.evaluate('C1+x1ta*(C2+x1ta*(C3+x1ta*C4))+x2ta*(C5+x1ta*(C6+\
                        x1ta*(C7+x1ta*C8))+x2ta*(C9+x1ta*(C10+x1ta*(C11+x1ta*C12))+\
                        x2ta*(C13+x1ta*(C14+x1ta*(C15+x1ta*C16)))))')

def TP(rho, ei, eosfile, C):
    lnx11d = np.log(eosfile.block[0]["x1"].data +\
                     eosfile.block[0]["x1shift"].data).squeeze()
    lnx21d = np.log(eosfile.block[0]["x2"].data +\
                     eosfile.block[0]["x2shift"].data).squeeze()
    C = C.T
    x2_shift = eosfile.block[0]["x2shift"].data

    n1 = lnx11d.size-1
    n2 = lnx21d.size-1

    x1fac = float(n1) / (lnx11d.max() - lnx11d.min())
    x2fac = float(n2) / (lnx21d.max() - lnx21d.min())

    nx1 = rho.size-1
    nx2 = rho.size-2

    x1ta,x2ta,x1t,x2t,lnx1off,lnx2off,s = (np.zeros((rho.shape)) for i
                                                    in range(7))
    lnx1off = lnx11d[0]*np.ones(rho.shape)
    lnx2off = lnx21d[0]*np.ones(rho.shape)
    lnx1 = ne.evaluate('log(rho)')
    lnx2 = ne.evaluate('log(ei+x2_shift)')
    i1 = ne.evaluate('(lnx1-lnx1off)*x1fac').astype(int)
    i2 = ne.evaluate('(lnx2-lnx2off)*x2fac').astype(int)
    i1[i1<0] = 0
    i2[i2<0] = 0
    i1[i1>nx1] = nx1
    i2[i2>nx2] = nx2
    lnx11d = lnx11d[i1]
    lnx21d = lnx21d[i2]
    C = C[:,i1,i2]
    C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16 = C
    x1ta = lnx1 - lnx11d
    x2ta = lnx2 - lnx21d
    return ne.evaluate('exp(C1+x1t*(C2+x1t*(C3+x1t*C4))+x2t*(C5+x1t*(C6+x1t*(C7+\
                        x1t*C8))+x2t*(C9+x1t*(C10+x1t*(C11+x1t*C12))+x2t*(C13+\
                        x1t*(C14+x1t*(C15+x1t*C16))))))')

def Pall(rho, ei, eosfile, C):
    lnx11d = np.log(eosfile.block[0]["x1"].data +\
                     eosfile.block[0]["x1shift"].data).squeeze()
    lnx21d = np.log(eosfile.block[0]["x2"].data +\
                     eosfile.block[0]["x2shift"].data).squeeze()
    C = C.T
    x2_shift = eosfile.block[0]["x2shift"].data

    n1 = lnx11d.size-1
    n2 = lnx21d.size-1

    x1fac = float(n1) / (lnx11d.max() - lnx11d.min())
    x2fac = float(n2) / (lnx21d.max() - lnx21d.min())

    nx1 = rho.size-1
    nx2 = rho.size-2

    x1ta,x2ta,x1t,x2t,lnx1off,lnx2off,s = (np.zeros((rho.shape)) for i
                                                    in range(7))
    lnx1off = lnx11d[0]*np.ones(rho.shape)
    lnx2off = lnx21d[0]*np.ones(rho.shape)
    lnx1 = ne.evaluate('log(rho)')
    lnx2 = ne.evaluate('log(ei+x2_shift)')
    i1 = ne.evaluate('(lnx1-lnx1off)*x1fac').astype(int)
    i2 = ne.evaluate('(lnx2-lnx2off)*x2fac').astype(int)
    i1[i1<0] = 0
    i2[i2<0] = 0
    i1[i1>nx1] = nx1
    i2[i2>nx2] = nx2
    lnx11d = lnx11d[i1]
    lnx21d = lnx21d[i2]
    C = C[:,i1,i2]
    C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16 = C
    x1ta = lnx1 - lnx11d
    x2ta = lnx2 - lnx21d
    P = ne.evaluate('exp(C1+x1t*(C2+x1t*(C3+x1t*C4))+x2t*(C5+x1t*(C6+x1t*(C7+\
                     x1t*C8))+x2t*(C9+x1t*(C10+x1t*(C11+x1t*C12))+x2t*(C13+x1t*(\
                     C14 + x1t*(C15 + x1t*C16))))))')
    dPdrho = ne.evaluate('P/rho*(C2+x1t*(2*C3+x1t*3*C4)+x2t*(C6+x1t*(2*C7+x1t*3*C8)+\
                          x2t*(C10+x1t*(2*C11+x1t*3*C12)+x2t*(C14+x1t*(2*C15+\
                          x1t*3*C16)))))')
    dPde = ne.evaluate('P/(e+x2_shift)*(C5+x1t*(C6+x1t*(C7+x1t*C8))+2*x2t*(C9+\
                        x1t*(C10+x1t*(C11+x1t*C12))+1.5*x2t*(C13+x1t*(C14+x1t*\
                        (C15+x1t*C16)))))')
    return P, dPdrho, dPde

def Tall(rho, ei, eosfile, C):
    lnx11d = np.log(eosfile.block[0]["x1"].data +\
                     eosfile.block[0]["x1shift"].data).squeeze()
    lnx21d = np.log(eosfile.block[0]["x2"].data +\
                     eosfile.block[0]["x2shift"].data).squeeze()
    C = C.T
    x2_shift = eosfile.block[0]["x2shift"].data

    n1 = lnx11d.size-1
    n2 = lnx21d.size-1

    x1fac = float(n1) / (lnx11d.max() - lnx11d.min())
    x2fac = float(n2) / (lnx21d.max() - lnx21d.min())

    nx1 = rho.size-1
    nx2 = rho.size-2

    x1ta,x2ta,x1t,x2t,lnx1off,lnx2off,s = (np.zeros((rho.shape)) for i
                                                    in range(7))
    lnx1off = lnx11d[0]*np.ones(rho.shape)
    lnx2off = lnx21d[0]*np.ones(rho.shape)
    lnx1 = ne.evaluate('log(rho)')
    lnx2 = ne.evaluate('log(ei+x2_shift)')
    i1 = ne.evaluate('(lnx1-lnx1off)*x1fac').astype(int)
    i2 = ne.evaluate('(lnx2-lnx2off)*x2fac').astype(int)
    i1[i1<0] = 0
    i2[i2<0] = 0
    i1[i1>nx1] = nx1
    i2[i2>nx2] = nx2
    lnx11d = lnx11d[i1]
    lnx21d = lnx21d[i2]
    C = C[:,i1,i2]
    C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16 = C
    x1ta = lnx1 - lnx11d
    x2ta = lnx2 - lnx21d
    T = ne.evaluate('exp(C1+x1t*(C2+x1t*(C3+x1t*C4))+x2t*(C5+x1t*(C6+x1t*(C7+\
                     x1t*C8))+x2t*(C9+x1t*(C10+x1t*(C11+x1t*C12))+x2t*(C13+x1t*(\
                     C14+x1t*(C15+x1t*C16))))))')
    dTde = ne.evaluate('T/(e+x2_shift)*(C5+x1t*(C6+x1t*(C7+x1t*C8))+2*x2t*(C9+\
                        x1t*(C10+x1t*(C11+x1t*C12))+1.5*x2t*(C13+x1t*(C14+x1t*\
                        (C15+x1t*C16)))))')
    return T, dTde