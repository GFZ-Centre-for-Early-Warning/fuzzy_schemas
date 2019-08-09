#fuzzy.py 
#atuthor: Massimiliano Pittore, @GFZ 2019
#

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, show, cm
from matplotlib.patches import Polygon


def fuzzy_sum(a,b,ac=1,bc=1):
    '''
    Weighted sum of two triangular fuzzy numbers. implements:
    sum = ac*a + bc*b
    'ac' and 'bc' are the (real-valued) multiplicative coefficient 
    of the two summands 'a' and 'b'. 
    '''
    #a,b: triangular fuzzy numbers
    #ac,bc: coefficients (multiplicative)
    # equivalent to d = ac*a + bc*b
    d = [ac*a[0]+bc*b[0],ac*a[1]+bc*b[1],ac*a[2]+bc*b[2]]
    return d

def defuzzify(a,method='mode'):
    '''
    turn a triangular fuzzy number into a crisp number (i.e., a single real value). 
    Mode may take the following values: 'mode','mean','median', 
    indicating the respective statistical descriptors considering the TFN as 
    a piecewise linear probability density.
    '''
    r = 0
    if (method=='mode'):
        r = a[0]
    elif (method=='mean'):
        r = sum(a)/3.0
    elif (method=='median'):
        if (a[0]>=(a[1]+a[2])/2.0):
            r = a[1]+np.sqrt((a[2]-a[1])*(a[0]-a[1])/2.0)
        else:
            r = a[2]-np.sqrt((a[2]-a[1])*(a[2]-a[0])/2.0)
    else:
        raise NumError('unrecognized method: {}'.format(method))
    return r


def fuz_greater(a,b):
    '''
    Compute the degree of membership of the relation "a > b"
    between two triangular fuzzy numbers.
    after:
    D. Dorohonceanu and A. Marin (2002) Simple Method for Comparing Fuzzy Numbers, and
    A. S. Dadgostar, A Decentralized Reactive Fuzzy Scheduling System for 
    Cellular Manufacturing Systems, 
    Ph.D. Thesis, University of South Wales, Australia, 1996.
    
    NOTE: crisp inputs are not supported
    '''
    dsum=dsuml=0
    for p in np.arange(0,1,0.2):
        i_a = [a[1]+p*(a[0]-a[1]),a[2]-p*(a[2]-a[0])]
        i_b = [b[1]+p*(b[0]-b[1]),b[2]-p*(b[2]-b[0])]
        d = (i_a[1]-i_b[0]) / (i_b[1]-i_b[0]+i_a[1]-i_a[0])
        if d>1: d=1
        if d<0: d=0
        dl = (i_b[1]-i_b[0])*(i_a[1]-i_a[0])
        dsum = dsum+d*dl
        dsuml = dsuml+dl
        assert abs(dsuml)>1e-8,'error, crisp numbers are not supported'
    return dsum/dsuml

def fuz_argmax(fvec,mThresh=0.5):
    '''
    implement argmax of a list of fuzzy numbers 'fvec'.
    'mThresh' is the threshold on the degree of membership of 
    the 'greater than' relation in order to consider the number actually greater.
    '''
    ind1=0
    ind2=1
    for step in range(1,len(fvec)):
        if fuz_greater(fvec[ind1],fvec[ind2])<mThresh:
            ind1 = ind2
        ind2 = ind2+1
    return ind1
    

def plot_fnum(fnumlist):
    '''
    Plot a list of triangular fuzzy numbers as triangles (polygons)
    '''
    plt.figure()
    ax = plt.gca()

    for fnum in fnumlist:
        print (fnum)
        poly = get_tripoly(fnum)
        p = Polygon(poly,closed=True,color='red',alpha=0.2,fill=False)
        ax.add_patch(p)

    ax.set_xlim(-1,1)
    plt.show()

def get_tripoly(f_num):
    '''
    auxiliary. Turns a triangular fuzzy number into a polygon 
    '''
    poly = [[f_num[1],0],[f_num[0],1],[f_num[2],0]]
    return poly

def plot_v_fnum(ax,fnum, xx, width,alpha):
    '''
    plots a triangular fuzzy number 'fnum' on a predefined axix 'ax' at a x-coord 'xx'
    as a rectangular patch with gradient fill, opacity 'alpha' and width 'width'. 
    Also overlay three defuzzified estimates. It needs the auxiliary 
    function 'defuzzify'.
    '''
    Xup = [[1, 1], [.0, .0]]
    Xdown = [[.0, .0], [1, 1]]
    ax.imshow(Xdown, interpolation='quadric', cmap=cm.Blues,vmin=-1,vmax=1,
                      extent=(xx-width, xx+width, fnum[0],fnum[2]), alpha=alpha)
    ims = ax.imshow(Xup, interpolation='quadric', cmap=cm.Blues,vmin=-1,vmax=1,
                      extent=(xx-width, xx+width, fnum[1],fnum[0]), alpha=alpha)
    mode=defuzzify(fnum,'mode')
    median=defuzzify(fnum,'median')
    mean=defuzzify(fnum,'mean')
    hl1 = ax.hlines(y=mode, xmin=xx-width, xmax=xx+width,alpha=alpha)
    hl2 = ax.hlines(y=median, xmin=xx-width, xmax=xx+width,alpha=alpha,linestyle='dashed')
    hl3  = ax.hlines(y=mean, xmin=xx-width, xmax=xx+width,alpha=alpha,linestyle='dotted')
    return ims


def plot_fnum_vec(fnum_list,fnum_lab,figfilename='',alpha=0.5,rot=0,ha ='center',loc='upper right'):
    '''
    Plots a list of triangular fuzzy nubers 'fnum_list', with respective
    labels 'fnum_lab'. 'alpha' is the level of opacity, 'rot' the rotation of the x labels,
    'ha' is the location of the x-labels with respect to the theoretic position, 
    'loc' is the location of the legend. 
    if 'figfilename' is defined then is used as path and filename to save the figure.
    Needs the auxiliary function plot_v_fnum.
    '''
    fig = figure()
    bar_width = 0.5

    n_groups= len(fnum_list)
    ax = fig.add_subplot(111, xlim=[bar_width/2,n_groups+bar_width], ylim=[-1,1],
                         autoscale_on=False)

    ax.set_xticks(np.arange(n_groups) + 1)
    ax.set_xticklabels(fnum_lab,rotation=rot,ha=ha)
    
    ims = 0
    for i,fnum in enumerate(fnum_list):
        ims = plot_v_fnum(ax,fnum,i+1,0.25,alpha)
    
    ax.set_aspect('auto')
    ax.legend(('mode','median','mean'),loc=loc)
    cbar = fig.colorbar(ims,orientation='vertical')
    plt.ylabel('compatibility score')
    plt.xlabel('compatibility level (fuzzy)')
    if (figfilename):
        plt.tight_layout()
        print 'saving fig {}'.format(figfilename)
        plt.savefig(figfilename,dpi=300)    
    plt.show()
    show()

