# -*- coding: utf-8 -*-
"""
Created on Tue Dec 09 12:15:50 2014

@author: Leo, Alexis
"""

import math
import numpy as np
import pandas as pd

from exploitation_sniiram import get_base_brute
from load_data.atc_ddd import load_atc_ddd
from outils import all_periods


def lambda_float(x):
    try:
        return float(x)
    except:
        return np.nan


def sel_by_dosage_value(table):
    '''Sensé selectionner les CIP dont les dosages sont des nombres ronds '''
    dosage = table['Dosage']
    if dosage.notnull().all():
        # On prend la valeure numérique du dosage
        
        dosage = dosage.str.split().apply(lambda x: x[0]).apply(lambda_float)
        # On vérifie que tous les dosages sont bien définis et non nulls
        if dosage.notnull().all() and (dosage != 0).all():
            max_val = dosage.max()
            min_val = dosage.min()
            # On s'assure que l'écart relatif maximal est faible
            if (float(max_val) / float(min_val)) < 1.3:
                # On récupere la puissance de dix de chaque dosage en nottation scientifique
                n = dosage.apply(lambda x: 10**(math.floor(math.log(x, 10))))
                # On récupère la première partie de la notation scientifique
                dosage = dosage / n
                for i in range(3):
                    test = dosage == dosage.apply(round)
                    # Si on a une unique ligne pour laquelle le dosage est nul on renvoie 
                    if (test.sum()) == 1:
                        return test
                    else:
                        dosage = 10 * dosage
    return pd.Series(False, index = dosage.index)


def selection_CIP_ASMR(table):
    ''' choisit une seule ASMR par CIP, pour ne pas avoir de doublon '''
    # TODO:
    table['Nom_Substance'].fillna('inconnu', inplace=True)
    # Attention : dans la selection, on ne filtre plus les groupes qui ont des substances inconnues
    table = table.groupby(['CIP','Nom_Substance']).first().reset_index()
    return table

