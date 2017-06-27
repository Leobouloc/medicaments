# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 11:51:46 2014

@author: debian
"""
import os
import pdb
import pandas as pd
from bs4 import BeautifulSoup

from CONFIG import path_BDM_scrap


def _contains(tab, _list):
    '''Renvoie true si le texte du tableau contient tous les strings de la liste'''
    return all([x in tab.text for x in _list])

def get_tab_colon(all_tables, _list, columns=None, len_assert=True):
    '''Renvoie un tableau selectionné par ses colonnes (à valeurs dans _list)'''
    tabs = [tab for tab in all_tables if _contains(tab, _list)]
    if not tabs:
        return pd.DataFrame(columns=columns)
    if len_assert:
        assert len(tabs) == 1
#        try:
#            assert len(tabs) == 1 ## On s'assure que l'on a qu'une seule table qui vérifie les criteres
#        except:
#            pdb.set_trace()
    temp = tabs[0]
#    try:
    return_tab = pd.io.html.read_html(str(temp))[0]
    return_tab = pd.DataFrame([list(return_tab[2])], columns = return_tab[0])
    if columns:
        return_tab = return_tab.iloc[:, :len(columns)]
        return_tab.columns = columns
#    except:
#        pdb.set_trace()
    return return_tab


def get_tab(all_tables, _list, columns=None, len_assert=True):
    '''Renvoie un tableau selectionné par ses colonnes (à valeurs dans _list)'''
    tabs = [tab for tab in all_tables if _contains(tab, _list)]
    if not tabs:
        return pd.DataFrame(columns=columns)

    return_tab = None
    for temp in tabs:
        tab = pd.io.html.read_html(str(temp), header = 0)[0]
        tab.columns = [str(x) for x in tab.columns]
        if all([any([x in col for col in tab.columns])  for x in _list]):
            if return_tab is None:
                return_tab = tab
            else:
                return_tab = return_tab.append(tab)

    if columns != None:
        return_tab.columns = columns
    return return_tab

def get_tab_verticale(all_tables, _list, columns=None, len_assert=True):
    '''pour les tables sans entêtes à deux colonnes'''
    tabs = [tab for tab in all_tables if _contains(tab, _list)]
    if not tabs:
        return pd.DataFrame(columns=columns)

    return_tab = None
    for temp in tabs:
        tab = pd.io.html.read_html(str(temp), header = None)[0]
        tab = tab.T
        tab.columns = tab.iloc[0]
        tab = tab[1:]
        tab.index = [0]
        tab.columns = [str(x) for x in tab.columns]
        if all([any([x in col for col in tab.columns])  for x in _list]):
            if return_tab is None:
                return_tab = tab
            else:
                return_tab = return_tab.append(tab)
    if columns != None:
        return_tab.columns = columns
    return return_tab



def get_val(all_fonts, _list, columns=None):
    '''Renvoie une valeur selectionnée par ses colonnes (à valeurs dans _list)'''
    return_font = [font for font in all_fonts if _contains(font, _list)]
#    try:
    assert len(return_font) == 2
#    except:
#        return_font = [font for font in all_fonts if _contains(font, 'Classe ATC')]
#        print 'probleme ici pour le code ATC'
#        print ' #TODO: '
#        pass
#        pdb.set_trace()
#
    return_font = str(return_font[0]).split('<br/>')[1:-1]
    return_font = [x.replace('\r', '') for x in return_font]
    return_font = [x.replace('\n', '') for x in return_font]
    if columns:
        return_font.columns = columns
    return return_font


def _real_parse(data):
    ''' parse la soup issue d'un html'''
    soup = BeautifulSoup(data)
    corps = soup.findAll('td', {'colspan': '4'})[1].find('table')
    all_tables = corps.findAll('table')
    all_fonts = corps.findAll('font')

    table_presentation = get_tab_colon(all_tables,
                                       ['Code CIP 13 ', 'Code CIP 7'],
                                       ['CIP', 'CIP_7', 'designation', 'description'])

    # Table presentation
    table_infos = get_tab_colon(all_tables,
                                ['Code CIP', 'ment de nom'],
                                ['CIP_', 'specialite', 'complement_de_nom']
                                )


    # Table forme
    table_forme = get_tab_colon(all_tables,
                                ['Forme Pharmaceutique 1', 'Info compl'],
                                ['Forme Pharmaceutique', 'Info compl']
                                )

    # Table dates
    table_date_commercialistation = get_tab_verticale(all_tables, ['Commercialisation'])
    table_date_aggrement = get_tab_verticale(all_tables, ['Date d', 'ment collectiv'])
    table_date_premiere_inscription = get_tab_verticale(all_tables, ['Date de premi', 're inscription s'])

    # Table voie d'administration
    table_voie = get_tab_colon(all_tables,
                               ["Voie d'administration 1"],
                               ['voie_administration_1'])

    # Table chemical 1
    list_fluticason = ['3400926648794', '3400926648855']
    if all([cip not in table_presentation['CIP'].values for cip in list_fluticason]):
        table_chemical_1 = get_tab(all_tables,
                                   ["Substance Active", "CAS"],
                                   ['substance_active_inutile', 'cas'])
    else:
        table_chemical_1 = pd.DataFrame(index = [0],
                                        columns = ['Substance Active', 'CAS'])
        table_chemical_1.iloc[0, :] = ['FLUTICASONE PROPIONATE', 'Â']
    # Table chemical 2
    table_chemical_active = get_tab(all_tables,
                                    ["Substance Active", "Dosage", "Dosage Base"],
                                    ['substance_active', 'dosage', 'dosage_base'])
    table_chemical_active['active'] = True

    # Table chemical 4
    #   ATTENTION : il peut y en avoir plusieurs
    table_chemical_aux = get_tab(all_tables,
                                 ["Substance Auxiliaire", "Dosage", "Nature", "Classe chimique", "Voie"],
                                 ['substance_aux', 'dosage', 'nature', 'classe_chimique', 'voie', 'vecteur'],
                                 len_assert = False)

    #### START : Values
#    _list = ["Classe ATC de la Substance Active"]
#    classe_atc = get_val(all_fonts, ["Classe ATC de la Substance Active"])[0]
    ####  Cas ou l'on n'a qu'une classe ATC
    for font in all_fonts:
        if 'Classe ATC :' in font.text:
            break
    try:
        code_ATC = font.next_sibling.next_sibling.text
    except:
        ####  Cas ou l'on a plusieurs classes ATC
        #### ATTENTION : non géré : penser à la gestion des données (CIP ex : 3400931713869)
        for font in all_fonts:
            if 'Classe ATC de la Substance Active' in font.text:
                break
        code_ATC = font.text.split('\n')[2:-1]


    ## Labo
    laboratoire = ''
    for font in all_fonts:
        if 'Laboratoire :' in font:
            laboratoire = font.next_sibling.next_sibling.next_sibling.next_sibling.text
            break

    ### Labo exploitant
    laboratoire_exploitant = ''
    for font in all_fonts:
        if 'Laboratoire exploitant :' in font:
            laboratoire_exploitant = font.next_sibling.next_sibling.next_sibling.next_sibling.text
            break


    #### START : Statut de remboursement
    try:
        table_rembourement = str(get_tab(all_tables, ['Statut de remboursement']))
    except:
        table_rembourement = str(get_tab(all_tables, ['Statut de remboursement : ']))

    #### START : table posologie
    table_posologie = str(get_tab(all_tables, ["Seuil d'alerte"]))

    #### START :  SMR
    smr = get_tab(all_tables, ['Service m', 'dical rendu'])

    ligne = pd.tools.merge.concat([table_presentation, table_infos, table_voie, smr,
                                   table_forme, table_chemical_1, table_date_commercialistation, table_date_premiere_inscription,
                                   table_date_aggrement], axis = 1)
    ligne['statut_remboursement'] = table_rembourement
    ligne['seuils_alerte'] = table_posologie

    if isinstance(code_ATC, str):
        ligne['classe_atc'] = code_ATC

    ligne['labo'] = laboratoire
    ligne['labo_exploitant'] = laboratoire_exploitant


    tab = pd.tools.merge.concat([table_chemical_active, table_chemical_aux])
    tab.index = range(len(tab))

    for col in ligne.columns:
        tab[col] = ligne[col].iloc[0]

    return tab


def parse(file, no_chance=False):

    # Load du texte contenant l'information
    with open(file, "r") as myfile:
        data = myfile.read()

    if no_chance:
        return _real_parse(data)

    if data.count('Warning') > 20:
        warning += [file]
        return

    try:
        return _real_parse(data)
    except:
        problem += [file]
        pass


def parse_list(list_cip, no_chance=False):
    table = None
    i = 0
    problem = []
    warning = []
    for file in list_cip:
        i += 1
        if i % 100 == 0:
            print 'on en a fait', i
        file_name = os.path.join(path_BDM_scrap, 'cip', file)

        # Load du texte contenant l'information
        with open(file_name, "r") as myfile:
            data = myfile.read() #.encode('utf8')

        if no_chance:
            if table is None:
                table = _real_parse(data)
            else:
                table = table.append(_real_parse(data))
        else:
            if data.count('Warning') > 20:
                warning += [file]
            else:
                try:
                    if table is None:
                        table = _real_parse(data)
                    else:
                        table = table.append(_real_parse(data))
                except:
                    problem += [file]
                    pass
#        try:
#            if table is not None:
#                table.to_csv('just.csv', encoding='utf8')
#        except:
##            print table.iloc[-1,:]
#            print table.iloc[-1, :]
#            pdb.set_trace()

    return table, warning, problem


def cip_from_file_name(file_name):
    '''Renvoie le numero de cip en prenant le path d Alexis '''
#    file_name = file_name.replace('D:\\data\\Medicament\\BDM\\/cip\\', '')
#    file_name = file_name.replace('C:\\Users\\work\\Documents\\Etalab_data\\AFM\\BDM_scrap', '')
    cip = os.path.split(file_name)[-1]
    cip = cip.replace('.html', '')
    return cip


if __name__ == '__main__':
    list_cip = os.listdir(os.path.join(path_BDM_scrap, 'cip'))
    table, warning, problem = parse_list(list_cip)

    with open(os.path.join(path_BDM_scrap, 'problem.txt'), "w") as myfile:
        myfile.write(";".join(problem))

    with open(os.path.join(path_BDM_scrap + 'warning.txt'), "w") as myfile:
        myfile.write(";".join(warning))

#    ## Probleme
#    with open (path_BDM_scrap + 'problem.txt', "r") as myfile:
#        problems = myfile.read().split(';')

    for col in table.columns:
        table[col] = table[col].str.encode('utf-8')
    filename = os.path.join(path_BDM_scrap, 'without_prob_all.csv')
    table.to_csv(filename, sep=';', encoding='utf-8')
    filename = os.path.join(path_BDM_scrap, 'without_prob_with_dose.csv')
    table[table.dosage != '-'].to_csv(filename, sep=';', encoding='utf-8')
