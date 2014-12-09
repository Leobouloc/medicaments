# -*- coding: utf-8 -*-
"""
Created on Tue Dec 09 12:15:50 2014

@author: Leo, Alexis
"""

import math
import numpy as np      
import pandas as pd

from exploitation_sniiram import get_base_brute
from fuzzy_join import fuzzy_join
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



def selection_ASMR(table):
    ''' choisit une seule ASMR par CIP, pour ne pas avoir de doublon '''
    # TODO:
    table['Nom_Substance'].fillna('inconnu', inplace=True)
    return table.groupby(['CIP','Nom_Substance']).first().reset_index()

def selection_substance(table):
    '''Ajoute les champs selector et classe_a_conserver dans base_brute'''
    '''selector dépend des criteres choisis'''
    '''classe_a_conserver montre les classes qui sont assez complètes après selector'''

    period = all_periods(table)[0]
    
    # Calcul du nombre de lignes pour chaque CIP
    nb_CIP = table.groupby('CIP').apply(len)
    nb_CIP = pd.DataFrame(nb_CIP, columns = ['nb_CIP'])
    table = pd.merge(table, nb_CIP, left_on = 'CIP', right_index = True, how = 'left')

    # Calcule le nombre de substances différentes pour chaque CIP
    nb_substances = table.groupby('CIP')['Code_Substance'].apply(lambda x: x.nunique()) # Nombre de substances differentes dans : le cip
    nb_substances = pd.DataFrame(nb_substances)
    nb_substances.columns = ['nb_substances'] # Il y a un bug à cause de l'attribut name de la série
    table = pd.merge(table, nb_substances, left_on = 'CIP', right_index = True, how = 'left')

    # On regarde si le nom de substance contient le mot Base et si celui çi est unique pour le CIP
    # Selecteur : On sélectionne les médicaments définis comme "de base"
    selector_substance_base = table['Nom_Substance'].str.contains(' BASE')
    selector_substance_base.fillna(False, inplace = True)
    # Selecteur : On compte qu'il n'y a qu'un seul "de base" pour un un unique CIP


    selector_seule_base = (table[selector_substance_base].groupby('CIP').apply(len) == 1) & table[selector_substance_base].groupby('CIP')['Nom_Substance'].apply(lambda x: x.notnull().all())
    selector_seule_base.fillna(False, inplace = True)
    selector_seule_base = selector_seule_base[selector_seule_base]
    table['une_seule_base'] = table['CIP'].isin(selector_seule_base.index)
#    selector_seule_base = pd.DataFrame(selector_seule_base)
#    selector_seule_base.columns = ['une_seule_base']
#    table = table.merge(selector_seule_base, left_on = 'CIP', right_index = True, how = 'left')
    selector_is_Base = selector_substance_base & (table['une_seule_base'])


    ### ATTENTION : le selectionneur par SA n'est pas correct
##   Selecteur : On regarde s'il y a une unique SA pour le CIP
#    selector_SA_defini = table.groupby('CIP')['Nature_Composant'].apply(lambda x: (sum(x == 'SA') == 1) & x.notnull().all())
#    selector_SA_defini = selector_sa_defini[selector_sa_defini]
#    table['SA_defini'] = table['CIP'].isin(selector_SA_defini.index)
##    selector_SA_defini = pd.DataFrame(selector_SA_defini)
##    selector_SA_defini.columns = ['SA_defini']
##    table = table.merge(selector_SA_defini, left_on = 'CIP', right_index = True, how = 'left')
#    selector_is_SA = table['SA_defini'] & (table['Nature_Composant'] == 'SA')

    # On fait l'union des selecteurs
    selector = (table['nb_CIP'] == 1) | selector_is_Base #| selector_is_SA
    print "A l'étape 1), on a : "
    print table[selector].groupby('CIP').apply(len).value_counts()
    assert table.loc[selector, 'CIP'].value_counts().max() == 1


     ###############################################################
     ##### ETAPE 2

#    # On selectionne les lignes à éliminer car le CIP est déjà dedans
    table['cip_sel'] = table['CIP'].isin(table.loc[selector, 'CIP']) # True si le CIP est déjà dedans
    cip_sel = table['cip_sel']


    # table = table.merge(cip_sel, left_on = 'CIP', right_index = True, how = 'left')
    # table['cip_sel'] = table['cip_sel'].fillna(False)
    # TODO: mettre pivot table pour conserver tous les changements de dates d'ASMR
    # On choisit les CIP qui n'ont pas été selectionné
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


     ###############################################################
     ##### ETAPE 3

