# -*- coding:cp1252 -*-
'''
Created on Thu Aug 25

@author: aeidelman

lit les bases PMF et donne des résultats agrégé qui peuvent être exploités.
-> on crée une base CIP x tranche de 5 minutes de vente.
->
'''
import os
import numpy as np
import pandas as pd
import pdb
import datetime as dt
import gc
import matplotlib.pyplot as plt

path = "D:\\data\\tbl-ctpm-140820-donnes-brutes-jlr"



dates = [100*year + month + 1
         for year in range(2009, 2014)
         for month in range(12)]

k = 0

test = '2009-02-13 14:59:00.000'


def parser(x):
    return pd.datetime.strptime(x, "%Y-%m-%d %H:%M:%S.000" )

all_tab = dict()
all_tab = None

len_totale = dict( (name, 0) for name in ['temp_cip', 'pharm_temp', 'tot',
                                          'pharma_temp_cip', 'by_day', 'pharma_cip'])

for k, date in enumerate(dates):
    print (k, date)
    name_file = "TBL-CTPM 140820 Données tickets " + str(date) + "_JLR.csv"
    path_file = os.path.join(path, name_file)
    temp = pd.read_csv(path_file, sep=';', engine='c', header=None,
                       usecols=[1,2,4,5,6], names=['pharma', 'date', 'CIP', 'prix', 'qte'],
                       decimal=',', #parse_dates=['date'], date_parser=parser
                       )
    temp['Date'] = temp['date'].apply(parser)
    temp.drop(['date'], axis=1, inplace=True)
    temp['minute'] = temp['Date'].dt.minute
    temp['hour'] = temp['Date'].dt.hour
    temp['day'] = temp['Date'].dt.day
    temp['day'] = temp['Date'].dt.day
    temp['day'] = temp['Date'].dt.day

    temp['minute_of_day'] = (60*temp['hour'] + temp['minute'])/60
#    temp['Date'].dt.minute.value_counts()
#    temp['Date'].dt.hour.value_counts()
#    temp['minute_of_day'].value_counts()
    # TODO: savoir pourquoi on a beaucoup de truc qui sont à 1 minute

    assert all(100*temp['Date'].dt.year + temp['Date'].dt.month == date)
    print ('la base du mois ' + str(date) + ' a initialement : ' + str(len(temp)) + ' lignes')
    if temp['prix'].min() < 0:
        print 'probleme de prix négatif'
        temp['prix'] = temp['prix'].abs()

    try:
        temp['prix'] = (100*temp['prix']).astype(np.int32)
#        temp['CIP'] = temp['CIP'].astype(np.int32)
        temp['qte'] = temp['qte'].astype(np.int16)
        temp['pharma'] = temp['pharma'].astype(np.int16)
        assert temp['prix'].min() >= 0
#        assert temp['CIP'].min() > 0
        # on a des valeurs négatives non-aberrantes dans qte

        assert temp['pharma'].min() > 0
    except:
        print("oups")
        pdb.set_trace()


# en gardant l'info par pharmacie, on arrive presque à avoir toutes les dates
     # on considère que le ticket n'a pas d'importance alors on regroupe les données par prix par pharmacie et par médicament :
     # le groupby permet de réduire la taille de la base
    dic_groupby = {
                   'temp_cip': ['CIP', 'Date'],
                   'pharm_temp': ['pharma', 'Date'],
                   'pharma_temp_cip': ['CIP', 'Date', 'pharma'],
                   'by_day': ['CIP', 'pharma', 'day', 'month', 'year']
                    }

    for ext_name in ['temp_cip', 'pharm_temp', 'pharma_temp_cip', 'pharma_cip']:
        path_out = os.path.join(path, ext_name)
        if not os.path.exists(path_out):
             os.makedirs(path_out)
        name = os.path.join(path_out, name_file)
        if not os.path.exists(name):
            table = temp.groupby(dic_groupby[ext_name]['qte'].sum())
            eval(ext_name).to_csv(name)
            print ext_name, len(eval(ext_name))
            len_totale[ext_name] += len(eval(ext_name))
            del table

    len_totale['tot'] += len(temp)
    del temp
    gc.collect()


# file_prix_qte = (path + "prix_qte.csv").decode('utf-8').encode('cp1252')
# all_tab.to_csv(file_prix_qte)
# file_prix_qte = (path + "prix_qte.h5").decode('utf-8').encode('cp1252')
# all_tab.to_hdf(file_prix_qte, 'base')

#if __name__ == '__main__':


# => len_total :
#    {'pharm_temp': 187460357,
#     'pharma_cip': 65740505,
#     'by_day': 0,
#     'temp_cip': 170982172,
#     'pharma_temp_cip': 255146039,
#     'tot': 259043997}