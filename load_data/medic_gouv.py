# -*- coding:cp1252 -*-

'''
Created on 26 juin 2014
'''
import pandas as pd
import numpy as np
import re
import os
import pdb

pd.set_option('max_colwidth', 100)

from CONFIG import path_gouv
# Derniere mise � jour BDM
maj_bdm = 'maj_20140915122241'


dico_variables = dict(
    bdpm=['CIS', 'Nom', 'Forme', 'Voies', 'Statut_AMM', 'Type_AMM', 'Etat',
          'Date_AMM', 'Statut_BDM', 'Num_Europe', 'Titulaires', 'Surveillance'],
    CIP_bdpm=['CIS', 'CIP7', 'Label_presta', 'Statu_admin_presta',
              'etat_commercialisation', 'Date_declar_commerc', 'CIP13',
              'aggrement_collectivites', 'Taux_rembours', 'Prix',
              'indic_droit_rembours'],
    GENER_bdpm=['Id_Groupe', 'Nom_Groupe', 'CIS', 'Type', 'Num_Tri'],
    COMPO_bdpm=['CIS', 'Element_Pharma', 'Code_Substance', 'Nom_Substance',
                'Dosage', 'Ref_Dosage', 'Nature_Composant',
                'Substance_Fraction'],
    HAS_SMR_bdpm=['CIS', 'HAS', 'Evalu', 'Date', 'Valeur_SMR', 'Libelle_SMR'],
    HAS_ASMR_bdpm=['CIS', 'HAS', 'Evalu', 'Date', 'Valeur_ASMR',
                   'Libelle_ASMR'],
    )

unite_standard = ['ml', 'mg', 'litre']
element_standard = [u'comprim�', u'g�lule', u'capsule', u'flacon', u'ampoule',
                    u'dispositif', u'lyophilisat', u'pastille', u'seringue',
                    u'sachet-dose', u'suppositoire', u'dose', u'ovule',
                    u'sachet', u'gomme', u'tube', u'b�ton', u'creuset', u'insert',
                    u'r�cipient', u'poche', u'cartouche', u'pression', u'film',
                    u'cm^2', u'g�n�rateur', u'stylo', u'empl�tre',
                    u'goutte', u'anneau', u'�ponge', u'p�te', u'compresse',
                    u'implant', u'r�cipient', u'pot', u'bouteille', u'unit�',
                    u'pilule', u'seringue pr�remplie']
                    # u'mole',  pour les gaz
            #contenants = ['plaquette','flacon','tube', 'r�cipient', 'sachet',
#              'cartouche', 'boite', 'pochette', 'seringue', 'poche',
#              'pilulier', 'ampoule', 'pot', 'stylo', 'film', 'inhalateur',
#              'bouteille', 'vaporateur', 'enveloppe', 'g�n�rateur',
#              'bo�te', 'aquette', 'sac', 'pompe', 'distributeur',
#              'applicateur', 'f�t'
#              ]
element_standard = [x.encode('cp1252') for x in element_standard]


def recode_dosage(table):
    assert 'Dosage' in table.columns
    table = table[table['Dosage'].notnull()].copy()
    table['Dosage'] = table['Dosage'].str.replace(' 000 ', '000 ')
    # il faut le faire 2 fois
    table['Dosage'] = table['Dosage'].str.replace(' 000 ', '000 ')
    table['Dosage'] = table['Dosage'].str.replace('7 500', '7500')
    table['Dosage'] = table['Dosage'].str.replace('4 500', '4500')
    table['Dosage'] = table['Dosage'].str.replace('3 500', '3500')
    table['Dosage'] = table['Dosage'].str.replace('2 500', '2500')
    table['Dosage'] = table['Dosage'].str.replace('1 500', '1500')
    table['Dosage'] = table['Dosage'].str.replace('1 200', '1200')
    table['Dosage'] = table['Dosage'].str.replace('3 700', '3700')
    table['Dosage'] = table['Dosage'].str.replace(',', '.')
    table['Dosage'] = table['Dosage'].str.replace('\. ', '.')
    return table

def recode_prix(table):
    assert 'Prix' in table.columns
    table['Prix'] = table['Prix'].str.replace(',','.')
    #Enlever le premier point pour ceux qui en ont deux
    table.loc[table['Prix'].apply(lambda x: x.count('.'))>1,'Prix'] = table.loc[table['Prix'].apply(lambda x: x.count('.'))>1,'Prix'].str.replace('.','',1)
    table['Prix'] = table['Prix'].apply(lambda x: float(x))   
    return table

