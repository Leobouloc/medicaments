#-*- coding: utf-8 -*-
'''
Created on 26 juin 2014
'''
# from __future__ import unicode_literals

import pandas as pd
import os
from pdb import set_trace

from CONFIG import path_sniiram


def add_date_vente_observee(sniiram):
    # Pour chaque médicament on détermine l'année de la première vente :
    # Determiner les dates de premieres ventes
    periods = sniiram.columns
    assert all(periods == sorted(periods))
    # TODO: change periods in string
    premiere_vente = pd.Series(index=sniiram.index)
    derniere_vente = pd.Series(index=sniiram.index)
    for month in periods:
        vente = sniiram[month] > 0
        cond_prem = vente & premiere_vente.isnull()
        premiere_vente[cond_prem] = month
        cond_dern = ~vente & premiere_vente.notnull() & derniere_vente.isnull()
        derniere_vente[cond_dern] = month - 1

    # Ajout de la donnée première vente à la base Sniiram
    sniiram['premiere_vente'] = premiere_vente
    sniiram['derniere_vente'] = derniere_vente
    return sniiram


def load_sniiram(date=200301):
    assert date in [200301, 201003, 201012]
    path = os.path.join(path_sniiram, 'since' + str(date) + '.csv')
    table = pd.read_csv(path, sep=';')
    table.columns = ['date', 'cip13', 'nb']
    table['nb'] *= 97
    table['year'] = table['date'] // 100
    table['cip13'].fillna(1, inplace=True)
    table = table.pivot(index='cip13', columns='date', values='nb')
    return add_date_vente_observee(table)

def load_sniiram2():
    table = pd.read_csv(path_sniiram + 'PHARMA2.csv', sep=';')
    table.columns = ['cip13', 'date', 'nb','caisse','typ_presta']
    table['nb'] *= 97
    table['year'] = table['date']//100
    table['cip13'].fillna(1, inplace=True)
    table.groupby(['date','caisse'])['nb'].sum()
    #ajout des nouvelles caisses :
    table.groupby(['date','caisse'])['nb'].sum().loc[201012] - table.groupby(['date','caisse'])['nb'].sum().loc[201010]


    def presta_unique(group):
        if group['typ_presta'].min() == group['typ_presta'].max():
            return group['typ_presta'].max()
        return 0
    set_trace()
    test['deb_cip'] = table['cip13'] // 100000000
    table[table['deb_cip'] != 34009].head(30)
    particular_cip = table[table['deb_cip'] != 34009]
    part = particular_cip
    test = table.groupby(['cip13']).apply(presta_unique)
    table.groupby(['date','caisse'])

    table = table.pivot(index='cip13', columns='date', values='nb')
    #TODO: redresser après 2011
    return add_date_vente_observee(table)

if __name__ == '__main__':
    table = load_sniiram()
    #set_trace()
#    print(table.loc[ table['cip13'] == 3400934917547].groupby('year').sum())
#    table.set_index('cip13', inplace=True)
#    
#    table.loc[ table['cip13'] == 3400934917547].groupby('cip13')['nb'].sum()
    
# test = table.sum(axis=1)
# test[test.index==9999999999999] / test.sum()
# test[test.index==1] / test.sum()