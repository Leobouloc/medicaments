# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 16:27:10 2014

@author: work
"""

import os
from CONFIG import path_asmr_eculape as path

def load_eculape(path):
    file = os.path.join(path, 'asmr.xlsx')
    table_entiere = pd.read_excel(file, 0)
    return table_entiere
    
def asmr_try(x, test3):
    for i in test3.index:
        if i in x['Nom_Substance']:
            return(test3[i])
    return np.nan
    
    
if __name__ == '__main__':
    test = load_eculape(path)
    test['Nom_court'] = test['Nom'].apply(lambda x: x.split()[0])
    selector = test.groupby('Nom_court')['ASMR'].nunique()
    test2 = test[test.apply(lambda x: selector[x['Nom_court']] == 1, axis = 1)]
    test3 = test2.groupby('Nom_court').apply(lambda  x: x['ASMR'].iloc[0])
    base_brute['ASMR'] = base_brute.apply(lambda x: asmr_try(x, test3), axis = 1)
    