def recode_ref_dosage(table):
    # TODO: on a des probl�me de ref dosage.
    assert 'Ref_Dosage' in table.columns
    table = table[table['Ref_Dosage'].notnull()].copy()
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('un ','')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('une ','')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('1ml','1 ml')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('L','l')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace("\(s\)",'')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace(',','.')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('100. 0 g','100.0 g')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('00ml','00 ml')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('1g','1 g')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('1ml','1 ml')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('ml</p>', 'ml')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('comrpim�','comprim� ')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('comprimer','comprim� ')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('comprim�.','comprim� ')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('comprimp�','comprim� ')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('gelule','g�lule')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('g�lulle','g�lule')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('gramme','g')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('r�cipent','r�cipient')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('pr�-remplie' ,'pr�remplie')
    table['Ref_Dosage'] = table['Ref_Dosage'].str.replace('sachet dose', 'sachet-dose')
    table['Ref_Dosage'] = table['Ref_Dosage'].apply(recode_litre_en_ml)
    return table


def recode_PVC(chaine):
    if 'PVC' in chaine:
        try:
            int(chaine[-1])
            return chaine + ' comprim�'
        except:
            pass
    return chaine


def recode_litre_en_ml(chaine):
    chaine = chaine.replace('litres', 'litre')
    if chaine[-2:] == ' l':
        chaine = chaine + 'itre'
    if chaine[:5] == 'litre':
        chaine = '1 ' + chaine
    chaine = chaine.replace(' l ', ' litre ')
    if ' litre' in chaine:
        mots = chaine.split()
        idx_avant = mots.index('litre') - 1
        nombre = mots[idx_avant]
        try:
            nombre = float(nombre)
            nombre *= 1000
            mots[idx_avant] = str(nombre)
            chaine = ' '.join(mots)
        except:
            assert nombre == 'par'
        chaine = chaine.replace(' litre', ' ml')
        return chaine
    else:
        return chaine


def recode_label_presta(table):
    assert 'Label_presta' in table.columns
    # TODO: identifier d'o� viennent les label nuls
    table = table[table['Label_presta'].notnull()].copy()
    table['Label_presta'] = table['Label_presta'].str.replace(',', '.')
    table['Label_presta'] = table['Label_presta'].str. \
        replace("\(s\)", '')
    # 1 seul cas, qui n'est pas grave car flacon
    table['Label_presta'] = table['Label_presta'].str.replace('1 1', '1')
    table['Label_presta'] = table['Label_presta'].str.replace('00 00', '0000')
    table['Label_presta'] = table['Label_presta'].str.replace('  l', ' l')

    table['Label_presta'] = table['Label_presta'].apply(recode_litre_en_ml)
    table['Label_presta'] = table['Label_presta'].apply(recode_PVC)
    # un oubli du nombre de comprim�
    table['Label_presta'] = table['Label_presta'].str.replace(
        'plaquette thermoform�e PVC poly�thyl�ne PVDC aluminium comprim�',
        'plaquette thermoform�e PVC poly�thyl�ne PVDC aluminium 60 comprim�')
#    table['Label_presta'] = table['Label_presta'].str.replace('1 kg', '1000 g')
#    table['Label_presta'] = table['Label_presta'].str.replace('litres', 'litre')
#    table['Label_presta'] = table['Label_presta'].str.replace('5.0 l', '5000 ml')
#    table['Label_presta'] = table['Label_presta'].str.replace('2 l ', '2000 ml ')
#    table['Label_presta'] = table['Label_presta'].str.replace('\.5 l ', '500 ml ')
#    table['Label_presta'] = table['Label_presta'].str.replace('0.25 l ', '250 ml ')
#    # on a un cas avec des 2l � la fin
#    table['Label_presta'] = table['Label_presta'].str.replace('de 2 l', ' de 2000 ml')
#    table['Label_presta'] = table['Label_presta'].str.replace('1 f�t poly�thyl�ne de 5 l', '1 f�t poly�thyl�ne de 5000 ml')

    return table