def selection_CIP_substance(table):
    '''Ajoute les champs "selector" et "classe_a_conserver" dans la table'''
    '''selector est une selectiona au niveau de chaque CIP'''
    '''classe_a_conserver montre les classes qui sont assez complètes après la selection (selector)'''
    
    # XXXXXXXXXXXXXXXXXXXXXXXXX
    # PARAMETRE
    method = 2 # Methode pour le fuzzy join (1 : sans séparation des mots, 2 : avec séparation des mots)
    # XXXXXXXXXXXXXXXXXXXXXXXXX

    
     #######################################################################
     ##### ETAPE 0 : selection par cip unique       
    
    # Calcul du nombre de lignes pour chaque CIP
    nb_CIP = table.groupby('CIP').apply(len)
    nb_CIP = pd.DataFrame(nb_CIP, columns = ['nb_CIP'])
    table = pd.merge(table, nb_CIP, left_on = 'CIP', right_index = True, how = 'left')

    # Calcule le nombre de substances différentes pour chaque CIP
    nb_substances = table.groupby('CIP')['Code_Substance'].apply(lambda x: x.nunique()) # Nombre de substances differentes dans : le cip
    nb_substances = pd.DataFrame(nb_substances)
    nb_substances.columns = ['nb_substances'] # Il y a un bug à cause de l'attribut name de la série
    table = pd.merge(table, nb_substances, left_on = 'CIP', right_index = True, how = 'left')

     #######################################################################
     ##### ETAPE 1 : selection par le mot _Base dans le nom_substance

    # On regarde si le nom de substance contient le mot Base et si celui çi est unique pour le CIP
    # Selecteur : On sélectionne les médicaments définis comme "de base"
    selector_substance_base = table['Nom_Substance'].str.contains(' BASE')
    selector_substance_base.fillna(False, inplace = True)
    # Selecteur : On compte qu'il n'y a qu'un seul "de base" pour un un unique CIP


    selector_seule_base = (table[selector_substance_base].groupby('CIP').apply(len) == 1) & table[selector_substance_base].groupby('CIP')['Nom_Substance'].apply(lambda x: x.notnull().all())
    selector_seule_base.fillna(False, inplace = True)
    selector_seule_base = selector_seule_base[selector_seule_base]
    table['une_seule_base'] = table['CIP'].isin(selector_seule_base.index)
    selector_is_Base = selector_substance_base & (table['une_seule_base'])

    # On fait l'union des selecteurs
    selector = (table['nb_CIP'] == 1) | selector_is_Base #| selector_is_SA
    print "A l'étape 1), on a : "
    print table[selector].groupby('CIP').apply(len).value_counts()
    assert table.loc[selector, 'CIP'].value_counts().max() == 1


     #######################################################################
     ##### ETAPE 2 : selection par cip rond

    # On selectionne les lignes à éliminer car le CIP est déjà dedans
    table['cip_sel'] = table['CIP'].isin(table.loc[selector, 'CIP']) # True si le CIP est déjà dedans
    cip_sel = table['cip_sel']

    tab_copy = table[~cip_sel]

    # On selectionne les médicaments qui ont un dosage rond
    h = tab_copy.groupby('CIP').apply(sel_by_dosage_value)
    h = h.reset_index() # h[0] est True si la ligne est selectionnée
    print 'les deux valeurs doivent être égales : ' + str(h[0].sum()) + ' et ' + str(h.loc[h[0], 'CIP'].nunique())
    assert h[0].sum() == h.loc[h[0], 'CIP'].nunique()
    table['cip_rond'] = False
    indexes = h.loc[h[0], 'level_1'] # h[0] correspond au fait d'être selectionné (T/F), et h['level_1'] est l'index du médicament
    table.loc[indexes, 'cip_rond'] = True

    print "La selection 'dosage_rond' ajoute : " + str(table['cip_rond'].sum()) + ' médicaments uniques'

    selector = selector | table['cip_rond']
    print "A l'étape 2), on a : "
    print table[selector].groupby('CIP').apply(len).value_counts()


     #######################################################################
     ##### ETAPE 3 : selection fuzzy join

    # On selectionne les lignes à éliminer car le CIP est déjà dedans
    cip_sel = table['CIP'].isin(table.loc[selector, 'CIP']) # True si le CIP est déjà dedans
    # On choisit les CIP qui n'ont pas été selectionné
    tab_copy = table[~cip_sel]

    # On selectionne les médicaments dont le Code_substance est proche
    # en retirant les voyelles
    
    if method == 1:
        voyelles = ['A', 'E', 'I', 'O', 'U', 'Y', 'É', '\xc9', "D'", '\xca', 'Ê', ' ']
        substance_ddd = tab_copy['CHEMICAL_SUBSTANCE'].str.upper()
        substances = tab_copy['Nom_Substance']    
        for voy in voyelles:
            substance_ddd = substance_ddd.str.replace(voy, '')
            substances = substances.str.replace(voy, '')
            
    if method == 2:
        voyelles = ['A', 'E', 'I', 'O', 'U', 'Y', 'É', '\xc9', '\xca', 'Ê']
        substance_ddd = tab_copy['CHEMICAL_SUBSTANCE'].str.upper()
        substances = tab_copy['Nom_Substance']
        substances = substances.str.replace(' DE ', ' ')
        substances = substances.str.replace(" D'", ' ')
        for voy in voyelles:
            substance_ddd = substance_ddd.str.replace(voy, '')
            substances = substances.str.replace(voy, '')
        
        def lambda_set_or_nan(x):
            if isinstance(x, list):
                return set(x)
            else:
                return np.nan
        
        substance_ddd = substance_ddd.str.split().apply(lambda_set_or_nan)
        substances = substances.str.split().apply(lambda_set_or_nan)
        
    tab_copy.loc[:, 'substance_of_ddd'] = substances == substance_ddd
    tab = tab_copy.groupby('CIP').filter(lambda x: sum(x['substance_of_ddd']) == 1)
    selector_substance_ddd = tab[tab['substance_of_ddd']].index
    
    table['select_by_subst_match'] = False
    table.loc[selector_substance_ddd, 'select_by_subst_match'] = True
    
    print "normalement, la seule valeur est 1: " + str(table[table['select_by_subst_match']].groupby('CIP').apply(len).value_counts())

    print "La selection 'fuzzy_join' ajoute : " + str(table['select_by_subst_match'].sum()) + ' médicaments uniques'

    selector = selector | table['select_by_subst_match']
    print "A l'étape 3), on a : "
    print table[selector].groupby('CIP').apply(len).value_counts()

    #######################################################################

    # Var veut dire variation (i.e. il y a plusieurs valeurs possibles)
    var_in_substance = (tab_copy.groupby('CIP')['Code_Substance'].apply(lambda x: x.nunique()) > 1) & tab_copy.groupby('CIP')['Code_Substance'].apply(lambda x: x.notnull().all())
    var_in_substance = var_in_substance[var_in_substance]
    tab_copy.loc[:, 'var_in_substance'] = tab_copy['CIP'].isin(var_in_substance.index)
