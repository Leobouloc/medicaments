# -*- coding:cp1252 -*-
'''
Created on 28 sept. 2014

@author: alexis
'''

import os
import re
import numpy as np
import pandas as pd
from pandas import read_csv
from numpy import int64

from CONFIG import working_path

from choix_de_la_base import choix_de_la_base
from load_data.atc_ddd import load_atc_ddd

maj_gouv = 'maj_20140915122241'

from datasets import dataset_brut
from datasets import dataset_plus

# TODO: REmplacer par le ddd_par_presta

def calcul_ddd_ligne(ligne, atc_ddd, base_source):
    '''Calcul de la ddd pour les medicaments qu'on a pris de medic_gouv'''
    code_atc = ligne['CODE_ATC']
    selector = atc_ddd['CODE_ATC'] == str(code_atc)
    atc_ddd_restreint = atc_ddd.loc[selector, :]
    
    if len(atc_ddd_restreint) == 0:
        return np.nan
    
    nunique_code_atc = sum(selector)

    if base_source == 'cnamts':
        dosage = ligne['DOSAGE_SA']
        unite = str(ligne['UNITE_SA'])
        nb_unites = ligne['NB_UNITES']
        col_descriptive = 'FORME'
    if base_source == 'medic_gouv':
        try: # avoid
            dosage_list = ligne['Dosage'].split()
            dosage = float(dosage_list[0])
        except:
            return np.nan
        unite = dosage_list[1]
        nb_unites = ligne['nb_ref_in_label_medic_gouv']
        col_descriptive = 'Label_presta'
        if len(dosage_list) != 2:
            return np.nan

    list_mode = dict()
    list_mode['O'] = ['compr', 'lule', 'capsule', 'flacon', 'sirop', 'granule', 'poudre']
    list_mode['P'] = ['seringue']
    list_mode['TD'] = ['creme', 'pommade']
    list_mode['R'] = ['suppositoire']
    list_mode['SL'] = ['gomme', 'pastille'] # pastille n'est peut-être pas à sa place

    '''Si le code est présent une seule fois dans la base des ddd, on n'a pas de doute'''
    if nunique_code_atc == 1:
        '''On vérifie que les unités correspondent bien'''
        if unite.upper() == str(atc_ddd_restreint['UNITE'].iloc[0]):
            ddd_par_presta = dosage * nb_unites / atc_ddd_restreint['DDD'].iloc[0]
            return ddd_par_presta
        else:
            return 'prob_1'
            
    if not isinstance(ligne[col_descriptive], str):
        return 'prob_2'

    if nunique_code_atc == atc_ddd_restreint['MODE'].nunique():
        for mode in ['O', 'P', 'TD', 'R', 'SL']:
            if sum([x in ligne[col_descriptive].lower() for x in list_mode[mode]]) == 1 and mode in list(atc_ddd_restreint['MODE'].apply(str)):
                diviseur = atc_ddd_restreint.loc[atc_ddd_restreint['MODE'] == mode, 'DDD'].iloc[0]
                if unite.upper() == str(atc_ddd_restreint.loc[atc_ddd_restreint['MODE'] == mode, 'UNITE'].iloc[0]):
                    ddd_par_presta = dosage * nb_unites / diviseur
                    return ddd_par_presta
                else:
                    return 'prob_4'
            else:
                return 'prob_5'

    return 'prob_3'
    

def calcul_ddd_par_presta(table, atc_ddd):
    '''Calcul de la dose journalière par prestation : ATTENTION : requiert le champ base_choisie'''
#    assert table['CIP'].nunique() == table['CIP'].notnull().sum()    
#    
    print 'actuellement dans calcul_ddd_par_presta'
    
    table['ddd_par_presta_medic_gouv'] = table.apply(lambda ligne: calcul_ddd_ligne(ligne, atc_ddd, 'medic_gouv'), axis=1)
    table['ddd_par_presta_cnamts'] = table.apply(lambda ligne: calcul_ddd_ligne(ligne, atc_ddd, 'cnamts'), axis=1)

    return table


def create_dataset_ddd(from_gouv, maj_gouv, from_cnamts, force=False):
    table = dataset_plus(from_gouv, maj_gouv, from_cnamts, force)
    ddd = load_atc_ddd()

    table = calcul_ddd_par_presta(table, ddd)
    print (' après calcul ddd :' + str(len(table)))
   
    table = choix_de_la_base(table)
    print (' après choix de la base :' + str(len(table)))

    # => on a une seule substance par code ATC
    assert ddd.groupby(['CODE_ATC'])['CHEMICAL_SUBSTANCE'].nunique().max()
    ddd = ddd[ddd['CHEMICAL_SUBSTANCE'].notnull()]
    ddd = ddd.groupby(['CODE_ATC']).first().reset_index()
    table = table.merge(ddd, how='left')
    return table


