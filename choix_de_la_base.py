# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 10:09:55 2014

@author: work
"""
import re
import numpy as np
import pandas as pd


def calcul_dosage_par_prestation_test(table):
    '''Renvoie le dosage par prestation estimé pour les deux bases cnamts et medic_gouv'''
    print 'actuellement dans calcul_dosage_par_prestation'
    # Pour la base medic_gouv
    table.loc[table['Dosage'] == 'qs', 'Dosage'] = 0  # Cas particulier
    table['Dosage_num'] = table['Dosage'].str.findall('\d*\.?\d+').str.get(0)
    table['Dosage_num'] = table['Dosage_num'].astype(float)
    table['dosage_par_prestation_medic_gouv'] = table['Dosage_num']*table['nb_ref_in_label_medic_gouv']
    table['dosage_par_prestation_medic_gouv'].replace(0, np.nan, inplace=True)
    # Pour la base cnamts
    table['dosage_par_prestation_cnamts'] = table['DOSAGE_SA']*table['NB_UNITES']
    return table


def prix_par_dosage_test(table):
    date = 201406
    string = 'prix_' + str(date)
    table['prix_par_dosage_test_cnamts'] = [float(x) / float(y) for x,y in zip(table[string], table['dosage_par_prestation_cnamts'])]
    table['prix_par_dosage_test_medic_gouv'] = [float(x) / float(y) for x,y in zip(table[string], table['dosage_par_prestation_medic_gouv'])]
    return table


def choix_de_la_base(table):
    '''Indique s'il faut conserver les valeurs du cnamts ou de médic. gouv pour chaque médicament
    Le choix est fait de telle sorte à minimiser la variance de prix au sein d un groupe'''

    print 'actuellement dans choix_de_la_base'
    table = calcul_dosage_par_prestation_test(table)
    table['base_choisie'] = pd.Series()

#    prix_nul = table['prix_par_dosage_test_medic_gouv'] == 0
#    table.loc[prix_nul, 'prix_par_dosage_test_medic_gouv'] = \
#    table.loc[prix_nul, 'prix_par_dosage_test_medic_gouv'].apply(lambda x: np.nan)

    global taille_du_groupe
    global prix_moyen_par_groupe_medic_gouv
    global prix_moyen_par_groupe_cnamts
    global variance_par_groupe_medic_gouv
    global variance_par_groupe_cnamts
    grp = table.groupby('group')
    taille_du_groupe = grp.size()

    table = prix_par_dosage_test(table)

    prix_moyen_par_groupe_medic_gouv = grp['prix_par_dosage_test_medic_gouv'].sum().div(taille_du_groupe)#.apply(lambda x: x*x) #Il s'agit en fait du carré
    prix_moyen_par_groupe_cnamts = grp['prix_par_dosage_test_cnamts'].sum().div(taille_du_groupe)#.apply(lambda x: x*x) #Il s'agit en fait du carré

    prix_var_norm_par_groupe_medic_gouv = table.groupby('group')['prix_par_dosage_test_medic_gouv'].std().div(prix_moyen_par_groupe_medic_gouv)
    prix_var_norm_par_groupe_cnamts = table.groupby('group')['prix_par_dosage_test_cnamts'].std().div(prix_moyen_par_groupe_cnamts)

    # On conserve les prix dans la même base si on a tous les prix d'un groupe
    a = prix_moyen_par_groupe_medic_gouv.notnull()
    b = prix_moyen_par_groupe_cnamts.notnull()

    #Pour chaque groupe
    i = 0
    for group in set(table['group']):
        if i % 100 == 0:
            print str(float(i) / float(len(set(table['group'])))) + '%'
        i = i + 1
        # Dans le cas où les valeurs de prix pour tout le groupe dans les deux base
        if a[group] and b[group]:
            # On garde le groupe avec la variance normalisée la plus faible
            if prix_var_norm_par_groupe_medic_gouv[group] < prix_var_norm_par_groupe_cnamts[group]:
                table.loc[table['group'] == group, 'base_choisie'] = 'medic_gouv'
            else:
                table.loc[table['group'] == group, 'base_choisie'] = 'cnamts'
        elif a[group]:
            table.loc[table['group'] == group, 'base_choisie'] = 'medic_gouv'
        elif b[group]:
            table.loc[table['group'] == group, 'base_choisie'] = 'cnamts'
        else:
            # Enfin, si on a deux valeurs différentes, on calcule le prix relativement à la moyenne du groupe.
            # Le prix "moyen" est en réalité la somme des prix mais ca n'a pas de conséquences
            table[table['base_choisie'].isnull()] = table[table['base_choisie'].isnull()].apply(lambda x: choix_de_la_base_lambda1(x), axis=1)
            # print('f')
            table[table['base_choisie'].isnull()] = table[table['base_choisie'].isnull()].apply(lambda x: choix_de_la_base_lambda2(x), axis=1)
    return table


def choix_de_la_base_lambda1(ligne):
    if ligne['prix_par_dosage_test_medic_gouv'] == 0:
        ligne['prix_par_dosage_test_medic_gouv'] = np.nan
    if sum(ligne[['prix_par_dosage_test_medic_gouv', 'prix_par_dosage_test_cnamts']].isnull()) == 2:
        ligne['base_choisie'] = 'Aucune'
    elif sum(ligne[['prix_par_dosage_test_medic_gouv', 'prix_par_dosage_test_cnamts']].isnull()) == 1:
        if np.isnan(ligne['prix_par_dosage_test_medic_gouv']):
            ligne['base_choisie'] = 'cnamts'
        else:
            ligne['base_choisie'] = 'medic_gouv'
    elif ligne['prix_par_dosage_test_medic_gouv'] == ligne['prix_par_dosage_test_cnamts']:
        ligne['base_choisie'] = 'medic_gouv'
    return ligne


def choix_de_la_base_lambda2(ligne):
    # On choisit la base qui donne un ratio le plus petit possible (équivalent écart à la moyenne)
    # print (prix_moyen_par_groupe_medic_gouv[ligne['Id_Groupe']])
    # if taille_du_groupe[ligne['group']] <=2:
    #    ligne['base_choisie'] = 'medic_gouv'

    ratio_medic_gouv = ligne['prix_par_dosage_test_medic_gouv'] / float(prix_moyen_par_groupe_medic_gouv[ligne['group']])
    ratio_cnamts = ligne['prix_par_dosage_test_cnamts'] / float(prix_moyen_par_groupe_cnamts[ligne['group']])
    if ratio_medic_gouv < 1:
        ratio_medic_gouv = float(1) / ratio_medic_gouv
    if ratio_cnamts < 1:
        ratio_cnamts = float(1) / ratio_cnamts

    if ratio_medic_gouv < ratio_cnamts:
        ligne['base_choisie'] = 'medic_gouv'
    else:
        ligne['base_choisie'] = 'cnamts'
    return ligne
