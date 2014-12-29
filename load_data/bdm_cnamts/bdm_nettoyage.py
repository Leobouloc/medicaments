# -*- coding: utf-8 -*-
"""
Created on Mon Dec 29 18:29:49 2014

@author: work
"""

from CONFIG import path_BDM_scrap
from CONFIG import path_BDM




def column_clean(x):
    x = x.replace('\xc3\x83\xc2\xa9', 'e')
    x = x.replace(' ', '_')
    x = x.replace(':', '')
    x = x.strip('_')
    if not 'CIP' in x:
        x = x.lower()
    return x
    
def classe_atc(table):
    '''Parse de la colonne originale classe_atc'''
    if 'classe_atc' in table.columns:
        atc_col = table.classe_atc
        atc_col = atc_col.str.split(' - ')
        table['code_atc'] = atc_col.apply(lambda x: x[0])
        table['nom_atc'] = atc_col.apply(lambda x: x[1])
        table.drop('classe_atc', axis = 1, inplace = True)
    else:
        print 'la colonne classe_atc n existe pas'
        
    return table

file = os.path.join(path_BDM_scrap, 'without_prob_with_dose.csv')
table = pd.read_csv(file)

columns_to_drop = [col for col in table.columns if 'Unnamed' in col] + ['active'] + ['cas']
table.drop(columns_to_drop, axis = 1, inplace = True)
table.columns = [column_clean(col) for col in table.columns]


table = classe_atc(table)

### print le ratio de completude de chaque colonne (par CIP)
#grp = table.groupby('CIP')
#nb_cip = table.CIP.nunique()
#for col in table.columns:
#    ratio = grp[col].apply(lambda x: x.notnull().any()).sum()/ float(nb_cip)
#    print str(col) + ' : ' + str(ratio)