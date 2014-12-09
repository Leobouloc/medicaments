# -*- coding: utf-8 -*-
"""
Created on Mon Dec 08 17:02:52 2014

@author: work
"""

import pandas as pd
voyelles = ['A', 'E', 'I', 'O', 'U', 'Y', 'É', '\xc9', "D'", '\xca', 'Ê', ' ']

def fuzzy_join(left_table, right_table):
    '''la table de gauche doit être un groupe de même CIP'''
    '''celle de droite est atc_ddd'''
    left_substances = pd.Series(left_table['Nom_Substance'].unique())
    code_atc = left_table['CODE_ATC'].iloc[0]
    right_table_small = right_table[right_table['CODE_ATC'] == code_atc]
    right_substances = right_table_small['CHEMICAL_SUBSTANCE'].str.upper()
    
    
    if (len(right_substances) != 1) | left_substances.isnull().any():
        return pd.Series(False, index = left_table.index)

    else:
        right_substance = right_substances.iloc[0]
        left_substances = left_substances.astype(str)
        for voy in voyelles:
            left_substances = left_substances.str.replace(voy, '')
            right_substance = right_substance.replace(voy, '')
        select_by_subst_name = left_substances == right_substance
        if select_by_subst_name.sum() == 1:
#            print "XXX"
#            print left_substances
#            print right_substance      
            return select_by_subst_name
            
        else:
            return pd.Series(False, index = left_table.index)


def fuzzy_join_bis(table):
    '''la table de gauche doit être un groupe de même CIP'''
    '''celle de droite est atc_ddd'''
    substance_ddd = table['CHEMICAL_SUBSTANCE'].str.upper()
    substance = table['Nom_Substance']
    
    for voy in voyelles:
        substances_ddd = substance_ddd.str.replace(voy, '')
        substance = substance.replace(voy, '')
            
    select_by_subst_name = substances == substances_ddd