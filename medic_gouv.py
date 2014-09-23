# -*- coding: utf-8 -*-
'''
Created on 26 juin 2014
'''
import pandas as pd
import numpy as np
import pdb

from CONFIG import path_gouv


pd.set_option('max_colwidth',100)
# Derniere mise à jour BDM
maj_bdm = 'maj_20140915122241\\'


dico_variables = dict(
                      bdpm = ['CIS','Nom','Forme','Voies','Statut_AMM','Type_AMM','Etat','Date_AMM','Statut_BDM','Num_Europe','Titulaires','Surveillance'],
                      CIP_bdpm = ['CIS','CIP7','Label_presta', 'Statu_admin_presta','etat_commercialisation',
                                        'Date_declar_commerc','CIP13','aggrement_collectivites','Taux_rembours','Prix', 'indic_droit_rembours'],
                      GENER_bdpm = ['Id_Groupe','Nom_Groupe','CIS','Type','Num_Tri'],
                      COMPO_bdpm = ['CIS','Element_Pharma','Code_Substance','Nom_Substance','Dosage','Ref_Dosage','Nature_Composant','Substance_Fraction'],
                      HAS_SMR_bdpm = ['CIS','HAS','Evalu','Date','Valeur_SMR','Libelle_SMR'],
                      HAS_ASMR_bdpm = ['CIS','HAS','Evalu','Date','Valeur_ASMR','Libelle_ASMR'],
                      )


def load_medic_gouv(maj_bdm, var_to_keep=None, CIP_not_null=False):
    ''' renvoie les tables fusionnées issues medicament.gouv.fr
        si var_to_keep est rempli, on ne revoit que la liste des variables
    '''
    # chargement des données
    path = path_gouv + maj_bdm
    output = None
    for name, vars in dico_variables.iteritems():
        # teste si on doit ouvrir la table
        if var_to_keep is None:
            intersect = vars
        if var_to_keep is not None:
            intersect = [var for var in vars if var in var_to_keep]
        if len(intersect) > 0:
            tab = pd.read_table(path + 'CIS_' + name + '.txt', header=None)
            if name in ['COMPO_bdpm', 'GENER_bdpm']:
                tab = tab.iloc[:,:-1]
            tab.columns = vars
            tab = tab[['CIS'] + intersect]
            # correction ad-hoc...
            if tab['CIS'].dtype == 'object':
                problemes = tab['CIS'].str.contains('REP', na=False)
                problemes = problemes | tab['CIS'].isin(['I6049513','inc     '])
                tab = tab.loc[~problemes,:]
                tab['CIS'].astype(int)

            if output is None:
                output = tab
                print "la première table est " + name + " , son nombre de ligne est " + str(len(output))
            else:
                output = output.merge(tab, how='outer', on='CIS', suffixes=('', name[:-4]))
                if CIP_not_null:
                    if 'CIP7' in output.columns:
                        output = output[output['CIP7'].notnull()]
                print "après la fusion avec " + name + " la base mesure " + str(len(output))
    return output