#    var_in_substance = pd.DataFrame(var_in_substance)
#    var_in_substance.columns = ['var_in_substance']
    var_in_ASMR = (tab_copy.groupby('CIP')['Valeur_ASMR'].apply(lambda x: x.nunique()) > 1) & (tab_copy.groupby('CIP')['Valeur_ASMR'].apply(lambda x: x.notnull().all()))
    var_in_ASMR = var_in_ASMR[var_in_ASMR]
    tab_copy.loc[:, 'var_in_ASMR'] = tab_copy['CIP'].isin(var_in_ASMR.index)

    print 'xxxxxxxxxxxxxxx'
    print 'Variations dans la substance'
    print tab_copy['var_in_substance'].value_counts()
    print 'yyyyyyyyyyyyyy'
    print 'Variations dans l ASMR'
    print tab_copy['var_in_ASMR'].value_counts()
    print 'zzzzzzzzzzzzzz'

    table['selector_cip'] = selector
    
    table.drop(['nb_CIP', 'nb_substances'], axis=1)
    return table    


def selection_classe(table, selector = ''):
    '''Renvoie une table en ajoutant le champ "classe_a_conserver"'''
    '''Ce champ indique si la sélection effectuée par selector laisse les classes entières'''    
    
    # XXXXXXXXXXXXXXXXXXXXXXXXX
    # PARAMETRE
    seuil_conservation = 1 # Proportion de ventes et nombres de médicaments pour que la classe soit considérée complète
    # XXXXXXXXXXXXXXXXXXXXXXXXX

    if isinstance(selector, str):
        selector = table['selector_cip']

    period = all_periods(table)[0]
            
    def lambda_nb(x):
        return x.loc[selector, 'CIP'].nunique() >= seuil_conservation * x['CIP'].nunique()
    
    def lambda_ventes(x):
        return x.loc[selector, period].sum().sum() >= seuil_conservation * x[period].sum().sum()
    
    classes_a_conserver = table.groupby('CODE_ATC_4').filter(lambda x: lambda_nb(x) & lambda_ventes(x))

    ind = classes_a_conserver.index
    
    table['selector_classe'] = table.index.isin(ind)
    
    return table


    ######################################################################
    ###### Visualisation des facteurs de multiplicité

#    medicaments_par_classe_avt = table.groupby('CODE_ATC_4')['CIP'].nunique()
#    boites_vendues_par_classe_avt = table.groupby('CODE_ATC_4')[period].sum().sum(axis=1)

#    medicaments_par_classe_apr = table[selector].groupby('CODE_ATC_4')['CIP'].nunique()
#    boites_vendues_par_classe_apr = table[selector].groupby('CODE_ATC_4')[period].sum().sum(axis = 1)

#    classes_a_conserver_ventes = table.groupby('CODE_ATC_4').filter(lambda x: )    
    
#    classes_a_conserver_nb = (medicaments_par_classe_apr/medicaments_par_classe_avt)
#    classes_a_conserver_nb = classes_a_conserver_nb >= seuil_conservation

#    classes_a_conserver_ventes = (boites_vendues_par_classe_apr / boites_vendues_par_classe_avt)
#    classes_a_conserver_ventes = classes_a_conserver_ventes >= seuil_conservation

#    classes_a_conserver = classes_a_conserver_nb & classes_a_conserver_ventes
#    classes_a_conserver = pd.DataFrame(classes_a_conserver, columns = ['classe_a_conserver'])

    ######## Fin : filtrage pour les classes assez complètes
    ######################################################################

#    table = table.merge(classes_a_conserver, left_on = 'CODE_ATC_4', right_index = True, how = 'left')


if __name__ == '__main__':
    base_brute = get_base_brute()
    base_ASMR = selection_CIP_ASMR(base_brute)
    base_substance = selection_CIP_substance(base_ASMR)
    base = selection_classe(base_substance, base_substance['selector_cip'])
    
    sel = base['selector_cip'] & base['selector_classe'] # La dernière sélection à faire   
    
    # Les CIP que l'on a pas récupéré
    non_sel = base.groupby('CIP').filter(lambda x: ~x['selector_cip'].any())
    sauvables = non_sel.groupby('CIP').filter(lambda x: x['CHEMICAL_SUBSTANCE'].notnull().any())
