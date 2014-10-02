# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 11:54:31 2014

@author: aeidelman
"""

from load_data.bdm_cnamts import bdm_cnamts
from load_data.medic_gouv import load_medic_gouv, table_update


gouv = load_medic_gouv(var_to_keep=['CIP7', 'Label_presta',
                'Element_Pharma', 'Code_Substance', 'Nom_Substance',
                'Dosage', 'Ref_Dosage', 'Nature_Composant'])
cnam = bdm_cnamts(['CIP', 'CIP7','DOSAGE_SA', 'UNITE_SA'])


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