def load_medic_gouv(maj_bdm, var_to_keep=None, CIP_not_null=False):
    ''' renvoie les tables fusionn�es issues medicament.gouv.fr
        si var_to_keep est rempli, on ne revoit que la liste des variables
    '''
    # chargement des donn�es
    output = None
    for name, vars in dico_variables.iteritems():
        # teste si on doit ouvrir la table
        if var_to_keep is None:
            intersect = vars
        if var_to_keep is not None:
            intersect = [var for var in vars if var in var_to_keep]
        if len(intersect) > 0:
            path = os.path.join(path_gouv, maj_bdm, 'CIS_' + name + '.txt')
            tab = pd.read_table(path, header=None)
            if name in ['COMPO_bdpm', 'GENER_bdpm']:
                tab = tab.iloc[:, :-1]
            tab.columns = vars
            tab = tab[['CIS'] + intersect]
            # correction ad-hoc...
            if tab['CIS'].dtype == 'object':
                problemes = tab['CIS'].str.contains('REP', na=False)
                problemes = problemes | tab['CIS'].isin(['I6049513', 'inc     '])
                tab = tab.loc[~problemes, :]
                tab['CIS'].astype(int)

            if 'Ref_Dosage' in intersect:
                tab = recode_ref_dosage(tab)
            if 'Dosage' in intersect:
                tab = recode_dosage(tab)
            if 'Label_presta' in intersect:
                tab = recode_label_presta(tab)
            if 'Prix' in intersect:
                tab = recode_prix(tab)
            if output is None:
                output = tab
                print("la premi�re table est " + name + " , son nombre de " +
                      "lignes est " + str(len(output)))
            else:

                output = output.merge(tab, how='outer', on='CIS',
                                      suffixes=('', name[:-4]))
                if CIP_not_null:
                    if 'CIP7' in output.columns:
                        output = output[output['CIP7'].notnull()]
                print("apr�s la fusion avec " + name + " la base mesure " +
                      str(len(output)))
    return output

#if __name__ == '__main__':
##table = load_medic_gouv(maj_bdm, ['Etat','Date_AMM','CIP7','Label_presta','Date_declar_commerc','Taux_rembours','Prix','Id_Groupe','Type',
##                                  'indic_droit_rembours', 'Statu_admin_presta','Element_Pharma','Code_Substance','Nom_Substance','',
##                                  'Ref_Dosage','Nature_Composant','Substance_Fraction'])
##     test = load_medic_gouv(maj_bdm)
#    table = load_medic_gouv(maj_bdm, ['CIP7', 'Label_presta',
#                                      'Element_Pharma','Code_Substance','Nom_Substance','Dosage',
#                                      'Ref_Dosage','Nature_Composant','Substance_Fraction'])
#
#    table = table[~table['Element_Pharma'].isin(['pansement', 'gaz'])]
#
#    for var in ['Ref_Dosage', 'Dosage', 'Label_presta']:
#        print table[var].isnull().sum()
#        table = table[table[var].notnull()]


def extract_quantity(label, reference):

    # TODO: douteux quand la r�f�rence apparait plusieurs fois
    # on ne garde que la partie avant la r�f�rence
    label = label[:label.index(reference)]
    # s'il y a un "et" ou un " - ", on ne prend que
    # la partie qui concerne la r�f�rence
    if " et " in label:
        label = label.split(' et ')[-1]
    if " - " in label:
        label = label.split(" - ")[-1]  
    floats = re.findall(r"[-+]?\d*\.\d+|\d+", label)
    floats = [float(x) for x in floats]
    if len(floats) == 0:
        return 1   
    return reduce(lambda x, y: x*y, floats)
#    except:
#        print label, reference
#        print row
#        pdb.set_trace()
#        pass
    
