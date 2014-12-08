# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 13:56:00 2014

@author: work
"""


import os
import pandas as pd

from CONFIG import path_atc_ddd

rename_vars = {'Chemical Substance': 'CHEMICAL_SUBSTANCE',
               'Anatomical Main Group': 'ANATOMICAL_MAIN_GROUP',
               'Adm.R': 'MODE',
               'Therapeutic Subgroup': 'THERAPEUTIC_SUBGROUP',
               'Pharmacological Subgroup': 'PHARMACOLOGICAL_SUBGROUP',
               'Note': 'NOTE',
               'ATC code': 'CODE_ATC',
               'U': 'UNITE',
               'Chemical Subgroup': 'CHEMICAL_SUBGROUP',
               'DDD': 'DDD'}

def load_atc_ddd(info_utile, brut=False):
    print 'Actuellement dans load_atc_ddd'
    path = os.path.join(path_atc_ddd, "atc-ddd.csv")
    tab = pd.read_table(path, header=False, sep = ';')
    tab.rename(columns=rename_vars, inplace=True)
    tab = tab.loc[:, info_utile]
    tab = tab[tab['DDD'].notnull()]
    tab.loc[tab['UNITE'] == 'mg', 'UNITE'] = 'MG'
    tab.loc[tab['UNITE'] == 'g', 'DDD'] *= 1000
    tab.loc[tab['UNITE'] == 'g', 'UNITE'] = 'MG'
    tab.loc[tab['UNITE'] == 'mcg', 'DDD'] /= 1000
    tab.loc[tab['UNITE'] == 'mcg', 'UNITE'] = 'MG'
#    tab = tab.apply(recode_ligne, axis=1)
    if brut:
      return tab
      
    prob = tab.groupby(['CODE_ATC', 'MODE', 'UNITE']).filter(lambda x: len(x) > 1)
    # les problèmes viennent des NOTE. On a :
    #    assert tab.groupby(['CODE_ATC', 'MODE', 'UNITE', 'NOTE']).size().max() == 1
    # TODO: traiter "manuellement" ces cas
    tab_out = tab.groupby(['CODE_ATC', 'MODE', 'UNITE'])['DDD'].mean().reset_index()
    assert tab_out.groupby(['CODE_ATC', 'MODE', 'UNITE']).size().max() == 1
    # TODO: comprendre pourquoi, on a plusieurs unité
    prob = tab_out.groupby(['CODE_ATC', 'MODE']).filter(lambda x: len(x) > 1)
    assert tab_out.groupby(['CODE_ATC', 'MODE']).size().max() == 1
    others_var = tab[['CODE_ATC', 'MODE', 'UNITE']  + [x for x in info_utile if
                    x not in tab_out.columns]]
    tab_out = tab_out.merge(others_var, on=['CODE_ATC', 'MODE', 'UNITE'])
    return tab_out

if __name__ == '__main__':
    info_utile = ['CODE_ATC', 'CHEMICAL_SUBSTANCE', 'DDD', 'UNITE', 'MODE']
    test = load_atc_ddd(info_utile, brut=True)

    cond = test.CHEMICAL_SUBSTANCE.str.contains('statin')
    cond[cond.isnull()] = False
    test[cond]

    test.groupby(['CODE_ATC', 'MODE', 'CHEMICAL_SUBSTANCE']).size().value_counts()
    # => 19 groupes ont deux substances
    
    prob = test.CHEMICAL_SUBSTANCE.isnull()