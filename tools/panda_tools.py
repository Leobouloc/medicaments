# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 16:39:30 2014

@author: work
"""

import numpy

def bind_and_plot(serie1, serie2, color_serie = '', describe = '', return_obj = False, return_ma = False, smooth_avr = None, xlabel = '', ylabel = '', title = ''):
    assert (not return_obj) or (not return_ma)   
    
    def movingaverage(interval, window_size):
        window= numpy.ones(int(window_size))/float(window_size)
        return numpy.convolve(interval, window, 'same')    
    def avr_in_window(x, step , test):
        selector = test.apply(lambda ligne: x-step/2 <= ligne['x'] and ligne['x']<x+step/2, axis = 1)
        avr = test.loc[selector, 'y'].mean()
        return(avr)
        
    test = pd.merge(pd.DataFrame(serie1), pd.DataFrame(serie2), left_index = True, right_index = True, how='inner')    
    test.dropna(inplace = True)
    if isinstance(color_serie, str):
        test.columns = ['x', 'y']
        test = test.sort('x')
        test = test[test['y'] != np.inf]
        plt.scatter(test['x'], test['y'])
        
        if smooth_avr != None:
            y_av = movingaverage(test['y'], smooth_avr)
            print y_av
            if return_ma:
                return([test['x'], y_av])
            plt.plot(test['x'], y_av, c = "r")
    else:
        test = pd.merge(test, pd.DataFrame(color_serie), left_index = True, right_index = True, how='inner')
        test.columns = ['x', 'y', 'z']
        test = test.sort('x')
        test = test[test['y'] != np.inf]
        plt.scatter(test['x'], test['y'], c = test['z'], s=40, lw = 0.1)
        plt.hot()
        
        if smooth_avr != None:
            y_av = movingaverage(test['y'], smooth_avr)
            plt.plot(test['x'], y_av,"r")      
            
            
            max_range = test['x'].max()
            step = max_range / smooth_avr
            x_curve = [step/2 + step * i for i in range(smooth_avr)]
            y_curve = [avr_in_window(x, step, test) for x in x_curve]
            plt.plot(x_curve, y_curve, "g") 
    

    plt.xlabel(xlabel)    
    plt.ylabel(ylabel)
    plt.title(title)
        
    if describe == 'describe':
        obj = test.groupby('0_x').describe()
    elif describe == 'mean':
        obj = test.groupby('0_x').mean()
    elif describe == 'min_max':
        obj = [test.groupby('0_x').min(), test.groupby('0_x').max()]
    elif describe == 'count':
        obj = test.groupby('0_x').count()
        
    if return_ma:
        plt.show()
        return
    
    if return_obj:
        plt.show()
        return obj
    elif describe != '':
        print obj
        plt.show()
    else:
        plt.show()
   
def panda_merge(*series):
    ''' est égal à reduce(series, pd.merge) ? '''
    test = pd.DataFrame(series[0])
    for i in range(1, len(series)):
        test = pd.merge(test, pd.DataFrame(series[i]), left_index = True, right_index = True, how='inner')
    return test
 
def dot_prod_series(a, b):
    b.index = a.index
    return a*b