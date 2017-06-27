# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 13:47:43 2015

@author: Alexis Eidelman
"""

import os
from sas7bdat import SAS7BDAT
import pandas as pd
from numpy import int64

path = 'D:/data/Medicament/cnamts'
path_csv = os.path.join(path, 'base_sas_en_csv.csv')

#path_sas = os.path.join(path, 'medicaments2014v3.sas7bdat')
#with SAS7BDAT(path_sas) as f:
#    f.convert_file(path_csv, delimiter='\t')


brut = pd.read_csv(path_csv, sep ='\t')

# Correction sur brut
sans_date = brut[brut.EXE_SOI_AMD.isnull()]
assert all((sans_date.isnull()) | (sans_date == 0))
brut = brut[brut.EXE_SOI_AMD.notnull()]

brut['CIP'] = brut['PHA_PRS_C13'].astype(int64).astype(str)
brut.drop('PHA_PRS_C13', axis=1, inplace=True)
brut['PSP_SPE_COD'] = brut['PSP_SPE_COD'].astype(int)

correspondance = brut.groupby(['PSP_SPE_COD', 'PFS_SPE_LIB']).size()
correspondance = pd.DataFrame(correspondance).reset_index()
correspondance.drop(0, axis=1, inplace=True)
correspondance.to_csv(os.path.join(path, 'dico_SPE.csv'), sep ='\t', index=None)


# ça prend un peu de temps mais c'est vrai
#assert brut.groupby(['PHA_PRS_C13'])['PHA_MED_NOM'].nunique().max() == 1
#assert brut.groupby(['PHA_PRS_C13'])['PHA_ATC_C03'].nunique().max() == 1

medicament =  brut.groupby(['CIP','PHA_MED_NOM', 'PHA_ATC_C03']).size()
medicament = pd.DataFrame(medicament).reset_index()
medicament.drop(0, axis=1, inplace=True)
medicament.to_csv(os.path.join(path, 'dico_medicament.csv'), sep ='\t', index=None)


tab = brut[['EXE_SOI_AMD', 'Dept_ben', 'CIP', 'PSP_SPE_COD', 'QUANTITE']]
tab.columns = ['date', 'dep', 'CIP', 'PSP_SPE_COD', 'qte']

for col in tab.columns:
    print tab[col].isnull().value_counts()

for col in ['date', 'dep', 'PSP_SPE_COD', 'qte']:
    assert all(tab[col].notnull())
    # tab[col].fillna(0, inplace=True)
    tab[col] = tab[col].astype(int)

tab.to_csv(os.path.join(path, 'base.csv'), index=False)
