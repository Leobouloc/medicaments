# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 18:18:37 2014

@author: debian
"""

def selection(table):
    '''Ajoute les champs selector et classe_a_conserver dans base_brute'''
    '''selector dépend des criteres choisis'''
    '''classe_a_conserver montre les classes qui sont assez complètes après selector'''

    for name in ['selector', 'classe_a_conserver', 'SA_defini', 'une_seule_base', 'cip_sel']:
        try :
            table = table.drop(name, axis = 1)
        except:
            pass

    # On retire les groupes qui ont beaucoup trop de substances
    # On travaillera plus loin sur les autres
    # poche = table['Label_presta'].str.contains('poche').sum()
    # TODO: Mettre la sélection de trop de substances après les autres selections par substance
    nb_subs = table.groupby('CIP')['Nom_Substance'].nunique()
    trop_substance = nb_subs[nb_subs > 3].index
    table['trop_de_substances'] = ~(table['CIP'].isin(trop_substances))
#    trop_substance_atc4 = table.loc[table['CIP'].isin(trop_substance), 'CODE_ATC_4']
#    to_remove = table['CODE_ATC_4'].isin(trop_substance_atc4)
    nb_atc4 = table['CODE_ATC_4'].nunique()
    nb_atc4_removed = trop_substance_atc4.nunique()
    print("on retire " + str(nb_atc4_removed) + " groupe atc4 parmi " +
            str(nb_atc4) + " parce qu'on a trop de substances parfois")
    table = table[~to_remove]

#    # Calcul du nombre de lignes pour chaque CIP
#    try:
#        table['nb_CIP']
#    except:
#        nb_CIP = table.groupby('CIP').apply(len)
#        nb_CIP = pd.DataFrame(nb_CIP, columns = ['nb_CIP'])
#        table = pd.merge(table, nb_CIP, left_on = 'CIP', right_index = True, how = 'left')
#
#    # Calcule le nombre de substances différentes pour chaque CIP
#    try:
#        table['nb_substances']
#    except:
#        nb_substances = table.groupby('CIP')['Code_Substance'].apply(lambda x: x.nunique()) # Nombre de substances differentes dans : le cip
#        nb_substances = pd.DataFrame(nb_substances)
#        nb_substances.columns = ['nb_substances'] # Il y a un bug à cause de l'attribut name de la série
#        table = pd.merge(table, nb_substances, left_on = 'CIP', right_index = True, how = 'left')


    # Résolution des CIP multiples
#    multi_cip = table.groupby('CIP').filter(lambda x: len(x) > 1)
    multi_cip = table.groupby('CIP').filter(lambda x: x['Nom_Substance'].nunique(dropna=False) > 1)
    
    print( " au début on a \n", multi_cip['CIP'].value_counts().value_counts())    
    # on fait ici, une séléction apr ASMR, qu'il faudra retirer à terme
    # TODO: voir la séléction d'ASMR avant
    # on séléctionne donc une ligne par CIP/substance
    multi_cip = multi_cip.groupby(['CIP','Nom_Substance']).first().reset_index()
    # on retire quand on ne connait pas la substance
    print( " sans les problemes ASMR on a \n", multi_cip['CIP'].value_counts().value_counts())  
    multi_cip = multi_cip[multi_cip['Nom_Substance'].notnull()]
    multi_cip = multi_cip[multi_cip['Dosage'] != '0'] # un cas : de l'eau
    print( " en retirant les valeurs nulles \n", multi_cip['CIP'].value_counts().value_counts())
#    On regarde si le nom de substance contient le mot Base et si celui çi est unique pour le CIP
#   Selecteur : On sélectionne les substances définies comme "de base"

    multi_cip['Substance_BASE'] = multi_cip['Nom_Substance'].str.contains(' BASE')
    multi_cip['Substance_BASE'].fillna(False, inplace = True)
#   Selecteur : On compte qu'il n'y a qu'un seul "de base" pour un un unique CIP

    def _select_BASE(x):
        return (sum(x['Substance_BASE']) == 1)

    selector_is_Base = multi_cip.groupby('CIP').apply(_select_BASE)
    selector_is_Base = selector_is_Base[selector_is_Base]
    anti_select = (multi_cip['CIP'].isin(selector_is_Base.index)) & \
                            (~multi_cip['Substance_BASE'])
    multi_cip = multi_cip[~anti_select]

    print( " après select BASE, on a  \n", multi_cip['CIP'].value_counts().value_counts())


    dosage = multi_cip['Dosage']
    dose = dosage.str.split().str.get(0)
    dose = dose.apply(lambda_float)

    max_power = int(floor(log(max(dose), 10)))
    min_power = int(floor(log(min(dose), 10)))
    power = Series(min_power - 1, index=multi_cip.index)
    for i in range(min_power, max_power + 1):
        divide = 10**(i)
        cond = dose/divide == (dose/divide).apply(floor)
        power[cond] = i

    multi_cip['power'] = power

    min_power_dosage = multi_cip.groupby('CIP')['power'].min().reset_index()
#    diff = (multi_cip.groupby('CIP')['power'].max() != multi_cip.groupby('CIP')['power'].min()).sum()
    import pdb
    pdb.set_trace()
    multi_cip = multi_cip.merge(min_power_dosage, on=['CIP'], suffixes=('', '_min'))
    multi_cip = multi_cip[multi_cip['power'] == multi_cip['power_min']]
    
    print( " après selection sur les arrondis, on a  \n", multi_cip['CIP'].value_counts().value_counts())


    multi_cip = multi_cip['Label_presta'].str.contains('oche')
    multi_cip.groupby('CIP')['Nom_Substance'].nunique()
    multi_cip = multi_cip['CIP'].value_counts().value_counts()
    


    prob = multi_cip['CIP'].value_counts() > 10
    prob = multi_cip['CIP'].value_counts()[prob].index.tolist()
    prob_table = multi_cip[multi_cip['CIP'].isin(prob)]


#   Selecteur : On regarde s'il y a une unique SA pour le CIP
    selector_SA_defini = table.groupby('CIP')['Nature_Composant'].apply(lambda x: (sum(x == 'SA') == 1) & x.notnull().all())
    selector_SA_defini = pd.DataFrame(selector_SA_defini)
    selector_SA_defini.columns = ['SA_defini']
    table = table.merge(selector_SA_defini, left_on = 'CIP', right_index = True, how = 'left')
    selector_is_SA = table['SA_defini'] & (table['Nature_Composant'] == 'SA')

    # On fait l'union des selecteurs
    selector = (table['nb_CIP'] == 1) | selector_is_Base | selector_is_SA


#    # On selectionne les lignes à éliminer car le CIP est déjà dedans
    cip_sel = pd.DataFrame(True, index = table.loc[selector, 'CIP'], columns = ['cip_sel']) # True si le CIP est déjà dedans
    table = table.merge(cip_sel, left_on = 'CIP', right_index = True, how = 'left')
    table['cip_sel'] = table['cip_sel'].fillna(False)
    cip_sel = table['cip_sel']

    print 'nb cip sel is : ' + str(cip_sel.sum())

    # TODO: mettre pivot table pour conserver tous les changements de dates d'ASMR
    tab_copy = table[~cip_sel]
    # Var veut dire variation
    var_in_substance = (tab_copy.groupby('CIP')['Code_Substance'].apply(lambda x: x.nunique()) > 1) & tab_copy.groupby('CIP')['Code_Substance'].apply(lambda x: x.notnull().all())
    var_in_substance = pd.DataFrame(var_in_substance)
    var_in_substance.columns = ['var_in_substance']
    var_in_ASMR = (tab_copy.groupby('CIP')['Valeur_ASMR'].apply(lambda x: x.nunique()) > 1) & (tab_copy.groupby('CIP')['Valeur_ASMR'].apply(lambda x: x.notnull().all()))
    var_in_ASMR = pd.DataFrame(var_in_ASMR)
    var_in_ASMR.columns = ['var_in_ASMR']

    tab_copy = tab_copy.merge(var_in_substance, left_on = 'CIP', right_index = True, how = 'left')
    tab_copy = tab_copy.merge(var_in_ASMR, left_on = 'CIP', right_index = True, how = 'left')

    print 'xxxxxxxxxxxxxxx'
    print tab_copy['var_in_substance'].value_counts()
    print 'yyyyyyyyyyyyyy'
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
    ####### Début : Filtrage des classes assez complètes
    ### On ne garde que les classes pour lequel il reste une certaine proportion 
    ### de médicaments et de ventes

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


    table = pd.merge(table, classes_a_conserver, left_on = 'CODE_ATC_4', right_index = True, how = 'left')
    return table