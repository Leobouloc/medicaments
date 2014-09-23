#-*- coding: utf-8 -*-
'''
Created on 26 juin 2014
'''
# from __future__ import unicode_literals

import pandas as pd
import os
from pdb import set_trace

from CONFIG import path_sniiram


def load_sniiram():
    path = os.path.join(path_sniiram, 'PHARMA.csv')
    table = pd.read_csv(path, sep=';')
    table.columns = ['cip13', 'date', 'nb']
    table['nb'] *= 97
    table['year'] = table['date']//100
    table['cip13'].fillna(1, inplace=True)
    table = table.pivot(index='cip13', columns='date', values='nb')
    # TODO: redresser après 2011
    return table

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
    return table

if __name__ == '__main__':
    table = load_sniiram()
    #set_trace()
    print(table.loc[ table['cip13'] == 3400934917547].groupby('year').sum())
    table.set_index('cip13', inplace=True)
    
    table.loc[ table['cip13'] == 3400934917547].groupby('cip13')['nb'].sum()
    
# test = table.sum(axis=1)
# test[test.index==9999999999999] / test.sum()
# test[test.index==1] / test.sum()