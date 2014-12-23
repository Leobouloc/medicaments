# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 11:51:46 2014

@author: debian
"""
import os
import pandas as pd
from bs4 import BeautifulSoup

from CONFIG import path_BDM_scrap


def _contains(tab, _list):
    '''Renvoie true si le texte du tableau contient tous les strings de la liste'''
    return all([x in tab.text for x in _list])

def get_tab_colon(all_tables, _list, len_assert=True):
    '''Renvoie un tableau selectionné par ses colonnes (à valeurs dans _list)'''
    return_tab = [tab for tab in all_tables if _contains(tab, _list)]
    if len_assert:
        assert len(return_tab) == 1 ## On s'assure que l'on a qu'une seule table qui vérifie les criteres
    return_tab= return_tab[0]
    return_tab = pd.io.html.read_html(str(return_tab))[0]
    return_tab = pd.DataFrame([list(return_tab[2])], columns = return_tab[0])
    return return_tab


def get_tab(all_tables, _list, len_assert=True):
    '''Renvoie un tableau selectionné par ses colonnes (à valeurs dans _list)'''
    return_tab = [tab for tab in all_tables if _contains(tab, _list)]
    if len_assert:
        assert len(return_tab) == 1
    return_tab= return_tab[0]
    return_tab = pd.io.html.read_html(str(return_tab), header = False)[0]
    return return_tab


def get_val(all_fonts, _list):
    '''Renvoie un tableau selectionné par ses colonnes (à valeurs dans _list)'''
    def _contains(font, _list):
        '''Renvoie true si le texte du font contient tous les strings de la liste'''
        return all([x in font.text for x in _list])
    return_font = [font for font in all_fonts if _contains(font, _list)]
    assert len(return_font) == 2
    return_font = str(return_font[0]).split('<br/>')[1:-1]
    return_font = [x.replace('\r', '') for x in return_font]
    return_font = [x.replace('\n', '') for x in return_font]
    return return_font



def parse(file):
    
    ### START : Load du texte contenant l'information
    with open (file, "r") as myfile:
        data = myfile.read()  
    soup = BeautifulSoup(data)
    test = soup.find_all('table')
    corps = soup.findAll('td', {'colspan':'4'})[1].find('table')
    all_tables = corps.findAll('table')
    all_fonts = corps.findAll('font')
    ### END : Load du texte contenant l'information

    ##############"
    
    #### START : Table presentation
    table_presentation = get_tab_colon(all_tables, ['Code CIP 13 ', 'Code CIP 7'])
    import pdb
    pdb.set_trace()
    table_presentation.columns = ['CIP', 'CIP_7', 'designation', 'description']
    
    #### START : Table presentation
    _list = ['Code CIP', 'ment de nom']
    table_infos = get_tab_colon(all_tables, _list)
    table_infos.columns = ['CIP_', 'specialite', 'complement_de_nom']
    
    
    #### START : Table forme
    _list = ['Forme Pharmaceutique', 'Info compl']
    table_forme = get_tab_colon(all_tables, _list)
    
    columns = table_forme.columns
    #def _lambda_columns(x):
    #    if isinstance(x, float):
    #        return 'NaN'
    #    else:
    #        return x
    #columns = [_lambda_columns(col) for col in table_forme.columns]
    #table_forme.columns = columns
    #columns_to_merge = [col for col in table_forme.columns if ('NaN' in col or 'Info' in col)]
    
    ##### START : Table voie d'administration
    _list = ["Voie d'administration 1"]
    table_voie = get_tab_colon(all_tables, _list)
    table_voie.columns = ['voie_administration_1']
    
    ##### START : Table chemical 1
    _list = ["Substance Active", "CAS"]
    table_chemical_1 = get_tab(all_tables, _list)
    table_chemical_1.columns = ['substance_active', 'cas']
    
    ##### START : Table chemical 2
    _list = ["Substance Active", "Dosage", "Dosage Base"]
    table_chemical_active = get_tab(all_tables, _list)
    table_chemical_active.columns = ['substance_active', 'dosage', 'dosage_base']
    table_chemical_active['active'] = True
    
    ##### START : Table chemical 4
    #### ATTENTION : il peut y en avoir plusieurs
    _list = ["Substance Auxiliaire", "Dosage", "Nature", "Classe chimique", "Voie"]
    table_chemical_aux = get_tab(all_tables, _list, len_assert = False)
    table_chemical_aux.columns = ['substance_aux', 'dosage', 'nature', 'classe_chimique', 'voie', 'vecteur']
    table_chemical_aux['active'] = False    
    
    #### START : Values 
    _list = ["Classe ATC de la Substance Active"]
    classe_atc = get_val(_list)[0]
    
    #### START : Statut de remboursement
    table_rembourement = str(get_tab(all_tables, ['Statut de remboursement']))
    
    #### START : table posologie
    table_posologie = str(get_tab(all_tables, ["Seuil d'alerte"]))
    
    #### START :  SMR
    smr = get_tab(all_tables, ['Service m', 'dical rendu'])
    
    ligne = pd.tools.merge.concat([table_presentation, table_infos, table_voie, smr], axis = 1)
    ligne['statut_remboursement'] = table_rembourement
    ligne['seuils_alerte'] = table_posologie
    
    tab = pd.tools.merge.concat([table_chemical_active, table_chemical_aux])
    tab.index = range(len(tab))

    # TODO: a changer
    for col in ligne.columns:
        tab[col] = ligne[col].iloc[0]

    return tab
    
if __name__ == '__main__':
    list_cip = os.listdir(path_BDM_scrap + '/cip')
    for file in list_cip:
        file_name = os.path.join(path_BDM_scrap + '/cip', file)
        tab = parse(file_name)