#    # On selectionne les lignes à éliminer car le CIP est déjà dedans
    cip_sel = table['CIP'].isin(table.loc[selector, 'CIP']) # True si le CIP est déjà dedans
    table['cip_sel'] = cip_sel
    # On choisit les CIP qui n'ont pas été selectionné
    tab_copy = table[~cip_sel]

    # On selectionne les médicaments dont le Code_substance est proche
    # en retirant les voyelles
    voyelles = ['A', 'E', 'I', 'O', 'U', 'Y', 'É', '\xc9', "D'", '\xca', 'Ê', ' ']
    substance_ddd = tab_copy['CHEMICAL_SUBSTANCE'].str.upper()
    substance = tab_copy['Nom_Substance']    
    for voy in voyelles:
        substances_ddd = substance_ddd.str.replace(voy, '')
        substance = substance.replace(voy, '')
        
    tab_copy['substance_of_ddd'] = substance == substances_ddd
    une_seule_substance_dans_base = tab_copy.groupby('CIP').filter(lambda x: sum(x['substance_of_ddd']) == 1)
    tab =  une_seule_substance_dans_base
    selector_substance_ddd = tab[tab['substance_of_ddd']].index

    # TODO: inspecter pourquoi parfois il n'y a pas de match 
    assert len(tab_copy.groupby('CIP').filter(lambda x: sum(x['substance_of_ddd']) > 1)) == 0
    test = tab_copy.groupby('CIP').filter(lambda x: sum(x['substance_of_ddd']) == 0)


    h2 = tab_copy.groupby('CIP').apply(lambda x: fuzzy_join(x, atc_ddd))
    h2 = h2.reset_index() # h[0] correspond au fait d'être selectionné (T/F), et h['level_1'] est l'index du médicament
    print 'les deux valeurs doivent être égales : ' + str(h2[0].sum()) + ' et ' + str(h2.loc[h2[0], 'CIP'].nunique())
    assert h2[0].sum() == h2.loc[h2[0], 'CIP'].nunique()    
    table['same_subst'] = False
    indexes = h2.loc[h2[0], 'level_1']
    table.loc[indexes, 'same_subst'] = True

    print "La selection 'fuzzy_join' ajoute : " + str(table['same_subst'].sum()) + ' médicaments uniques'

    selector = selector | table['same_subst']
    print "A l'étape 3), on a : "
    print table[selector].groupby('CIP').apply(len).value_counts()

    ###################################################################

    # Var veut dire variation (i.e. il y a plusieurs valeurs possibles)
    var_in_substance = (tab_copy.groupby('CIP')['Code_Substance'].apply(lambda x: x.nunique()) > 1) & tab_copy.groupby('CIP')['Code_Substance'].apply(lambda x: x.notnull().all())
    var_in_substance = var_in_substance[var_in_substance]
    tab_copy['var_in_substance'] = tab_copy['CIP'].isin(var_in_substance.index)
#    var_in_substance = pd.DataFrame(var_in_substance)
#    var_in_substance.columns = ['var_in_substance']
    var_in_ASMR = (tab_copy.groupby('CIP')['Valeur_ASMR'].apply(lambda x: x.nunique()) > 1) & (tab_copy.groupby('CIP')['Valeur_ASMR'].apply(lambda x: x.notnull().all()))
    var_in_ASMR = var_in_ASMR[var_in_ASMR]
    tab_copy['var_in_ASMR'] = tab_copy['CIP'].isin(var_in_ASMR.index)

#    var_in_ASMR = pd.DataFrame(var_in_ASMR)
#    var_in_ASMR.columns = ['var_in_ASMR']



#    tab_copy = tab_copy.merge(var_in_substance, left_on = 'CIP', right_index = True, how = 'left')
#    tab_copy = tab_copy.merge(var_in_ASMR, left_on = 'CIP', right_index = True, how = 'left')

    print 'xxxxxxxxxxxxxxx'
    print 'Variations dans la substance'
    print tab_copy['var_in_substance'].value_counts()
    print 'yyyyyyyyyyyyyy'
    print 'Variations dans l ASMR'
    print tab_copy['var_in_ASMR'].value_counts()
    print 'zzzzzzzzzzzzzz'

#    selector_ASMR = tab_copy[~tab_copy['var_in_substance'] & tab_copy['var_in_ASMR']].groupby('CIP').apply(first_largest_asmr).reset_index()
#    selector_ASMR = pd.DataFrame(selector_ASMR['Valeur_ASMR'], index = list(selector_ASMR['CIP']), columns = ['selector_ASMR'])
#    selector_ASMR.columns = ['selector_ASMR']
#    table = table.merge(selector_ASMR, left_on = 'CIP', right_index = True, how = 'left')
#    table['selector_ASMR'].fillna(False, inplace = True)
#    selector_ASMR = table['selector_ASMR']
#
#    # TODO: Ca ne marche pas !!!
#    print selector_ASMR
#    print selector_ASMR.value_counts()
#    print selector
#
#    selector = selector | selector_ASMR


#    table = table.drop('nb_CIP', axis = 1)
#    table = table.drop('nb_substances', axis = 1)

    table['selector'] = selector

    ################################################################################

    medicaments_par_classe_avt = table.groupby('CODE_ATC_4')['CIP'].nunique()
    boites_vendues_par_classe_avt = table.groupby('CODE_ATC_4')[period].sum().sum(axis=1)

    medicaments_par_classe_apr = table[selector].groupby('CODE_ATC_4')['CIP'].nunique()
    boites_vendues_par_classe_apr = table[selector].groupby('CODE_ATC_4')[period].sum().sum(axis = 1)
    classes_a_conserver_nb = (medicaments_par_classe_apr/medicaments_par_classe_avt)
    classes_a_conserver_nb = classes_a_conserver_nb > 0.8

    classes_a_conserver_ventes = (boites_vendues_par_classe_apr / boites_vendues_par_classe_avt)
    classes_a_conserver_ventes = classes_a_conserver_ventes > 0.8


    classes_a_conserver = classes_a_conserver_nb & classes_a_conserver_ventes
    classes_a_conserver = pd.DataFrame(classes_a_conserver, columns = ['classe_a_conserver'])

    ######## Fin : filtrage pour les classes assez complètes
    ##################################################


    table = table.merge(classes_a_conserver, left_on = 'CODE_ATC_4', right_index = True, how = 'left')

    table.drop(['nb_CIP', 'nb_substances'], axis=1)
    return table


if __name__ == '__main__':
    base_brute = get_base_brute()
    base_ASMR = selection_ASMR(base_brute)
    test = selection_substance(base_ASMR)