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

    list_O = ['compr', 'lule', 'capsule', 'flacon']
    list_P = ['seringue']

    '''Si le code est présent une seule fois dans la base des ddd, on n'a pas de doute'''
    if nunique_code_atc == 1:
        '''On vérifie que les unités correspondent bien'''
        if unite.upper() == str(atc_ddd_restreint['UNITE'].iloc[0]):
            ddd_par_presta = dosage * nb_unites / atc_ddd_restreint['DDD'].iloc[0]
            return ddd_par_presta
            
    if not isinstance(ligne[col_descriptive], str):
        return np.nan

    if nunique_code_atc == atc_ddd_restreint['MODE'].nunique():
        if sum([x in ligne[col_descriptive].lower() for x in list_O]) == 1 and 'O' in list(atc_ddd_restreint['MODE'].apply(str)):
            diviseur = atc_ddd_restreint.loc[atc_ddd_restreint['MODE'] == 'O', 'DDD'].iloc[0]
            if unite.upper() == str(atc_ddd_restreint.loc[atc_ddd_restreint['MODE'] == 'O', 'UNITE'].iloc[0]):
                ddd_par_presta = dosage * nb_unites / diviseur
                return ddd_par_presta

        if sum([x in ligne[col_descriptive].lower() for x in list_P]) == 1 and 'P' in list(atc_ddd_restreint['MODE'].apply(str)):
            diviseur = atc_ddd_restreint.loc[atc_ddd_restreint['MODE'] == 'P', 'DDD'].iloc[0]
            if unite.upper() == str(atc_ddd_restreint.loc[list(atc_ddd_restreint['MODE'] == 'P'), 'UNITE'].iloc[0]): # check replace P for 0 ?
                ddd_par_presta = dosage * nb_unites / diviseur
                return ddd_par_presta
    return np.nan
    

def calcul_ddd_par_presta(table, atc_ddd):
    '''Calcul de la dose journalière par prestation : ATTENTION : requiert le champ base_choisie'''
#    assert table['CIP'].nunique() == table['CIP'].notnull().sum()    
#    
    print 'actuellement dans calcul_ddd_par_presta'
    
    table['ddd_par_presta_medic_gouv'] = table.apply(lambda ligne: calcul_ddd_ligne(ligne, atc_ddd, 'medic_gouv'), axis=1)
    table['ddd_par_presta_cnamts'] = table.apply(lambda ligne: calcul_ddd_ligne(ligne, atc_ddd, 'cnamts'), axis=1)

#    table['ddd_par_presta'] = np.nan
#    # Calcul de la ddd par presta pour les medicaments du cnamts
#    from_cnamts = table['base_choisie'] == 'cnamts'
#    table.loc[from_cnamts, 'ddd_par_presta'] = table.loc[from_cnamts, :].apply(lambda ligne: calcul_ddd_ligne(ligne, atc_ddd, 'cnamts'), axis=1)
#    # Calcul de la ddd par presta pour les medicaments de medic gouv avec une seule substance
#    cip_uniques = table.groupby('CIP')['Code_Substance'].nunique() == 1
#    
#    print 'dans le calcul de ddd par presta'
#    sel1 = table.apply(lambda ligne: (ligne['base_choisie'] == 'medic_gouv'), axis=1)
#    print 'sel1 : ' + str(sel1.sum())
##    sel2 = table.CIP.isin(cip_uniques.index[cip_uniques])
##    sel2 = sel2.apply(lambda x: str(x).replace('[]', 'False')).apply(bool)
##    print 'sel2 : ' + str(sel2.sum())
#    selector = sel1 #& sel2
#    print selector.sum()    
#    print 'selector : ' + str(selector.sum())
##    selector = table.apply(lambda ligne: cip_uniques[ligne['CIP7']] and (ligne['base_choisie'] == 'medic_gouv'), axis=1)
#    table.loc[selector, 'ddd_par_presta'] = table[selector].apply(lambda ligne: calcul_ddd_ligne(ligne, atc_ddd, 'medic_gouv'), axis=1)
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

#
#if __name__ == '__main__':
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