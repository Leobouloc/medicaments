# -*- coding: utf-8 -*-
"""
Created on Fri Aug 08 15:30:38 2014

@author: tvialette
"""
import pandas as pd
import re
import os
from CONFIG import path_BDM

info_dispo = ['CIP', 'CIP7', 'CIP_UCD', 'NATURE', 'NOM_COURT', 'INDIC_COND',
              'DEBUT_REMB', 'FIN_REMB', 'CODE_LISTE', 'CODE_FORME', 'FORME',
              'CODE_CPLT', 'CPLT_FORME', 'DOSAGE_SA', 'UNITE_SA', 'NB_UNITES',
              'CODE_ATC', 'CLASSE_ATC', 'CODE_EPH', 'CLASSE_EPH', 'LABO',
              'NOM_LONG1', 'NOM_LONG2', 'SUIVI', 'DATE_EFFET', 'SEUIL_ALER',
              'SEUIL_REJE', 'PRESC_REST', 'EXCEPTIONS', 'TYPE', 'SEXE',
              'INTERACT', 'PIH', 'PECP']


def get_dose(obj):
    ''' permet d'extraire le nombre d'unités des cellules où il y a un slash,
    exemple : pour [1/10 ML] renvoie [1] '''
    obj = str(obj)
    if '/' in obj:
        idx = obj.index('/')
        value = obj[:idx]
    else:
        value = obj
    try:
        return float(value)
    except ValueError:
        return None
        
def recode_dosage_sa(table):
    print('dosage ' + str(len(table)))
    #Supprimer le texte en particulier
    #table = table.loc[table['DOSAGE_SA'].apply(lambda x: x!='NON RENSEIGNE' and x!='NON RENSIGNE' and x!='NON RE' and x!='NR')] 
    #Supprimer toutes les listes avec du texte    
    table = table.loc[table['DOSAGE_SA'].apply(lambda x: str(x).isdigit())]
    table = table.loc[~table['DOSAGE_SA'].isnull(), :]
    table['DOSAGE_SA'] = table['DOSAGE_SA'].str.replace(',','.')
    table['DOSAGE_SA'] = table['DOSAGE_SA'].apply(lambda x: float(x))
    return table            
                
def recode_nb_unites(table):
    #print('nb_unites ' + str(len(table)))
    ''' recode les objets avec des slashs : 2/150 ---> 2''' 
    table = table.loc[~table['NB_UNITES'].isnull(), :]
    table['NB_UNITES'] = table['NB_UNITES'].str.replace(',','.')
    table['NB_UNITES'] = table['NB_UNITES'].str.replace(' M','000000')
    table['NB_UNITES'] = table['NB_UNITES'].str.split('/').apply(lambda x: recode_nb_unites_split_func(x))
    table['NB_UNITES'] = table['NB_UNITES'].apply(lambda x: re.findall('\d*\.?\d+',str(x))[0])
    table['NB_UNITES'] = table['NB_UNITES'].apply(lambda x: float(x))
    return table

def recode_nb_unites_split_func(x):
    print x
    assert(len(x)<=2)
    assert(len(x)>0)
    if len(x)==2:
        #Si lettre G est après le slash, on multiplie par la valeur avant le 'G'
        if len(re.findall('G', x[1])):  
            val = re.findall('\d*\.?\d+',str(x[1]))[0]
            return (float(x[0])*float(val))
        else:
            return (x[0])
    else:
        return (x[0])            
            
def recode_labo(table):
    print('labo ' + str(len(table)))
    table['LABO'] = table['LABO'].str.replace('-','')
    table['LABO'] = table['LABO'].str.replace(' ','')
    return table
    
#def recode_unites(table):
#    table = table[~table['UNITE_SA'].isnull()]
#    #On met les miligrammes en grammes
#    table.loc[table['UNITE_SA'].str.contains('MG'),'DOSAGE_SA']*=1000
    
#def recode_microgrammes_en_mg

def bdm_cnamts(info_utiles, unites_par_boite=True):
    ''' charge les info_utiles et crée la variable unites_par_boite '''
    path = os.path.join(path_BDM, "BDM_CIP.xlsx")
    table_entiere = pd.read_excel(path)
    table = table_entiere.loc[:, info_utiles]
    if 'DOSAGE_SA' in info_utiles:
        table = recode_dosage_sa(table)    
    if 'NB_UNITES' in info_utiles:
        table = recode_nb_unites(table)
    if 'LABO' in info_utiles:
        table = recode_labo(table)
    if unites_par_boite:
        table['unites_par_boite'] = table_entiere['NB_UNITES'].str.replace(',', '.')
        table['unites_par_boite'] = table['unites_par_boite'].apply(get_dose)
    return table


if __name__ == '__main__':
    info_utiles_from_cnamts = ['CIP', 'CIP7', 'FORME', 'NB_UNITES', 'DOSAGE_SA', 'UNITE_SA','LABO']
    test = bdm_cnamts(info_utiles_from_cnamts)
