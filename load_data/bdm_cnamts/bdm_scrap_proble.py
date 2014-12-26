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
        try:
            assert len(tabs) == 1 ## On s'assure que l'on a qu'une seule table qui vérifie les criteres
        except:
            pdb.set_trace()
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
        tab = pd.io.html.read_html(str(temp), header = False)[0]
        if all([x in _list for x in tab.columns]):
            if return_tab is None:
                return_tab = tab
            else:
                return_tab = return_tab.append(tab) 
            
    try:
        if columns:
            return_tab.columns = columns
    except:
        for temp in tabs:
            print pd.io.html.read_html(str(temp), header = False)[0]      
      
        pdb.set_trace()
    return return_tab            



def get_val(all_fonts, _list, columns=None):
    '''Renvoie un tableau selectionné par ses colonnes (à valeurs dans _list)'''
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



def parse(file):
    global problem
    print file
    ### START : Load du texte contenant l'information
    with open (file, "r") as myfile:
        data = myfile.read()  

    ### END : Load du texte contenant l'information

    ##############"
    #### START : Table presentation

    soup = BeautifulSoup(data)
    if data.count('Warning') > 20:
        print 'on passe celui la'
        return
    test = soup.find_all('table')
    corps = soup.findAll('td', {'colspan':'4'})[1].find('table')
    all_tables = corps.findAll('table')
    all_fonts = corps.findAll('font')
    
#    pdb.set_trace()
    table_presentation = get_tab_colon(all_tables, 
                                       ['Code CIP 13 ', 'Code CIP 7'],
                                       ['CIP', 'CIP_7', 'designation', 'description'])
    
    #### START : Table presentation
    table_infos = get_tab_colon(all_tables, 
                                ['Code CIP', 'ment de nom'],
                                ['CIP_', 'specialite', 'complement_de_nom']
                                )
    
    
    #### START : Table forme
    table_forme = get_tab_colon(all_tables, 
                                ['Forme Pharmaceutique 1', 'Info compl'], 
                                ['Forme Pharmaceutique', 'Info compl']
                                )
    
    # columns = table_forme.columns
    #def _lambda_columns(x):
    #    if isinstance(x, float):
    #        return 'NaN'
    #    else:
    #        return x
    #columns = [_lambda_columns(col) for col in table_forme.columns]
    #table_forme.columns = columns
    #columns_to_merge = [col for col in table_forme.columns if ('NaN' in col or 'Info' in col)]

    ##### START : Table voie d'administration
    table_voie = get_tab_colon(all_tables, 
                               ["Voie d'administration 1"],
                               ['voie_administration_1'])

    ##### START : Table chemical 1
    list_fluticason = ['3400926648794', '3400926648855']
    if all([cip not in file for cip in list_fluticason]):
        table_chemical_1 = get_tab(all_tables, 
                                   ["Substance Active", "CAS"],
                                   ['substance_active_inutile', 'cas'])
    else:
        table_chemical_1 =  pd.DataFrame(index = [0], 
                                         columns = ['Substance Active', 'CAS'])
        table_chemical_1.iloc[0,:] = ['FLUTICASONE PROPIONATE', 'Â']
    ##### START : Table chemical 2
    table_chemical_active = get_tab(all_tables, 
                                    ["Substance Active", "Dosage", "Dosage Base"],
                                    ['substance_active', 'dosage', 'dosage_base'])
    table_chemical_active['active'] = True
    
    ##### START : Table chemical 4
    #### ATTENTION : il peut y en avoir plusieurs
    table_chemical_aux = get_tab(all_tables, 
                                 ["Substance Auxiliaire", "Dosage", "Nature", "Classe chimique", "Voie"],
                                 ['substance_aux', 'dosage', 'nature', 'classe_chimique', 'voie', 'vecteur'],
                                 len_assert = False)
#    table_chemical_aux['active'] = False    
    
    #### START : Values 
#    _list = ["Classe ATC de la Substance Active"]
#    classe_atc = get_val(all_fonts, ["Classe ATC de la Substance Active"])[0]
    for font in all_fonts: 
        if 'Classe ATC :' in font.text:
            break
#            print font.text
    code_ATC = font.next_sibling.next_sibling.text    
    
    #### START : Statut de remboursement
    table_rembourement = str(get_tab(all_tables, ['Statut de remboursement']))
    
    #### START : table posologie
    table_posologie = str(get_tab(all_tables, ["Seuil d'alerte"]))
    
    #### START :  SMR
    smr = get_tab(all_tables, ['Service m', 'dical rendu'])
    
    ligne = pd.tools.merge.concat([table_presentation, table_infos, table_voie, smr,
                                   table_forme, table_chemical_1], axis = 1)
    ligne['statut_remboursement'] = table_rembourement
    ligne['seuils_alerte'] = table_posologie
    
    ligne['classe_atc'] = code_ATC


    
    tab = pd.tools.merge.concat([table_chemical_active, table_chemical_aux])
    tab.index = range(len(tab))

    for col in ligne.columns:
        tab[col] = ligne[col].iloc[0]
        
    return tab
    
  
if __name__ == '__main__':
    list_cip = os.listdir(path_BDM_scrap + '/cip')
    table = None
    i = 0
    problem = []
        
    ## Probleme 
    with open (path_BDM_scrap + 'problem.txt', "r") as myfile:
        problems = myfile.read().split(';')

    for file in problems:
        i += 1
        if i % 100 == 0: 
            print 'on en a fait', i
        file_name = os.path.join(path_BDM_scrap + '/cip', file)
        tab = parse(file_name)
        if table is None: 
            table = tab
        else:
            table = table.append(tab)    
    

   
