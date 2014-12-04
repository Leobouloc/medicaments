# -*- coding: utf-8 -*-
"""
Created on Thu Dec 04 10:37:16 2014

@author: work
"""
   
import math   
   
def lambda_float(x):
    try:
        return float(x)
    except:
        return np.nan
        
def sel_by_dosage_value(table):
    '''Sensé selectionner les CIP dont les dosages sont des nombres ronds '''
   dosage = table['Dosage']
   if dosage.notnull().all():
        dosage = dosage.str.split().apply(lambda x: x[0]).apply(lambda_float)
        dosage = dosage[dosage.notnull()]
        dosage = dosage[dosage != 0]
        max_val = dosage.max()
        min_val = dosage.min()
        '''Renvoie True si tous les dosages sont définis et si l'écart relatif max au sein de la série est inférieur à 0,3'''
        if (float(max_val) / float(min_val) < 1.3) & dosage.notnull().all() and ((dosage == 0).sum() == 0) :
            n = dosage.apply(lambda x: round(math.log(x, 10)))
            dosage = dosage / n.apply(lambda x: 10**x)
            for i in range(3):
                test = dosage == dosage.apply(round)
                if (test.sum()) == 1:
                    return test
                else:
                    dosage = 10 * dosage
   return pd.Series(False, index = dosage.index)
            
    