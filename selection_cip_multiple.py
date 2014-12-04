# -*- coding: utf-8 -*-
"""
Created on Thu Dec 04 10:37:16 2014

@author: work
"""
   
import math
from pandas import Series

def lambda_float(x):
    try:
        return float(x)
    except:
        return np.nan
        
def sel_by_dosage_value(table):
    '''Sensé selectionner les CIP dont les dosages sont des nombres ronds '''
    dosage = table['Dosage']
    if dosage.notnull().all():
        # On prend la valeure numérique du dosage
        
        dosage = dosage.str.split().apply(lambda x: x[0]).apply(lambda_float)
        # On vérifie que tous les dosages sont bien définis et non nulls
        if dosage.notnull().all() and (dosage != 0).all():
            max_val = dosage.max()
            min_val = dosage.min()
            # On s'assure que l'écart relatif maximal est faible
            if (float(max_val) / float(min_val)) < 1.3:
                # On récupere la puissance de dix de chaque dosage en nottation scientifique
                n = dosage.apply(lambda x: 10**(math.floor(math.log(x, 10))))
                # On récupère la première partie de la notation scientifique
                dosage = dosage / n
                for i in range(3):
                    test = dosage == dosage.apply(round)
                    # Si on a une unique ligne pour laquelle le dosage est nul on renvoie 
                    if (test.sum()) == 1:
                        return test
                    else:
                        dosage = 10 * dosage
    return pd.Series(False, index = dosage.index)
    

dose = dosage.str.split().str.get(0)
dose = dose.apply(lambda_float)

max_power = int(math.floor(math.log(max(dose), 10)))
min_power = int(math.floor(math.log(min(dose), 10)))
power = Series(min_power - 1, index=dose.index)
for i in range(min_power, max_power + 1):
    divide = 10**(i)
    cond = dose/divide == (dose/divide).apply(math.floor)
    power[cond] = i

table['power'] = power

table.groupby('CIP')['power'].min()