if __name__ == '__main__':
#table = load_medic_gouv(maj_bdm, ['Etat','Date_AMM','CIP7','Label_presta','Date_declar_commerc','Taux_rembours','Prix','Id_Groupe','Type',
#                                  'indic_droit_rembours', 'Statu_admin_presta','Element_Pharma','Code_Substance','Nom_Substance','Dosage',
#                                  'Ref_Dosage','Nature_Composant','Substance_Fraction'])
#     test = load_medic_gouv(maj_bdm)
    table = load_medic_gouv(maj_bdm, ['CIP7', 'Label_presta',
                                      'Element_Pharma','Code_Substance','Nom_Substance','Dosage',
                                      'Ref_Dosage','Nature_Composant','Substance_Fraction'])

    # TODO: on a des problème de ref dosage.
    table = table[table['Ref_Dosage'].notnull()]
    table = table[table['Dosage'].notnull()]
    table = table[table['CIS'] != 67861550] #On retire l'oxygène dont la dose est
    table = table[~table['Element_Pharma'].isin(['pansement', 'gaz'])]
    # illisible, 2. c'est un gaz

    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('un ','')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('une ','')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('1ml','1 ml')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('L','l')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace("\(s\)".decode('utf8').encode('cp1252'),'')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace(',','.')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('100. 0 g','100.0 g')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('00ml','00 ml')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('1g','1 g')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('1ml','1 ml')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('ml</p>'.decode('utf8').encode('cp1252'), 'ml')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('comrpimé'.decode('utf8').encode('cp1252'),'comprimé '.decode('utf8').encode('cp1252'))
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('comprimer'.decode('utf8').encode('cp1252'),'comprimé '.decode('utf8').encode('cp1252'))
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('comprimé.'.decode('utf8').encode('cp1252'),'comprimé '.decode('utf8').encode('cp1252'))
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('comprimpé'.decode('utf8').encode('cp1252'),'comprimé '.decode('utf8').encode('cp1252'))
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('gelule'.decode('utf8').encode('cp1252'),'gélule'.decode('utf8').encode('cp1252'))
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('gélulle'.decode('utf8').encode('cp1252'),'gélule'.decode('utf8').encode('cp1252'))
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('gramme','g')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('récipent'.decode('utf8').encode('cp1252'),'récipient'.decode('utf8').encode('cp1252'))


    # TODO: identifier d'où viennent les label nuls
    table = table[table['Label_presta'].notnull()]
    table['Label_presta'] = table['Label_presta'].str.replace(',','.')
    table['Label_presta'] = table['Label_presta'].str. \
        replace("\(s\)".decode('utf8').encode('cp1252'), '')
    # 1 seul cas, qui n'est pas grave car flacon
    table['Label_presta'] = table['Label_presta'].str.replace('1 1','1')
    table['Label_presta'] = table['Label_presta'].str.replace('00 00','0000')
    table['Label_presta'] = table['Label_presta'].str.replace( '1500 m','0 ml')
    table['Label_presta'] = table['Label_presta'].str.replace( 'PVC-aluminium de 10','VC-aluminium de 10 comprimés')


    table['Dosage'] = table['Dosage'].str.replace(' 000 ', '000 ')
    table['Dosage'] = table['Dosage'].str.replace(' 000 ', '000 ') #il faut le faire 2 fois
    table['Dosage'] = table['Dosage'].str.replace('7 500', '7500')
    table['Dosage'] = table['Dosage'].str.replace('4 500', '4500')
    table['Dosage'] = table['Dosage'].str.replace('3 500', '3500')
    table['Dosage'] = table['Dosage'].str.replace('2 500', '2500')
    table['Dosage'] = table['Dosage'].str.replace('1 500', '1500')
    table['Dosage'] = table['Dosage'].str.replace('1 200', '1200')
    table['Dosage'] = table['Dosage'].str.replace('3 700', '3700')
    table['Dosage'] = table['Dosage'].str.replace(',', '.')
    table['Dosage'] = table['Dosage'].str.replace('\. ', '.')

    nom = table['Label_presta']
    dose = table['Ref_Dosage']
    both = table[['Ref_Dosage','Label_presta', 'Dosage']]

    unite_standard = ['ml', 'mg', 'litre']
    element_standard = ['comprimé', 'gélule', 'capsule', 'flacon', 'ampoule',
                        'dispositif', 'lyophilisat', 'pastille', 'seringue',
                        'sachet-dose', 'suppositoire', 'dose', 'ovule',
                        'sachet', 'gomme', 'tube', 'bâton', 'creuset', 'insert',
                        'récipient', 'poche', 'cartouche', 'pression', 'film',
                        'cm\^2', 'générateur', 'stylo', 'emplâtre',
                        'goutte', 'anneau', 'éponge', 'pâte', 'compresse',
                        'implant', 'récipient', 'pot', 'bouteille', 'unité',
                        'pilule']
                        # 'mole',  pour les gaz
                #contenants = ['plaquette','flacon','tube', 'récipient', 'sachet',
    #              'cartouche', 'boite', 'pochette', 'seringue', 'poche',
    #              'pilulier', 'ampoule', 'pot', 'stylo', 'film', 'inhalateur',
    #              'bouteille', 'vaporateur', 'enveloppe', 'générateur',
    #              'boîte', 'aquette', 'sac', 'pompe', 'distributeur',
    #              'applicateur', 'fût'
    #              ]
    element_standard = [x.decode('utf8').encode('cp1252') for x in element_standard]

    def coupe(serie):
        qte = np.zeros((len(serie), 8), dtype=float)
        unit = np.zeros((len(serie), 8), dtype=np.dtype('a20'))
        for i, label in enumerate(serie):
            k = 0
            chaine = label.split()
            # Pour le premier mot, si c'est un nom, on le met en contenant
            s = chaine[0]
            mem = False
            try:
                qte[i,k] = float(s)
                mem = True
            except:
                qte[i,k] = 1
                unit[i,k] = s
                if s[-1] == 's':
                    unit[i,k] = s[:-1]
                k += 1
            for s in chaine[1:]:
                if mem:
                    unit[i,k] = s
                    if s[-1] == 's':
                        unit[i,k] = s[:-1]
                    if s in ['g','l']:
                        unit[i,k] = 'm' + s
                        qte[i,k] = 1000*qte[i,k]
                    try: # 1 seul cas, qui n'est pas grave car flacon, corrigé plus haut par '0 0' <- '00'
                        test = float(s)
                        print i, label
                        pdb.set_trace()
                    except:
                        pass
                    k += 1
                    if s == 'compartiments':
                        k -= 1
                        unit[i,k] = ''
                        qte[i,k] = 0
                    mem = False
                try: # si c'est un entier, on a mem=True pour aller cherche l'unité
                # le mot d'après
                    qte[i,k] = float(s)
                    mem = True
                except:
                    pass
        unit = pd.DataFrame(unit, index=serie.index)
        qte = pd.DataFrame(qte, index=serie.index)
        return qte, unit

    qte, unit = coupe(table['Label_presta'])
    qte_dose, unit_dose =  coupe(table['Ref_Dosage'])
    qte_dosage, unit_dosage =  coupe(table['Dosage'])

    test = (unit_dose.loc[:,1] != '').copy()
    unit_dose.loc[:,1][~unit_dose.loc[:,1].isin(['','mg','ml'])]
    dose_en_unite = unit_dose.loc[:,0]*unit_dose.loc[:,0].isin(unite_standard) + \
        unit_dose.loc[:,1]*unit_dose.loc[:,1].isin(unite_standard) + \
        unit_dose.loc[:,2]*unit_dose.loc[:,2].isin(unite_standard)
    dose_en_element = unit_dose.loc[:,0]*unit_dose.loc[:,0].isin(element_standard) + \
        unit_dose.loc[:,1]*unit_dose.loc[:,1].isin(element_standard) + \
        unit_dose.loc[:,2]*unit_dose.loc[:,2].isin(element_standard)


    assert sum((dose_en_element == '') & (dose_en_unite == '')) == 0
    #test = (dose_en_element == '') & (dose_en_unite =='')
    #print  sum(test)
    #print unit_dose[test]
    #table['Ref_Dosage'][test]
    #pdb.set_trace()
    assert qte_dose.loc[:,2].max() == 0
    test = (qte_dose.loc[:,1] > 0).copy()
    assert qte_dose.loc[test,0].min() == qte_dose.loc[test,0].max() == 1
    qte_dose_finale = qte_dose.loc[:,0]
    qte_dose_finale.loc[test] = qte_dose.loc[test, 1]
    test = (dose_en_element != '').copy()
    assert qte_dose.loc[test, 0].max() == 1
    assert qte_dose.loc[test, 0].min() == 1
    ## étude sur les noms contentant un ";"
    ## C'est des boites et on peut multiplier sereinement
    # nom[nom.str.contains(';')]
    # étude sur les noms contentant un "+"
    # Pas de problème non plus, c'est entre parenthèse
    # le seul souci c'est pour les comprimés roses + jaunes
    #nom[nom.str.contains('\+')]
    # avec les "et" c'est plus compliqué, on verra plus tard.
    # TODO:
    #nom[nom.str.contains(' et ')]


    to_do = pd.Series(index=table.index, dtype=bool)
    dosage_boite = pd.Series(index=table.index, dtype=float)

    ### on commence par les unités standards, là on sait que
    # l'on doit tout prendre dans les quantités.
    concern_label_unite = pd.Series('', index=table.index)
    concern_dosage_unite = pd.Series(False, index=table.index, dtype=bool)
    for col in range(8):
        en_unite = (dose_en_unite == unit.loc[:,col]) & (dose_en_unite != '')
        concern_dosage_unite[en_unite] = True


    qte_for_unit = qte.replace(0, 1)
    dosage_boite = qte_for_unit.product(axis=1)
    dosage_boite = dosage_boite/qte_dose_finale
    dosage_boite[~concern_dosage_unite] = np.nan

    value_dosage_element = pd.Series(1, index=table.index, dtype=float)
    concern_dosage_element = pd.Series(False, index=table.index, dtype=bool)
    #il faut lire ce qu'il y a devant:
    # 4 ampoule de 3 ml, ça fait pas 12 ampoule.
    # TODO: si on a un "et" il faut ajouter et pas multiplier
    for col in range(8):
        cond_to_add = (~concern_dosage_element) & (~unit.loc[:, col].isin(unite_standard))
        value_dosage_element[cond_to_add] = (value_dosage_element*qte.loc[:, col])[cond_to_add]
        concern_dosage_element = concern_dosage_element | \
            (dose_en_element == unit.loc[:, col]) & (dose_en_element != '')

    pdb.set_trace()
    test = (value_dosage_element[concern_dosage_element]).copy()
    assert test.min() == 1
    assert all(test - test.astype(int) == 0) # on a que des entiers

    double_info = (concern_dosage_element) & (concern_dosage_unite)
    zero_info = (~concern_dosage_element) & (~concern_dosage_unite)
    print('on a un conflit pour :' + str(sum(double_info)) + ' entités')
    print("on n'a pas d'info pour :" + str(sum(zero_info)) + ' entités')

    prob_double_info = value_dosage_element[double_info] != dosage_boite[double_info]
    #both[double_info][prob_double_info]
    #value_dosage_element[double_info][prob_double_info]
    #dosage_boite[double_info][prob_double_info]
    ## on prend les valeurs de unit parce que parfois la référence est une
    # seringue de 1 ml alors que le label c'est des seringues de 1,7 ml...
    index_prob = zero_info[zero_info].index
    unit[zero_info]
    unit_dose[zero_info]
    label_en_mg = pd.Series(False, index=index_prob)
    label_en_ml = pd.Series(False, index=index_prob)
    dosage_en_mg = pd.Series(False, index=index_prob)
    dosage_en_ml = pd.Series(False, index=index_prob)
    for col in range(8):
        label_en_mg[unit.loc[zero_info, col] == 'mg'] = True
        label_en_ml[unit.loc[zero_info, col] == 'ml'] = True
        dosage_en_mg[unit_dose.loc[zero_info, col] == 'mg'] = True
        dosage_en_ml[unit_dose.loc[zero_info, col] == 'ml'] = True
    assert (dosage_en_ml & label_en_ml).sum() == 0
    assert (dosage_en_mg & label_en_mg).sum() == 0
    cond1 = (dosage_en_mg & label_en_ml)
    cond2 = (dosage_en_ml & label_en_mg)
    rien_a_faire = cond1 | cond2
    autres = zero_info & ~rien_a_faire
    # compliqué....

    table['nb_dose'] = value_dosage_element
    table.loc[concern_dosage_unite, 'nb_dose'] = dosage_boite[concern_dosage_unite]
    table = table[~zero_info]


    qte_dosage.apply(max)
    deux_nom = unit_dosage.loc[:,1] != ''
    sum(deux_nom)
    #on prend le premier nom et puis c'est tout.
    unit_dosage.loc[:,1].value_counts()



    test = (value_dosage_element < 1)
    both[test][concern_dosage_element]
    dosage_boite = dosage_boite/np.maximum(qte_dose.loc[:,1], qte_dose.loc[:,0])
    dosage_boite[~concern_dosage_unite] = np.nan


    prob_unite = (~concern_dosage_unite) & (dose_en_unite != '')
    vrai_prob_unite = (concern_dosage_unite != concern_label_unite) & (concern_dosage_unite != '')
    faux_prob_unite = prob_unite & ~vrai_prob_unite #-> on verra comment les supprimer

    # On travaille maintenant sur les autres
    # ici, il faut reprérer la position de l'élément pour ne prendre que lui:
    #il faut lire ce qu'il y a devant:
    # 4 ampoule de 3 ml, ça fait pas 12 ampoule.
    concern_label_element = pd.Series('', index=table.index)
    concern_dosage_element = pd.Series('', index=table.index)
    for col in range(8):
        in_standard = unit.loc[:,col].isin(element_standard)
        concern_label_element[in_standard] = unit.loc[:,col][in_standard]
        in_standard = unit_dose.loc[:,col].isin(element_standard)
        concern_dosage_element[in_standard] = unit_dose.loc[:, col][in_standard]

    prob_element = concern_dosage_element != concern_label_element
    vrai_prob_element = (concern_dosage_element != concern_label_element) & \
                (concern_dosage_element != '')
    faux_prob_element = prob_element & ~vrai_prob_element #-> on verra comment les supprimer

    print sum(prob_element)
    print sum(vrai_prob_element)

    #test = unit.loc[:,1].isin(unite_standard + element_standard + [''])
    #unit.loc[~test,1]

    #print('on a ' + str(avant - sum(to_do)) + ' medicament exprimés en' + unite)



    # si le dosage est en litre, ou gramme, on regarde si on a ça.
    unite_standard = [' l', ' ml', ' g', ' mg']
    element_standard = [' comprimé', ' gélule', ' capsule', ' flacon', ' ampoule',
                        ' dispositif', ' lyophilisat', ' pastille', ' seringue',
                        ' sachet-dose', ' suppositoire']
    for unite in element_standard + unite_standard:
        avant = sum(to_do)
        if unite in element_standard:
            unite = unite.decode('utf8').encode('cp1252')
            concern = unit['Ref_Dosage'].str.contains(unite[1:])
        if unite in unite_standard:
            concern = unit['Ref_Dosage'].str.contains(unite)
        for col in range(8):
            futur_to_do = (unit.iloc[:,col] == unite[1:]) & (concern)
            to_do[futur_to_do] = False
        print('on a ' + str(avant - sum(to_do)) + ' medicament exprimés en' + unite)

    # on peut multiplier les quantité pour avoir le volume ou masse total:
    qte_unit = qte[to_do].replace(0, 1)
    qte_unit.product(axis=1)
    np.maximum(qte_dose.loc[:,1], qte_dose.loc[:,0])


    #contenants = ['plaquette','flacon','tube', 'récipient', 'sachet',
    #              'cartouche', 'boite', 'pochette', 'seringue', 'poche',
    #              'pilulier', 'ampoule', 'pot', 'stylo', 'film', 'inhalateur',
    #              'bouteille', 'vaporateur', 'enveloppe', 'générateur',
    #              'boîte', 'aquette', 'sac', 'pompe', 'distributeur',
    #              'applicateur', 'fût'
    #              ]
