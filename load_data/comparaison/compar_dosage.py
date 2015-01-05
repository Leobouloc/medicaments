# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 11:54:31 2014

@author: aeidelman
"""

import os
import pandas as pd

from CONFIG import path_BDM

from load_data.bdm_from_scrap import bdm_scrap
from load_data.bdm_cnamts import bdm_cnamts
from load_data.medic_gouv import load_medic_gouv, table_update

from CONFIG import path_BDM_scrap
from load_data.bdm_cnamts.get_bdm import load_cip



info_utiles = ['CIP', 'CIP7', 'CIP_UCD', 'NATURE', 'NOM_COURT', 'INDIC_COND',
                          'DEBUT_REMB', 'FIN_REMB', 'CODE_LISTE', 'CODE_FORME', 'FORME',
                          'CODE_CPLT', 'CPLT_FORME', 'DOSAGE_SA', 'UNITE_SA', 'NB_UNITES',
                          'CODE_ATC', 'CLASSE_ATC', 'CODE_EPH', 'CLASSE_EPH', 'LABO',
                          'NOM_LONG1', 'NOM_LONG2', 'SUIVI', 'DATE_EFFET', 'SEUIL_ALER',
                          'SEUIL_REJE', 'PRESC_REST', 'EXCEPTIONS', 'TYPE', 'SEXE',
                          'INTERACT', 'PIH', 'PECP']

#bdm = bdm_cnamts(info_utiles_from_cnamts)
#path = os.path.join(path_BDM, "BDM_CIP.xlsx")
#table_entiere = pd.read_excel(path, 0)
#bdm = table_entiere.loc[:, info_utiles]
#bdm['CIP'] = bdm['CIP'].astype(str)

gouv = load_medic_gouv(var_to_keep=['CIP7', 'CIP', 'Label_presta',
                'Element_Pharma', 'Code_Substance', 'Nom_Substance',
                'Dosage', 'Ref_Dosage', 'Nature_Composant',
                'Date_AMM', 'Statut_BDM', 'Num_Europe', 'Titulaires'])
scrap = bdm_scrap()


gouv['Dosage'] = gouv['Dosage'].str.replace('mg', 'MG')
gouv['Dosage'] = gouv['Dosage'].str.replace(',', '.')


print scrap['CIP'].nunique()
print gouv['CIP'].nunique()

compar = gouv.merge(scrap, on='CIP')
print compar['CIP'].nunique()

# TODO:
# Regarder les différences de présence dans les tables
pas_dans_scrap = gouv['CIP'][~gouv['CIP'].isin(scrap['CIP'])].unique()
pas_dans_gouv = scrap['CIP'][~scrap['CIP'].isin(gouv['CIP'])].unique()
print len(pas_dans_gouv)
print len(pas_dans_scrap)

pas_scrap = gouv[gouv['CIP'].isin(pas_dans_scrap)]
print pas_scrap['CIP'].nunique()

for cip in pas_dans_scrap[:-1]:
    load_cip(cip, 'cip')


# test d'homogénéité
sum(compar['CODE_ATC'] != compar['code_atc'])
probleme_atc = compar[compar['CODE_ATC'] != compar['code_atc']]
#probleme_atc['CODE_ATC'].value_counts() => beacuoup de na
vrai_diff_atc = probleme_atc[probleme_atc['CODE_ATC'].notnull()]
# => on a des différences de CIP pour trois CIP !
compar.drop(['CODE_ATC', 'code_atc'], axis=1, inplace=True)

sum(compar['CIP7'] != compar['CIP_7'])
compar.drop(['CIP7', 'CIP_7'], axis=1, inplace=True)



#compar['designation']  compar['NOM_LONG1']

active = compar.loc[compar['substance_active'].notnull(),
           ['CIP', # 'Code_Substance', 'Nom_Substance',
                'Dosage', 'Ref_Dosage', 'Nature_Composant', 'dosage', 'dosage_base']]

select_une_substance = active.groupby('CIP').filter(lambda x : len(x) == 1)
active = select_une_substance
active['DOSAGE_SA_ini'] = active['DOSAGE_SA_ini'].str.replace('mg', 'MG')
active['DOSAGE_SA_ini'] = active['DOSAGE_SA_ini'].str.replace(',', '.')
active['test'] = active['DOSAGE_SA'] + ' ' + active['UNITE_SA']
test1 = (active['test'] == active['dosage'])
test2 = (active['test'].str.replace(',', '.') == active['dosage'])

#test2 = (active['test'].str.replace('0 ', ' ') == active['dosage'])
#test3 = (active['test'].str.replace('.0 ', ' ') == active['dosage'])
#test4 = (active['test'].str.replace('.00 ', ' ') == active['dosage'])
#test5 = (active['test'].str.replace('nan', 'NON RENSEIGNE') == active['dosage'])
#test6 = (active['test'] == active['dosage'].str.replace('0 ', ' '))


test = test1 | test2 # | test3 | test4 | test5 | test6
prob = active[~test]

element = prob['test'].isnull() | prob['test'].str.contains('\/')
prob[~element]


# Cnam a 16695 ligne
# Gouv en a 22752
# all en a 11439

# explications: que pas que des médicaments dans gouv,
# une ligne par substance dans gouv
# les vieux médicaments ne sont pas dans gouv
all = gouv.merge(cnam)
all['dosage_gouv'] = table_update(all)

# différence
diff = all[all['dosage_gouv'] != all['unites_par_boite']]
diff_SA = diff[diff['Nature_Composant'] == 'SA']