def dataset_ddd(from_gouv, maj_gouv, from_cnamts, force=False):
    # Il manque from ddd
    file = os.path.join(working_path, 'dataset_ddd.csv')
    try:
        assert not force
        # TODO: check we have dataset_brut.csv was generated with maj_gouv
        table = read_csv(file, sep=',')
        from_ddd = ['CODE_ATC', 'CHEMICAL_SUBSTANCE', 'DDD', 'UNITE', 'MODE']
        not_saved = ['CIP13', 'CHEMICAL_SUBSTANCE', 'DDD', 'UNITE', 'MODE']
        vars_needed = [x for x in (from_gouv + from_cnamts + from_ddd) if x not in not_saved]
        for var in vars_needed:
            assert var in table.columns
        table['CIP'] = table['CIP'].astype(int64).astype(str)

    except:
        print 'bbbbbbbbbbbbbbbb'
        table = create_dataset_ddd(from_gouv, maj_gouv, from_cnamts, force)
        table.to_csv(file, sep=',', index = False)
        table.columns = [str(x) for x in table.columns]


    table.loc[table['premiere_vente'].notnull(), 'premiere_vente'] = table.loc[table['premiere_vente'].notnull(), 'premiere_vente'].astype(int).astype(str)
    table.loc[table['derniere_vente'].notnull(), 'derniere_vente'] = table.loc[table['derniere_vente'].notnull(), 'derniere_vente'].astype(int).astype(str)
    table.columns = [str(x) for x in table.columns]
    
    return table

if __name__ == '__main__':

    ##### START : Indique le nombre de ddds récupérables au max
    ### liste des atcs présents une seule fois dans atc_ddd
    ddd = load_atc_ddd()
#    base = calcul_ddd_par_presta(base, ddd)
    atcs_uniques = ddd.groupby('CODE_ATC')['CODE_ATC'].filter(lambda x: len(x) == 1)
    base['CODE_ATC'].fillna('', inplace = True)
    ## indique pour chaque cip si son code atc est unique dans atc_ddd
    a = base['CODE_ATC'].apply(lambda x: x in list(atcs_uniques))
    atcs_bien = ddd.groupby('CODE_ATC').filter(lambda x: (len(x) == x['MODE'].nunique()) and (len(x)>1))['CODE_ATC']
    base['CODE_ATC'].fillna('', inplace = True)
    ## indique pour chaque cip si son code atc est utilisable dans atc_ddd
    b = base['CODE_ATC'].apply(lambda x: x in list(atcs_bien))
    ##recuperables
    print 'On pourrait récupérer aux max : ' + str(a.sum() + b.sum()) + ' ddds'
    print 'On en récupère : ' + str((base['ddd_par_presta_medic_gouv'].notnull() | base['ddd_par_presta_cnamts'].notnull()).sum())
    ##### END : Indique le nombre de ddds récupérables au max

    sel = base['ddd_par_presta_cnamts'] == 'prob_1'
    selector = base['ddd_par_presta_cnamts'].isnull() & base['ddd_par_presta_medic_gouv'].isnull()
    base[selector & sel][['ddd_par_presta_cnamts', 'ddd_par_presta_medic_gouv', 'UNITE_SA', 'Dosage', 'UNITE', 'CODE_ATC']].iloc[10:20]


#nunique_code_atc == atc_ddd_restreint['MODE'].nunique()


#    maj_gouv = 'maj_20140915122241'
#    # parametres du calcul
#    # Ne marche pas si la liste inclut 'CIS'
#    from_gouv = ['CIP7', 'CIP', 'Nom', 'Id_Groupe', 'Prix', 'Titulaires', 'Num_Europe',
#                             'Code_Substance', 'Nom_Substance', 'Libelle_ASMR', 'Type',
#                             'Date_declar_commerc', 'Date_AMM', 'Taux_rembours',
#                             'indic_droit_rembours', 'Statu_admin_presta',
#                             'Ref_Dosage', 'Dosage', 'Label_presta','Valeur_ASMR',
#                             'nb_ref_in_label_medic_gouv', 'premiere_vente', 'derniere_vente']
#    from_cnamts = ['CIP', 'CODE_ATC', 'LABO', 'DOSAGE_SA',
#                               'UNITE_SA', 'NB_UNITES'] #LABO
#    from_ddd = ['CODE_ATC', 'CHEMICAL_SUBSTANCE', 'DDD', 'UNITE', 'MODE']
#    
#
##    test = dataset_ddd(info_utiles_from_atc_ddd, info_utiles_from_gouv, maj_gouv, info_utiles_from_cnamts)
#    test2 = dataset_ddd(from_gouv, maj_gouv, from_cnamts)