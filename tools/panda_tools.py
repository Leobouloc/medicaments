# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 16:39:30 2014

@author: work
"""

import numpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier


def all_info(table):
    '''n affiche que les colonnes non vides que l'on connait'''
    cols_to_show = [col for col in table.columns if table[col].notnull().any()]
    print (table[cols_to_show])
    
def grp_and_count(table, group, function):
    a = table.groupby(group).apply(function)
    b = table.groupby(group).apply(len)
    c = panda_merge(a, b)
    c.columns = ['a', 'b']
    c = c.sort('a')
    return c

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
    print str(len(test)) + ' points'
    if isinstance(color_serie, str):
        test.columns = ['x', 'y']
        test = test.sort('x')
        test = test[test['y'] != np.inf]
        plt.scatter(test['x'], test['y'], alpha = 0.1)
        
        if smooth_avr != None:
            y_av = movingaverage(test['y'], smooth_avr)
#            print y_av
#            if return_ma:
#                return([test['x'], y_av])
            plt.plot(test['x'], y_av, c = "r")
    else:
        test = pd.merge(test, pd.DataFrame(color_serie), left_index = True, right_index = True, how='inner')
        test.columns = ['x', 'y', 'z']
        test = test.sort('x')
        test = test[test['y'] != np.inf]
        plt.scatter(test['x'], test['y'], c = test['z'], s=40, lw = 0.1, alpha = 0.1)
        plt.hot()
        
        if smooth_avr != None:
            y_av = movingaverage(test['y'], smooth_avr)
            plt.plot(test['x'], y_av,"r")      
            
            
#            max_range = test['x'].max()
#            step = max_range / smooth_avr
#            x_curve = [step/2 + step * i for i in range(smooth_avr)]
#            y_curve = [avr_in_window(x, step, test) for x in x_curve]
#            plt.plot(x_curve, y_curve, "g") 
    

#    plt.xlabel(xlabel)    
#    plt.ylabel(ylabel)
#    plt.title(title)
#        
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


def rem_whspc(table):
    def _rem_whspc(x):
        if isinstance(x, str) or isinstance(x, unicode):
            if '' == x.replace(' ', ''):
                return np.nan
        return x
    return table.applymap(_rem_whspc)

def completness(table):
    '''Shows proportion of non null and whitespace strings'''
    table = rem_whspc(table)
    a =  table.apply(lambda x: x.notnull().sum() / float(len(x)))
    b = table.apply(lambda x: x.nunique())
    ret = panda_merge(a, b)
    ret.columns = ['not_null', 'nunique']
    print ret
    print 'This table has : ' + str(len(table)) + ' lines'
    
    
#####
def make_forest(train, a_predire_col, pour_predire_cols):
    '''Utilise les random forest de Sklearn pour predire la colonne a_predire de test par les features pour_predire_cols'''
    a_predire = list(train[a_predire_col])
    pour_predire_train = [list(x)[1:] for x in list(train[pour_predire_cols].itertuples())]
    forest = RandomForestClassifier(n_estimators=40, criterion='entropy', max_depth=None, min_samples_split=4, min_samples_leaf=2, max_features='auto', max_leaf_nodes= None, bootstrap=True, oob_score=False, n_jobs=1, random_state=None, verbose=0, min_density=None, compute_importances=None)
    forest.fit(pour_predire_train, a_predire)
    return forest
    
def use_forest(forest, test, pour_predire_cols):
    pour_predire_test = [list(x)[1:] for x in list(test[pour_predire_cols].itertuples())]
    prediction = forest.predict(pour_predire_test)
    return prediction