# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 12:10:10 2014

@author: work
"""

import pandas as pd
import os
from CONFIG import path_BDM

#test.iloc[0].loc[~test.iloc[0,:].isnull()]

#[[i,test.iloc[2].loc[~test.iloc[2,:].isnull()].loc[i]] for i in test.iloc[2].loc[~test.iloc[2,:].isnull()].index]


def load_cnamts_prix_harmonise(force=False):
    file = os.path.join(path_BDM, 'BDM_PRIX_harmonise.csv')
    try:
        assert not force
        table = pd.read_csv(file, sep=',')
        return table
    except:
        table = load_cnamts_prix()
        table.to_csv(file, sep=',')
        return table

#Creation de la base harmonisée
def load_cnamts_prix():
    '''On obtient pour chaque CIP13 une liste de tuples Date // Prix qui correspond aux dates et changements de prix'''
    file = os.path.join(path_BDM, 'BDM_PRIX.csv')
    table = pd.read_csv(file, sep=';')
    table['PRIX_E'] = table['PRIX_E'].astype(float)/100
    table['date'] = table['DATE_APPLI'].apply(lambda x: x[6:10] + x[3:5])

    assert table.groupby(['date', 'CIP']).size().max() == 2
    one_value_per_month = table.sort(['date','PRIX_E']).groupby(['date', 'CIP']).last()
    one_value_per_month.reset_index(inplace=True)
    assert one_value_per_month.groupby(['date', 'CIP']).size().max() == 1

    table_per_date = one_value_per_month.pivot(index='CIP', columns='date', values='PRIX_E')

    # on veut une valeur par mois, sans trou, correspondant à la base SNIIRAM.
    cols = table_per_date.columns
#    debut = min(cols)
#    fin = max(cols)
    # 138 correspond à la longeur de 'period', nombre de mois dans la base sniiram
    period_sniiram = ['20'+"%02.f"%x+"%02.f"%y for x in range(3,15) for y in range(1,13)][:138]
    output = pd.DataFrame(index=table_per_date.index, columns=period_sniiram)
    for period in period_sniiram:
        if period in cols:
            output[period] = table_per_date[period]
    # TODO: beaucoup plus beau: ajouter des colonnes à table_per_date, puis
    # réordonner, ça évite de ré-écrire une table

    output.dropna(how='all', inplace=True)  # output.index == 3400926606053
    # TODO: voir si mise à jour, sinon mettre le prix à la main
    # FAB_HT_E = 18000.000 et PRIX_E = 19521.80, DATE_APPLI = 26/11/2014

    output = output.fillna(method='ffill', axis=1)
    output = output.fillna(method='bfill', axis=1)

#    new_names_cols = ['prix_' + str(x) for x in output.columns]
#    output.columns = new_names_cols
    output.reset_index(inplace=True)
    #On rend les colonnes compatibles avec 'period'
    output.columns = ['CIP'] + ['prix_' + x for x in output.columns[1:]]
    return output
