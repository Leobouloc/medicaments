# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 11:54:31 2014

@author: aeidelman
"""

import pdb
import math

from load_data.bdm_cnamts import bdm_cnamts
from load_data.medic_gouv import load_medic_gouv, table_update, extract_quantity

gouv = load_medic_gouv(var_to_keep=['CIP7', 'Label_presta',
                'Element_Pharma', 'Code_Substance', 'Nom_Substance',
                'Dosage', 'Ref_Dosage', 'Nature_Composant'])
cnam = bdm_cnamts(['CIP', 'CIP7','DOSAGE_SA', 'UNITE_SA', 'NOM_LONG1'])


# Cnam a 16695 ligne
# Gouv en a 22752
# all en a 11439

# explications: que pas que des médicaments dans gouv,
# une ligne par substance dans gouv
# les vieux médicaments ne sont pas dans gouv
all = gouv.merge(cnam, how='outer')
all['resolu'] = 0
res = all['resolu']

## regarde les dosages différents : 
### est-ce la bonne unité ? 


all['UNITE_SA'] = all['UNITE_SA'].str.replace('MG', 'mg')
#all['UNITE_SA'] = all['UNITE_SA'].str.replace('MICROGRAMME\(S\)', 'mg')
unite_cnamts = all['UNITE_SA']
uc = unite_cnamts

dos = all['DOSAGE_SA_ini'] + ' ' + uc
# => pas de problème pour eux : 
res[dos  == all['Dosage']] = 1

test = (uc =='mg') & (res == 0)
all.CIP.value_counts()

sub_all = all.groupby('CIP').filter(lambda x: len(x) == 1)
sub_all['resolu'] = 0
res = sub_all['resolu']

dos_gouv = sub_all['Dosage'].astype(str)
unit_c = sub_all['UNITE_SA'].astype(str)
dos_c = sub_all['DOSAGE_SA']

#test = unit_c.str.contains('mg') & dos_gouv.str.contains('mg')
res.iloc[:1000].value_counts()

for idx, row in sub_all[['Dosage', 'UNITE_SA',  'DOSAGE_SA', 'NOM_LONG1', 'Label_presta']].iloc[:1000].iterrows():
    dos_gouv = str(row['Dosage'])
    unit_c = str(row['UNITE_SA'])
    dos_c = row['DOSAGE_SA']
    
    if unit_c == 'nan' or dos_gouv == 'nan':
        pass

    if unit_c in dos_gouv:
        dos_g = extract_quantity(dos_gouv, unit_c)
        if math.isnan(dos_c): 
            res.loc[idx] = -1
        elif dos_g == dos_c:
            res.loc[idx] = 1
        # elif 0.8 < dos_g/dos_c < 1: 
        else:
            print idx
            # print row
            res.loc[idx] = 2

    
#    if not math.isnan(unit_c):
#        print(idx, 'prob_dos')
#        print unit_c
#        pdb.set_trace()

xxx

all['UNITE_SA'].replace('MG', 'mg', inplace=True)













# virer les CIP7
test = all
deux_subst = test.NOM_LONG1.str.contains('MG/') & test.NOM_LONG1.str.contains(', ')
deux_subst = (1 - test.NOM_LONG1.str.contains('24 H')) & (deux_subst)
deux_subst = (1 - test.NOM_LONG1.str.contains('16 H')) & (deux_subst)
deux_subst = (1 - test.NOM_LONG1.str.contains(' ML ')) & (deux_subst)

prob = test[deux_subst]
  

# 781 cas sur 1327
# 1108 sur 2020
HYDROCHLOROTHIAZIDE = prob.NOM_LONG1.str.contains('HYDROCHLOROTHIAZIDE')
hydroturc = prob[HYDROCHLOROTHIAZIDE]
#  HYDROCHLOROTHIAZIDE en deuxième position
deuxieme = hydroturc[hydroturc.NOM_LONG1.str.contains('/HYDROCHLOROTHIAZIDE') | \
                     hydroturc.NOM_LONG1.str.contains(', HYDROCHLOROTHIAZIDE') | \
                     hydroturc.NOM_LONG1.str.contains('IL HYDROCHLOROTHIAZIDE') |
                     hydroturc.NOM_LONG1.str.contains('-HYDROCHLOROTHIAZIDE')] 
#  HYDROCHLOROTHIAZIDE en deuxième position
premiere = hydroturc[~hydroturc.CIP.isin(deuxieme.CIP)] # en ait premier aussi.
# => tous les HYDROCHLOROTHIAZIDE sont en deuxième position

autre = prob[~HYDROCHLOROTHIAZIDE]
    
    
all['dosage_gouv'] = table_update(all)

# différence
diff = all[all['dosage_gouv'] != all['unites_par_boite']]
diff_SA = diff[diff['Nature_Composant'] == 'SA']