def table_update(table):
    
    nb_ref_in_label = np.zeros(len(table))
    incoherence_identifiee = []
    reconstitu = []
    i = -1
    for k, row in table[['Ref_Dosage', 'Dosage', 'Label_presta']].iterrows():
        # travail de base sur la r�f�rence
        i += 1
        
        #if i % 100 == 0:
            #print(" on en a fait " + str(i) )
        reference = row['Ref_Dosage']
            
        if not pd.isnull(reference):
            if reference[:2] == '1 ':
                reference = reference[1:]  # on laisse un espace parce que
                # si �a commence par 1 g, comme �a, �a passe le test avec unit
            ref_floats = re.findall(r"[-+]?\d*\.\d+|\d+", reference)
            if len(ref_floats) > 0:
                ref_floats = [float(x) for x in ref_floats]
                reference_dose = reduce(lambda x, y: x*y, ref_floats)
            else:
                reference_dose = 1
            # travail de base sur le label
            label = row['Label_presta']
            if label.split()[0] in element_standard:
                label = '1 ' + label
        
            if reference in label:
                # TODO: douteux quand la r�f�rence apparait plusieurs fois
                label_dose = extract_quantity(label, reference)
                nb_ref_in_label[i] = label_dose/reference_dose
        
            if nb_ref_in_label[i] == 0:
                for unite in ['ml', 'l', 'mg', 'g', 'dose', 'litre']:
                    if len(reference) >= len(unite) + 1:
                        if ' ' + unite + ' ' in reference or \
                           reference[-(len(unite) + 1):] == ' ' + unite or \
                           reference[:len(unite)] == unite :
                            if ' ' + unite in label:
                                nb_ref_in_label[i] = extract_quantity(label, ' ' + unite)
        
            if nb_ref_in_label[i] == 0:
                reference = row['Ref_Dosage']
                contenant = [var for var in element_standard
                             if var in reference]
                if len(contenant) == 1:
                    var = contenant[0]
                    if var in label:
                        label_dose = extract_quantity(label, var)
                        nb_ref_in_label[i] = label_dose
        
            if nb_ref_in_label[i] == 0:
                reference = row['Ref_Dosage']
                if reference in ['lyophilisat', '1 flacon', 'dose mesur�e']:
                    nb_ref_in_label[i] = extract_quantity(label, 'flacon')
        
            if nb_ref_in_label[i] == 0:
                reference = row['Ref_Dosage']
                if ((any(masse in reference for masse in ['g', 'mg']) and
                    any(vol in label for vol in ['l', 'ml'])) or
                    (any(masse in label for masse in ['g', 'mg']) and
                    any(vol in reference for vol in ['l', 'ml']))):
                    incoherence_identifiee += [i]
        
                elif reference == 'comprim�' and 'g�lule' in label:
                    nb_ref_in_label[i] = extract_quantity(label, 'g�lule')
                elif 'qsp' in row['Dosage']:
                    incoherence_identifiee += [i]
                elif reference == 'pression':
                    incoherence_identifiee += [i]
                elif 'Bq' in label:  # GBq, MBq
                    pass
                elif 'Bq' in row['Dosage']:  # GBq, MBq
                    pass
                elif reference == 'dose':
                    # TODO:
                    pass
                elif reference == 'sachet-dose' and 'sachet' in label:
                    nb_ref_in_label[i] = extract_quantity(label, 'sachet')
                elif reference == 'flacon de lyophilisat' and 'flacon' in label:
                    nb_ref_in_label[i] = extract_quantity(label, 'flacon')
                elif reference in ['ampoule ou flacon', 'flacon ou ampoule'] and 'flacon' in label:
                    nb_ref_in_label[i] = extract_quantity(label, 'flacon')
                elif reference in ['ampoule ou flacon', 'flacon ou ampoule'] and 'ampoule' in label:
                    nb_ref_in_label[i] = extract_quantity(label, 'ampoule')
                elif reference == 'ampoule de lyophilisat' and 'ampoule' in label:
                    nb_ref_in_label[i] = extract_quantity(label, 'ampoule')
                elif reference == 'empl�tre' and 'sachet' in label:
                    nb_ref_in_label[i] = extract_quantity(label, 'sachet')
                elif reference == 'dispositif cutan�' and 'sachet' in label:
                    nb_ref_in_label[i] = extract_quantity(label, 'sachet')
                elif reference == 'flacon' and 'r�cipient unidose' in label:
                    nb_ref_in_label[i] = extract_quantity(label, 'r�cipient')
                elif reference == 'flacon' and 'ampoule' in label:
                    nb_ref_in_label[i] = extract_quantity(label, 'ampoule')
                elif reference == '1 ml de solution reconstitu�e':
                    reconstitu += [i]
                elif 'sachet-dose n' in reference:
                    pass
                    # TODO: un truc avec les sachets-doses num�rot�s
                elif 'cm^2' in reference:
                    pass
                    # TODO: un truc avec les sachets-doses num�rot�s
                else:
                    pass
    return nb_ref_in_label
#            print('il faut tenter autre chose')
#            print(row)
#            pdb.set_trace()
