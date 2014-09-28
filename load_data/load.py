# -*- coding:cp1252 -*-
'''
Created on 28 sept. 2014

@author: alexis
'''

import medic_gouv as mg
import bdm_cnamts as cnamts
from bdm_cnamts_prix import load_cnamts_prix_harmonise
from sniiram import load_sniiram

def load_all(from_gouv, maj_gouv, from_cnamts):
    # Chargement des données médicaments.gouv et cnamts
    gouv = mg.load_medic_gouv(maj_gouv, var_to_keep=from_gouv, CIP_not_null=True)
    cnam = cnamts.bdm_cnamts(from_cnamts)
    
    # Chargement de la base Sniiram
    sniiram = load_sniiram()
    #Chargement des prix dynamiques
    prix_dynamiques = load_cnamts_prix_harmonise()
    # On merge les bases
    base_brute = gouv.merge(cnam, left_on = 'CIP13', right_on='CIP')
    base_brute = base_brute.merge(sniiram, left_on='CIP13', right_index=True, how='outer')
    base_brute = base_brute.merge(prix_dynamiques, left_on = 'CIP13', right_on='CIP', how='outer')
    #On remplace les nan des periodes par 0
    base_brute.fillna(0, inplace=True)
    
    return base_brute