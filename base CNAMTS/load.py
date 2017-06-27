# -*- coding: utf-8 -*-
"""
Created on Mon May 04 17:53:41 2015

@author: Alexis Eidelman
"""
import os
import pandas as pd


path = 'D:/data/Medicament/cnamts'
path_file = os.path.join(path, 'base.csv')

base = pd.read_csv(path_file)

## on va chercher le labo
from load_data.medic_gouv import *
# TODO: il peut y avoir plusieurs titulaires
titulaire = load_medic_gouv(var_to_keep=['CIP', 'Titulaires'])
titulaire.drop('CIS', axis=1, inplace=True)

test = base.merge(titulaire, how='left')

## test
cadeaux = pd.read_csv(os.path.join(path, 'labos.departements.csv'))

#TODO: virer ce fucking espace
cad_sandoz = cadeaux[cadeaux['LABO'] == 'SANDOZ']
sandoz = test[test['Titulaires'] == ' SANDOZ']

# TODO: virer les génériques !

# TODO: pas tellement besoin du merge parce qu'on n'a pas de date pour l'instant
sandoz = sandoz.merge(cad_sandoz, left_on='dep', right_on='DEPARTEMENT')
# sandoz.CIP.value_counts()
# on regarde un medicamment :
cip = '3400939541778'
un_cip = sandoz[sandoz['CIP'] == cip]

## TODO: faire un beau truc avec des groupby
#dates = un_cip.date.unique().tolist()
#dates.sort()
#deps = un_cip.dep.unique().tolist()
#deps.sort()
#for dep in deps:
#    tab_dep = un_cip[un_cip['dep'] == dep]
#    tab_dep[].plot