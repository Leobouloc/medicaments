# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 13:56:00 2014

@author: work
"""


import os
import pandas as pd

from CONFIG import path_atc_ddd

info_dispo = ['CODE_ATC', 'ANATOMICAL_MAIN_GROUP', 'THERAPEUTIC_SUBGROUP', 'PHARMACOLOGICAL_SUBGROUP',
              'CHEMICAL_SUBGROUP', 'CHEMICAL_SUBSTANCE', 'DDD', 'UNITE', 'MODE', 'NOTE']

def load_atc_ddd(info_utile):
    print 'Actuellement dans load_atc_ddd'
    path = os.path.join(path_atc_ddd, "atc-ddd.csv")
    tab = pd.read_table(path, header=False, sep = ';')
    tab.columns = info_dispo
    tab = tab.loc[:, info_utile]
    tab = tab[tab['DDD'].notnull()]
    tab.loc[tab['UNITE'] == 'mg', 'UNITE'] = 'MG'
    tab.loc[tab['UNITE'] == ' g', 'DDD'] *= 1000
    tab.loc[tab['UNITE'] == ' g', 'UNITE'] = 'MG'
#    tab = tab.apply(recode_ligne, axis=1)
    return tab

#def recode_ligne(ligne):
#    if ligne['UNITE'] == 'mg':
#        ligne['UNITE'] = 'MG'
#    elif ligne['UNITE'] == 'g':
#        ligne['UNITE'] = 'MG'
#        ligne['DDD'] *= 1000
#    return ligne


if __name__ == '__main__':
    info_utile = ['CODE_ATC', 'CHEMICAL_SUBSTANCE', 'DDD', 'UNITE', 'MODE']
    test = load_atc_ddd(info_utile)