# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 12:31:43 2017

http://www.data.gouv.fr/fr/datasets/open-phmev-bases-sur-les-prescriptions-hospitalieres-de-medicaments-delivrees-en-ville/
http://open-data-assurance-maladie.ameli.fr/medicaments/index.php#Open_PHMEV
"""

import pandas as pd

path_file = "D:\data\OPEN_PHMEV_2015.CSV"

tab = pd.read_csv(path_file, encoding='cp1252', sep=';',
                  )
tab.rename(columns={'l_atc1': 'L_ATC1',
                    'ATC5': 'atc5'}, inplace=True)

# OK
#for k in range(1, 6):
#    all(tab.groupby(['atc' + str(k)])['L_ATC' + str(k)].nunique() == 1)
#    if k > 1:
#        tab_rempli = tab.loc[tab['atc' + str(k)].astype(str) != (k+1)*"9"]
#        all(tab_rempli.groupby(['atc' + str(k)])['L_ATC' + str(k - 1)].nunique() == 1)
# =>
#tab.drop(['L_ATC' + str(k) for k in range(1, 6)], axis=1, inplace=True)


var_etb = ['raison_sociale_etb', 'nom_voie', 'nom_ville',
           'categorie_jur', 'code_postal', 'nom_etb', 'numero_voie',
           'region_etb', 'top_etb_sexe', 'top_etb_age']
etb = tab[var_etb + ['etb_rgt']].drop_duplicates()
# on a un truc pour les centres hospitaliers :
etb[etb['raison_sociale_etb'] == 'CENTRE HOSPITALIER']
# TODO: ajouter le nom de la ville
for var in []:
    assert all(etb.groupby(['etb_rgt'])[var].nunique() <= 1)
# =>
#tab.drop(var_etb, axis=1, inplace=True)

tab.drop(['L_ATC' + str(k) for k in range(1, 6)], axis=1, inplace=True)
tab.drop(var_etb, axis=1, inplace=True)


tab.to_csv("D:\data\OPEN_PHMEV_2015.csv",
           index=False, encoding='utf8')